import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px
import math


st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date,end=end_date)
#st.dataframe(data)
fig= px.line(data, x=data.index, y= data['Adj Close'], title=ticker+" Closure Earnings")
st.plotly_chart(fig)

pricing_data, fundamental_data, news = st.tabs(['Pricing Data', 'Fundamental Data', 'Top 10 News'])

with pricing_data:
  st.subheader('Price Movements')
  data2 = data
  data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
  data2.dropna(inplace=True)
  st.write(data2)
  annual_return = data2['% Change'].mean()*252*100
  annual_return = round(annual_return,2)
  st.write('Annual Return is ', annual_return,'%')
  stdev = (np.std(data2['% Change'])*np.sqrt(252))*100
  stdev_rounded = round(stdev,2)
  st.write('Standard Deviation is ', stdev_rounded, '%')
  st.write('Risk Adjusted Return is ',(annual_return)/(stdev))

from stocknews import StockNews
with news:
  st.subheader('News')
  sn = StockNews(ticker, save_news=False)
  df_news = sn.read_rss()
  for i in range(10):
    st.subheader(f'News {i+1}')
    st.write(df_news['published'][i])
    st.write(df_news['title'][i])
    st.write(df_news['summary'][i])
    title_sentiment = df_news['sentiment_title'][i]
    st.write(f'Title Sentiment {title_sentiment}')
    news_sentiment =df_news['sentiment_summary'][i]
    st.write(f'News Sentiment {news_sentiment}')

from alpha_vantage.fundamentaldata import FundamentalData
with fundamental_data:
  #Gather Alpha Vantage Metrics and Dataframe
  key = '4F40ECA9ZJICKJQX'
  fd = FundamentalData(key, output_format='pandas')
  #Produce Related Balance Sheet Metrics
  st.subheader('Balance Sheet')
  balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
  bs = balance_sheet.T[2:]
  bs.columns = list(balance_sheet.T.iloc[0])
  st.write(bs)
  #Produce Related Income Statement Metrics
  st.subheader('Income Statement')
  income_statement = fd.get_income_statement_annual(ticker)[0]
  is1 = income_statement.T[2:]
  is1.columns = list(income_statement.T.iloc[0])
  st.write(is1)
  st.subheader('Cash Flow Statement')
  cash_flow = fd.get_cash_flow_annual(ticker)[0]
  cf = cash_flow.T[2:]
  cf.columns = list(cash_flow.T.iloc[0])
  st.write(cf)

