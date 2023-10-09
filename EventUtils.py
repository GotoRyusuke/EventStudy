# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from scipy import stats

# df = pd.read_csv('C:\\Users\\76782\\Desktop\\DATA_SP1500_close.csv')
# df.set_index('index', inplace=True)

def gen_daily_returns(data, base=1):
    '''
    Description
    ------------
    A function to calculate daily returns from a given data
    
    Args
    ----
        data: a numpy array, a pandas series or a pandas dataframe
        base: the base of the returns, default is 1
    Returns
    -------
        A numpy array, a pandas series or a pandas dataframe of daily returns
    '''
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

def apply_market_model(
        stock_returns, 
        market_returns,
        est_start,
        est_end,
        ):
    '''
    Description
    ------------
    A function to apply market model to a given stock and market returns

    Args
    ----
        stock_returns: a numpy array, a pandas series or a pandas dataframe
        market_returns: a numpy array, a pandas series or a pandas dataframe
        est_start: str
            the start date of the estimation period
        est_end: str
            the end date of the estimation period
    
    Returns
    -------
        beta: float
            the estimated beta
        intercept: float
            the estimated intercept
    '''
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
    '''
    Description
    ------------
    A function to generate a period of data from a given data

    Args
    ----
        data: a numpy array, a pandas series or a pandas dataframe
        start_date: str
            the start date of the period
        end_date: str
            the end date of the period
    
    Returns
    -------
        A numpy array, a pandas series or a pandas dataframe of the period data
    '''
    if type(data) is pd.DataFrame:
        data = data['close']
    dates = list(data.index)
    start_idx = dates.index(start_date)
    end_idx = dates.index(end_date)
    
    return data[start_idx:end_idx+1]
# test = gen_period_data(returns['AAPL.O'], '2022-01-03', '2023-01-06')
