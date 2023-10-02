import pandas as pd 
import yfinance as yf
import math
import numpy as np ##(https://numpy.org/doc/stable/user/absolute_beginners.html)
import matplotlib as mlp 
import matplotlib.pyplot as plt
import seaborn as sns

#List of stocks/etfs to be used 
tickers_list = ['CRM', 'NVDA', 'ADBE', 'GS', 'PG', 'SMCI', 'NEE']
tickers_list.sort()
etf = ['SPY','IWM','DIA']

#Different type of data pulls for Table 1
data = yf.download(tickers_list, period='10y')#General All data
ACdata = yf.download(tickers_list, period = '3mo')['Adj Close'] #Adjusted Close 3 month trail
etf_ticker_data = yf.download(tickers_list + etf, period='1y')['Adj Close'] #Adjusted Close 12 month trail including ETFs
Datahigh = yf.download(tickers_list, period='1y')['High']
Datalow = yf.download(tickers_list, period='1y')['Low']

##Portfolio Weight
Adj_Closing_Prices= data['Adj Close'].iloc[-1]
total_ACP = Adj_Closing_Prices.sum()

portfolio_weight = []

for Prices in Adj_Closing_Prices:
    portfolio_weight_raw = (Prices/total_ACP)*100
    portfolio_weight.append(round(portfolio_weight_raw,2))


n = len(tickers_list)
weight = 1/n


#Annualized Volatility 

returns = ACdata.pct_change().dropna() 
volatility_raw = returns.std()*(np.sqrt(252))*100 
annualized_volatility = round(volatility_raw,2)

#Function to use for each ETF to compare to Beta(Tickers/stocks)
def against_etf(etf_symbol):
    beta_values = []

    for ticker in tickers_list:
        # Extract daily returns for the current stock and ETF
        stock_returns = etf_ticker_data[ticker].pct_change().dropna()
        etf_returns = etf_ticker_data[etf_symbol].pct_change().dropna()

        # Calculate covariance and variance
        cov_matrix = np.cov(stock_returns, etf_returns, ddof=0)
        stock_etf_cov = cov_matrix[0, 1]
        etf_variance = np.var(etf_returns, ddof=0)

        # Calculate beta
        beta = round((stock_etf_cov / etf_variance),2)

        beta_values.append(beta)

    return beta_values
    

# Calculate beta for each ETF
Beta_SPY = against_etf('SPY')
Beta_IWM = against_etf('IWM')
Beta_DIA = against_etf('DIA')


#Average Weekly Drop Down 
avg_weekly_dd = []

for ticker in tickers_list:
    highsum = Datahigh[ticker].sum()
    lowsum = Datalow[ticker].sum()
    
    high = highsum/52
    low = lowsum/52

    awdcalc = ((low - high)/high)*100
    avg_weekly_dd.append(round(awdcalc , 2))

#Same code differnt data function (note .max and .min)/ Maximum Weekly Drawdown 
max_weekly_dd = []
for ticker in tickers_list:
    highsummax = Datahigh[ticker].max()
    lowsummin = Datalow[ticker].min()
    
    highmax = highsummax/52
    lowmin = lowsummin/52

    awdcalchm = ((lowmin - highmax)/highmax)*100 
    max_weekly_dd.append(round(awdcalchm, 2))

#Total Return 
Total_Return = []
for ticker in tickers_list:
    datatr = yf.download(ticker, period='10y')  
    beginning_value = datatr['Adj Close'].iloc[0]
    ending_value = datatr['Adj Close'].iloc[-1]

    return_value = ((ending_value - beginning_value)/beginning_value)*100
    Total_Return.append(round(return_value,2))
    
Annualized_Return = []
for i in Total_Return:
   AR = (i/10)*100
   Annualized_Return.append(round(AR,2))


#Creating a table 
Table1 = {'Ticker' : tickers_list ,
          'Portfolio Weight' : portfolio_weight, 
          'Portfolio Weight Equally Weighted':weight,
          'Annualized Volatility': annualized_volatility,
          'Beta against SPY' : Beta_SPY,
          'Beta against IWM': Beta_IWM ,
          'Beta against DIA': Beta_DIA, 
          'Average Weekly Drawdown':avg_weekly_dd,
          'Maximum Weekly Drawdown': max_weekly_dd,
          'Total Return': Total_Return,
          'Annualized Total Return': Annualized_Return}

df1 = pd.DataFrame(Table1)

##print(df1['Portfolio Weight Equally Weighted'])


# Table 2 
# Table 2 
# Data Pulls
Data10y = yf.download(tickers_list + etf, period='10y')['Adj Close']
returns_df = Data10y.pct_change().dropna()
portfolio_returns = returns_df[tickers_list].sum(axis=1)

#Data pull for Sharpe Ratio
Data1y = yf.download(tickers_list + etf, period='1y')['Adj Close']
returns_df1y = Data1y.pct_change().dropna()
portfolio_returns1y = returns_df1y[tickers_list].sum(axis=1)
etf_returns1y = returns_df1y[etf].sum(axis=1)

# Correlation Against ETF
##(https://www.investopedia.com/terms/c/correlation.asp)
correlation_etf = []

for i in etf:
    correlation = portfolio_returns.corr(returns_df[i])
    correlation_etf.append(round(correlation, 2))


##(https://www.geeksforgeeks.org/python-numpy-cov-function/)
##(https://www.investopedia.com/ask/answers/041315/how-covariance-used-portfolio-theory.asp)
# Covariance Against ETF
Covariance_etf =[]

for i in etf:
    covariance = portfolio_returns.cov(returns_df[i])
    Covariance_etf.append(round(covariance, 6))


#tracking error (https://www.investopedia.com/terms/t/trackingerror.asp#:~:text=Given%20a%20sequence%20of%20returns,and%20B%20is%20benchmark%20return.)
tracking_error = []
for i in etf:
    trackingerr = portfolio_returns - returns_df[i] 
    trackingerrstd = trackingerr.std()*100
    tracking_error.append(round(trackingerrstd,2))

sharpe_ratio = []
# Portfolio return, risk-free rate, and excess return
risk_free_rate = 0.0459

for i in etf:
    excess_return = portfolio_returns1y - risk_free_rate
    std_dev_excess_return = excess_return.std()
    sharpe_ratio_calc = excess_return.mean() / std_dev_excess_return
    sharpe_ratio.append(sharpe_ratio_calc)
Annualized_Volatility_etf = []

for i in etf:
    etf_returns = returns_df[i]
    etf_volatility_raw = etf_returns.std() * np.sqrt(252) * 100
    etf_annualized_volatility = round(etf_volatility_raw, 2)
    Annualized_Volatility_etf.append(etf_annualized_volatility)

# Calculate the annualized volatility spread
Annualized_Volatility_spread = []

for i in range(len(etf)):
    annualized_volatility_b = annualized_volatility.std()
    spread = annualized_volatility_b - Annualized_Volatility_etf[i]
    Annualized_Volatility_spread.append(round(spread, 2))

#Correlation Matrix(https://www.geeksforgeeks.org/create-a-correlation-matrix-using-python/)

dataplot = sns.heatmap(returns_df, annot=True, cmap='vlag')



Table2 ={'Tickers': etf,
         'Correlation against etf':correlation_etf,
         'Covariance against etf': Covariance_etf,
         'Tracking Error' : tracking_error,
         'Sharpe Ratio' : sharpe_ratio,
         'Annualized Volatility Spread': Annualized_Volatility_spread,
         }

df2=pd.DataFrame(Table2)

print(df2)
plt.show()



#(https://www.geeksforgeeks.org/plotting-correlation-matrix-using-python/)
