import requests
from bs4 import BeautifulSoup

#Create a class structure to handle input
class Stock:
  def __init__(self, ticker, sector):
    self.ticker = ticker
    self.sector = sector
    self.price = 0
    #utilize yf for scraping of data
    self.url = f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics?p={self.ticker}"
    self.data = {}
    #Create alias pairs of data coming in for recognition
    self.metric_aliases = {
            'Market Cap (intraday)': 'market_cap',
            'Beta (5Y Monthly)': 'beta',
            '52 Week High 3': '52_week_high',
            '52 Week Low 3': '52_week_low',
            '50-Day Moving Average 3': '50_day_ma',
            '200-Day Moving Average 3': '200_day_ma',
            'Avg Vol (3 month) 3': 'avg_vol_3m',
            'Avg Vol (10 day) 3': 'avg_vol_10d',
            'Shares Outstanding 5': 'shares_outstanding',
            'Float 8': 'float',
            '% Held by Insiders 1': 'held_by_insiders',
            '% Held by Institutions 1': 'held_by_institutions',
            'Short Ratio (Jan 30, 2023) 4': 'short_ratio',
            'Payout Ratio 4': 'payout_ratio',
            'Profit Margin': 'profit_margin',
            'Operating Margin (ttm)': 'operating_margin',
            'Return on Assets (ttm)': 'return_on_assets',
            'Return on Equity (ttm)': 'return_on_equity',
            'Revenue (ttm)': 'revenue',
            'Revenue Per Share (ttm)': 'revenue_per_share',
            'Gross Profit (ttm)': 'gross_profit',
            'EBITDA ': 'ebitda',
            'Net Income Avi to Common (ttm)': 'net_income',
            'Diluted EPS (ttm)': 'eps',
            'Total Cash (mrq)': 'total_cash',
            'Total Cash Per Share (mrq)': 'cash_per_share',
            'Total Debt (mrq)': 'total_debt',
            'Total Debt/Equity (mrq)': 'debt_to_equity',
            'Current Ratio (mrq)': 'current_ratio',
            'Book Value Per Share (mrq)': 'book_value_per_share',
            'Operating Cash Flow (ttm)': 'operating_cash_flow',
            'Levered Free Cash Flow (ttm)': 'levered_free_cash_flow'
        }
  def scrape_data(self):
    page = requests.get(self.url, headers=get_headers())
    soup = BeautifulSoup(page.content, 'html.parser')

    data = {}

    sections=soup.find_all('section', {'data-test', 'qsp-statistics'})
    for section in sections:
      rows = section.find_all('tr')
      for row in rows:
        cols = row.find_all('td')
        if len(cols) == 2:
          metric = cols[0].text.rstrip()
          if metric in self.metric_aliases:
            data[self.metric_aliases[metric]] = cols[1].text.strip()
    self.data = data

  def get_stock_price(self):
    try:
      url = f'https://finance.yahoo.com/quote/{self.ticker}'
      response = requests.get(url, headers=get_headers())
      soup = BeautifulSoup(response.content, 'html.parser')
      data = soup.find('fin-streamer', {'data-symbol': self.ticker})
      price = float(data['value'])
      self.price = price
    except:
      print(f'Price not available for {self.ticker}')
      self.price = 0.0

#Create the Stocks Screen class component
class StockScreener:
  def __init__(self, stocks, filters):
    self.stocks = stocks
    self.filters = filters

  #Add Data to Stocks
  def add_data(self):
    for stock in self.stocks:
      stock.scrape_data()
      stock.get_stock_price()
  
  #Select stocks that pass all filters
  def apply_filters(self):
    filtered_stocks = []
    for stock in self.stocks:
      passed_all_filters = True
      for filter_func in self.filters:
        if not filter_func(stock):
          passed_all_filters = False
          break
      if passed_all_filters:
        filtered_stocks.append(stock)
    return filtered_stocks

#UTILS Functions for Testing

#Gathers all the headers from the scraped data
def get_headers():
  return {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

#Filter functions based on sector
def filter_sector(stock, sector):
  return stock.sector == sector

#Filter function based on the price
def filter_price(stock, min_price, max_price):
  return min_price <= stock.price <= max_price

#Filter function based on operators
def filter_metric(stock, metric, operator, value):
  if metric not in stock.data:
    return False

  #Convert values based on desired metric
  if 'B' in stock.data[metric]:
    stock.data[metric] = stock.data[metric].replace('B', '')
    value = float(value) / 1e9
  elif 'M' in stock.data[metric]:
    stock.data[metric] = stock.data[metric].replace('M', '')
    value = float(value) / 1e6
  elif '%' in stock.data[metric]:
    stock.data[metric] = stock.data[metric].replace('M', '')
    value = float(value)
  else:
    value = float(value)
  
  #Check condition dependent on operator
  if operator == '>':
      return float(stock.data[metric]) > value
  elif operator == '>=':
      return float(stock.data[metric]) >= value
  elif operator == '<':
      return float(stock.data[metric]) < value
  elif operator == '<=':
      return float(stock.data[metric]) <= value
  elif operator == '==':
      return float(stock.data[metric]) == value
  else:
      return False

#Get sp500 ticker and sector
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html-parser')

table = soup.find('table', {'class': 'wikitable sortable'})
rows = table.find_all('tr')[1:]

sp500 = []

for row in rows:
   cells = row.find_all('td')
   ticker = cells[0].text.rstrip()
   company = cells[1].text.rstrip()
   sector = cells[3].text.rstrip()
   sp500.append({'ticker': ticker, 'company': company, 'sector': sector})

def get_sp500_stocks():
   sp500_stocks = [Stock(stock['ticker'], stock['sector']) for stock in sp500]
   return sp500_stocks




