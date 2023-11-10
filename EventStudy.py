# -*- coding: utf-8 -*-
'''
Description
------------
A class to conduct event study. Specifically, it can generate CARs for each event, 
which in this case is the earnings conference calls.

Structure
---------
- <CLASS> EventStudy
    - <METHOD> __init__
    - <METHOD> gen_car
        Method to generate CAR for a given event for a given stock
    - <METHOD> gen_tic_car_df
        Method to generate CARs for a given stock for all events
    - <METHOD> run
        Method to generate CARs for all stocks for all events

'''
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
            data_dir,
            est_period=(None, None),
            evt_window=3,
            rolling=True,
            rolling_window=(-65, -2),
            gen_returns=False,
            ):
        self.data = pd.read_excel(data_dir)
        self.full_period = self.data['date'].to_list()
        self.evt_panel = pd.read_csv(evt_panel_dir)
        self.rolling = rolling
        
        # preparation for estimation
        # if est_period is not None, then use est_period as estimation period
        # else use the rolling estimation period
        if est_period == (None, None):
            if rolling:
                self.est_start, self.est_end = rolling_window
            else:
                raise ValueError('est_period is None and rolling is False')
        else:
            self.est_start, self.est_end = est_period
        
        # preparation for event
        self.evt_window = evt_window

        # preparation for returns
        # if gen_returns is True, then generate returns from stock_data and market_data
        if gen_returns:
            self.returns = EventUtils.gen_daily_returns(self.data)
        else:
            self.returns = self.data.set_index('date')
    
    def gen_car(self, tic, evt_date):
        stock_returns = self.returns[tic]
        market_returns = self.returns['market']

        if evt_date not in self.full_period:
            while evt_date not in self.full_period:
                evt_date = pd.to_datetime(evt_date) + timedelta(days=1)
                evt_date = evt_date.strftime('%Y-%m-%d')
        
        evt_start = self.full_period[
            self.full_period.index(evt_date) - int((self.evt_window -1) / 2)
            ]
        evt_end = self.full_period[
            self.full_period.index(evt_date) + int((self.evt_window -1) / 2) 
            ]
            
        # print(evt_start)
        # print(evt_end)
        
        # get expected returns
        #      Estimation (63 days)  Event (window days)
        # |-----------------------|----|---------|
        # est_start         est_end  evt_start evt_end
        if self.rolling:
            est_start = self.full_period[
                self.full_period.index(evt_date) + self.est_start + 1
            ]
            est_end = self.full_period[
                self.full_period.index(evt_date) + self.est_end
            ]
        else:
            est_start = self.est_start
            est_end = self.est_end
        # print(est_start)
        # print(est_end)

        beta, intercept = EventUtils.apply_market_model(
            stock_returns,
            market_returns,
            est_start=est_start,
            est_end=est_end,
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
        tic_list = [tic for tic in tic_list if tic in self.data.columns if tic != 'market']
        tic_car_df_list = []
        
        for tic in tqdm(tic_list):
            tic_car_df = self.gen_tic_car_df(tic)
            tic_car_df_list.append(tic_car_df)
        
        return pd.concat(tic_car_df_list)
        
            
    
    
        
        
        
        
        
        