# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 21:30:12 2023

@author: 76782
"""
import pandas as pd
import os
from EventUtils import gen_daily_returns

os.chdir('E:\\PROJECT_AI_N_CONFERENCE_CALL')

# Import stock returns
stock_returns = pd.read_csv('./Auxiliaries/DATA_Wind_SP1500_DailyReturns.csv')
stock_returns.set_index('date', inplace=True)
stock_returns.columns = [col.split('.')[0] for col in stock_returns.columns]

# Import market index time series and calculate market returns
market = pd.read_excel('./Auxiliaries/DATA_Yahoo_SP1500_TS.xlsx')
market['date'] = market['date'].astype(str).str.split().str[0]
market.sort_values(by=['date'], inplace=True)
market.set_index('date', inplace=True)

market_close = market['close']
market_returns = gen_daily_returns(market_close)

# -----------------------------
# Test EventStudy module
from EventStudy import EventStudy
stock_data = stock_returns
market_data = market_close

period = list(stock_returns.index)
launch_chatgpt = period.index('2022-11-30')
est_period = (period[481-1-255],  period[481-1])

evt = EventStudy(
    stock_data=stock_data,
    market_data=market_data,
    est_period=est_period,
    )

car = evt.gen_car('AAPL', '2023-02-28')

test = stock_returns['AAPL']

# works well
# ------------------------------
## Get confcall records after 2022.11.30
import pandas as pd
import os
os.chdir('E:\\PROJECT_AI_N_CONFERENCE_CALL')

confcall = pd.read_csv('./2021-2023_ALL_CONFCALL_PANEL.csv')
confcall['date'] = pd.to_datetime(confcall['date'])
launch_date = pd.to_datetime('2022-11-30')

confcall = confcall[confcall['date'] > launch_date]
confcall = confcall[['gvkey', 'sic', 'tic', 'date']]
confcall['date'] = confcall['date'].dt.strftime('%Y-%m-%d')
confcall.drop_duplicates(subset=['gvkey', 'date'], inplace=True)
confcall.sort_values(by=['gvkey','date'], inplace=True)

confcall.to_csv('./DATA_EventDate.csv', index=False)

## Calculate CAR
from EventStudy import EventStudy

# Import stock returns
stock_returns = pd.read_csv('./Auxiliaries/DATA_Wind_SP1500_DailyReturns.csv')
stock_returns.set_index('date', inplace=True)
stock_returns.columns = [col.split('.')[0] for col in stock_returns.columns]

# Import market index time series and calculate market returns
market = pd.read_excel('./Auxiliaries/DATA_Yahoo_SP1500_TS.xlsx')
market['date'] = market['date'].astype(str).str.split().str[0]
market.sort_values(by=['date'], inplace=True)
market.set_index('date', inplace=True)

market_close = market['close']

# Initialise EventStudy instance
stock_data = stock_returns
market_data = market_close

period = list(stock_returns.index)
est_period = (period[481-1-255],  period[481-1])
evt_panel_dir = './DATA_EventDate.csv'
s
evt = EventStudy(
    evt_panel_dir=evt_panel_dir,
    stock_data=stock_data,
    market_data=market_data,
    est_period=est_period,
    )

# test = evt.gen_tic_car_df('AAPL')
car_df = evt.run()
car_df.to_csv('DATA_CAR.csv', index=False)
wf_df = pd.read_csv('PANEL_CEO_AIWordFreq.csv')
wf_df.drop(columns=['title', 'quarter', 'fiscal_year', 'fiscal_quarter', 'month', 'week', 'cik', 'cleaned_dir'], inplace=True)
wf_df.sort_values(by=['gvkey','date'], inplace=True)

wf_df = wf_df[['gvkey', 'date', 'tic', 'sic', 'MD_num_words', 'MD_num_dict', 'QA_num_words', 'QA_num_dict']]
car_df = car_df[['gvkey', 'date', 'car']]

panel = pd.merge(
    wf_df,
    car_df,
    on=['gvkey', 'date'],
    )
for var in ['num_words', 'num_dict']:
    panel[f'total_{var}'] = panel[f'MD_{var}'] + panel[f'QA_{var}']
    
panel['ai_word_dummy'] = 0
panel.loc[panel['total_num_dict'] > 0, 'ai_word_dummy'] = 1
panel['sic2'] = panel['sic'].astype(str).str[:2]
panel.to_csv('PANEL_EventStudy.csv', index=False)
panel['ai_word_dummy'].sum()
