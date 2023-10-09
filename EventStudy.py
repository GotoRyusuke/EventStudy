# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy import stats
import EventUtils
import warnings
from datetime import timedelta
warnings.filterwarnings('ignore')

class EventStudy:
    def __init__(
            self,
            evt_panel_dir,
            stock_data,
            market_data,
            est_period,
            evt_window=1,
            gen_returns=False,
            ):
        self.stock_data = stock_data
        self.market_data = market_data
        self.full_period = list(stock_data.index)
        self.evt_panel = pd.read_csv(evt_panel_dir)
        
        # preparation for estimation
        self.est_start, self.est_end = est_period
        
        # preparation for event
        self.evt_window = evt_window

        if gen_returns:
            self.actual_returns = EventUtils.gen_daily_returns(self.stock_data)
        else:
            self.actual_returns = stock_data
        self.market_returns = EventUtils.gen_daily_returns(self.market_data)
    
    def gen_car(self, tic, evt_date):
        stock_returns = self.actual_returns[tic]
        market_returns = self.market_returns

        if evt_date not in self.full_period:
            while evt_date not in self.full_period:
                evt_date = pd.to_datetime(evt_date) + timedelta(days=1)
                evt_date = evt_date.strftime('%Y-%m-%d')
        
        evt_start = self.full_period[
            self.full_period.index(evt_date) - self.evt_window
            ]
        evt_end = self.full_period[
            self.full_period.index(evt_date) + self.evt_window
            ]
        
        # get expected returns
        beta, intercept = EventUtils.apply_market_model(
            stock_returns,
            market_returns,
            est_start=self.est_start,
            est_end=self.est_end,
            )
        
        # get AR
        evt_stock_returns = EventUtils.gen_period_data(stock_returns, evt_start, evt_end)
        # print(f'event stock returns: {evt_stock_returns}')
        evt_market_returns = EventUtils.gen_period_data(market_returns, evt_start, evt_end)
        # print(f'event market returns: {evt_market_returns}')

        expected_returns = np.array(evt_market_returns) * beta + intercept
        abnormal_returns = evt_stock_returns - np.array(expected_returns)
        # print(f'abnormal returns: {abnormal_returns}')
        
        return abnormal_returns.cumsum()[-1]
    
    def gen_tic_car_df(self, tic):
        tic_df = self.evt_panel[self.evt_panel['tic'] == tic]
        evt_date_list = tic_df['date'].to_list()
        tic_df.set_index('date', inplace=True)
        
        for evt_date in evt_date_list:
            tic_df.loc[evt_date, 'car'] = self.gen_car(tic, evt_date)
        
        return tic_df.reset_index()
    
    def run(self):
        tic_list = list(self.evt_panel['tic'].unique())
        tic_list = [tic for tic in tic_list if tic in self.stock_data.columns]
        tic_car_df_list = []
        
        for tic in tqdm(tic_list):
            tic_car_df = self.gen_tic_car_df(tic)
            tic_car_df_list.append(tic_car_df)
        
        return pd.concat(tic_car_df_list)
        
            
    
    
        
        
        
        
        
        