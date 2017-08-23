# =============================================================================
#          File: constants.py
#        Author: Andre Brener
#       Created: 12 Jun 2017
# Last Modified: 22 Aug 2017
#   Description: description
# =============================================================================
import pandas as pd

from get_portfolio import get_positions
from get_coin_names import get_names
from google_credentials import POSITION_SHEET_LINK, RANGE_NAME
from sklearn.linear_model import LinearRegression

BTC_GRADIENT_DAYS = 7
TECHNICAL_ANALYSIS = {
    'bollinger_bands': (20, 2.5),
    'roll_mean_1': (13, 21),
    'roll_mean_2': (21, 55),
    'macd_1': (12, 29, 9),
    'macd_2': (5, 34, 1),
    'rsi_1': (14)
}

LINEAR_PARAMS = {
    'fit_intercept': [True, False],
    'normalize': [True, False],
}

MODELS = {'LinearRegression': (LinearRegression(), LINEAR_PARAMS)}

MAX_BTC_BUY = 0.8
MAX_SELL_PERCENTAGE = 0.3
MIN_EARNINGS = 0.05
PRICE_PERIODS = 7
COIN_DATA_DAYS = 500
FEE_PERC = 0.1
TOP_COINS = 10

COIN_DATA_DF, BTC_AVAILABLE = get_positions(POSITION_SHEET_LINK, RANGE_NAME)

COIN_MK_CAPS = pd.read_csv('data/historical_market_caps_btc.csv')
COIN_MK_CAPS['date'] = pd.to_datetime(COIN_MK_CAPS['date'])

NAMES_URL = 'https://coinmarketcap.com/all/views/all/'
COIN_NAMES_DF = get_names(NAMES_URL)
COIN_NAMES_HEAD = COIN_NAMES_DF.head(TOP_COINS)

COIN_DATA_TEMP = pd.merge(COIN_DATA_DF, COIN_NAMES_DF, how='left').fillna(0)
COIN_DATA_DF = pd.concat([
    COIN_DATA_TEMP, COIN_NAMES_HEAD
]).drop_duplicates().fillna(0).groupby('coin').max().reset_index()

# print(COIN_DATA_DF)
