# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy import stats




# df = pd.read_csv('C:\\Users\\76782\\Desktop\\DATA_SP1500_close.csv')
# df.set_index('index', inplace=True)

# calculate daily returns
def gen_daily_returns(data, base=1):
    if type(data) is np.ndarray:
        daily_returns = np.zeros(shape=data.shape)
        daily_returns[base:] = data[base:] / data[0:-base] - 1
        return daily_returns * 100
    if type(data) is pd.Series:
        daily_returns = gen_daily_returns(data.values, base=base)
        name = data.name
        return pd.Series(daily_returns, index=data.index, name=name)
    if type(data) is pd.DataFrame:
        returns = data.apply(gen_daily_returns)
        returns.index=data.index
        return returns

# returns = gen_daily_returns(df)

# calcualte expected returns
def apply_market_model(
        stock_returns, 
        market_returns,
        est_start,
        est_end,
        ):
    
    # prepare data
    stock_returns = gen_period_data(stock_returns, est_start, est_end)
    market_returns = gen_period_data(market_returns, est_start, est_end)
        
    # estimation
    y = np.array(stock_returns)
    x = np.array(market_returns)
    
    beta, intercept, r, p, std = stats.linregress(x, y)
    # print(f'Estimated Beta: {beta}')
    # print(f'Estimated Intercept: {intercept}')
    # print(f'Estimation metrics:\n\tp-value: {p}\n\tStd Error: {std}')
    
    return beta, intercept

def gen_period_data(data, start_date, end_date):
    dates = list(data.index)
    start_idx = dates.index(start_date)
    end_idx = dates.index(end_date)
    
    return data[start_idx:end_idx+1]

# test = gen_period_data(returns['AAPL.O'], '2022-01-03', '2023-01-06')
