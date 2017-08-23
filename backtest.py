# =============================================================================
#          File: backtest.py
#        Author: Andre Brener
#       Created: 12 Jun 2017
# Last Modified: 14 Jun 2017
#   Description: description
# =============================================================================
from datetime import date, timedelta

import pandas as pd

from main import get_coin_decisions, get_daily_recommendations
from constants import BTC_AVAILABLE, COIN_DATA_DF, PRICE_PERIODS
from get_coin_data import get_price_history


def get_final_coin_position(total_decisions_df, total_prices_df):
    day_cols = [
        col for col in total_decisions_df.columns if 'index' not in str(col)
    ]

    btc_available = BTC_AVAILABLE
    new_coin_data_df = COIN_DATA_DF
    for col in day_cols:
        day_decision_df = total_decisions_df[['index', col]]
        day_price_df = total_prices_df[['index', col]]

        total_df, new_coin_data_df, btc_available = get_daily_recommendations(
            new_coin_data_df, day_decision_df, day_price_df, btc_available)

    final_position = new_coin_data_df

    final_date = pd.to_datetime(col) + timedelta(PRICE_PERIODS)

    return final_position, final_date, btc_available


def get_earnings(df, total_decisions_df, total_prices_df):

    final_position, final_date, btc_available = get_final_coin_position(
        total_decisions_df, total_prices_df)

    df['date'] = pd.to_datetime(df['date'])

    new_prices = df[df['date'] == final_date].T.reset_index()
    new_prices.columns = ['coin', 'new_price']

    final_df = pd.merge(final_position, new_prices)
    final_df['btc_position'] = final_df['coin_position'] * final_df[
        'new_price']

    btc_invested = final_df['btc_position'].sum()
    final_btc_position = final_df['btc_position'].sum() + btc_available

    print('BTC Start: ', BTC_AVAILABLE)
    print('BTC Invested: ', btc_invested)
    print('BTC END: ', btc_available)
    print('BTC Total: ', final_btc_position)
    print('Earnings: ', (final_btc_position - BTC_AVAILABLE) / BTC_AVAILABLE)


def main_backtest():
    print("Getting Coin Data")
    coin_list = list(COIN_DATA_DF['coin'].unique())
    end_date = date.today() - timedelta(1)
    print("Getting predictions")
    df = get_price_history(coin_list, end_date)
    total_decisions_df, total_prices_df = get_coin_decisions(df)
    print("Predictions done")
    get_earnings(df, total_decisions_df, total_prices_df)


if __name__ == '__main__':
    # df = pd.read_csv('historical_data.csv')
    # total_decisions_df = pd.read_csv('backtest_decisions.csv')
    # total_prices_df = pd.read_csv('backtest_prices.csv')

    # get_earnings(df, total_decisions_df, total_prices_df)

    main_backtest()
