# =============================================================================
#          File: get_coin_data.py
#        Author: Andre Brener
#       Created: 08 May 2017
# Last Modified: 02 Jul 2017
#   Description: description
# =============================================================================
import json
import time

import requests
import pandas as pd

from constants import COIN_DATA_DAYS, COIN_DATA_DF


def get_current_prices(coin_list, currency='BTC'):

    coin_list_string = ','.join(coin_list)
    price_now_url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'.format(
        coin_list_string, currency)

    response_text = requests.get(price_now_url).text
    d = json.loads(response_text)

    coin_prices = [[coin, val[currency]] for coin, val in d.items()]

    return coin_prices


def get_df_from_api(url):
    response_text = requests.get(url).text
    d = json.loads(response_text)
    df = pd.DataFrame(d['Data'])
    return df


def get_price_history(coin_list, end_date, currency='BTC'):
    ts = time.mktime(end_date.timetuple())
    df_list = []
    btc_url = 'https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&toTs={}&limit={}'.format(
        ts, COIN_DATA_DAYS)
    btc_df = get_df_from_api(btc_url)
    btc_df['coin'] = 'BTC'
    df_list.append(btc_df)
    for l in coin_list:
        url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&toTs={}&limit={}'.format(
            l, currency, ts, COIN_DATA_DAYS)
        df = get_df_from_api(url)
        if df.empty:
            continue
        df = df[['time', 'close']]
        df['coin'] = l
        df_list.append(df)
    total_df = pd.concat(df_list)
    total_df = total_df.pivot(
        index='time', columns='coin', values='close').reset_index()
    total_df['date'] = pd.to_datetime(total_df['time'], unit='s')

    cols = [col for col in total_df.columns if col not in ['time', 'coin']]
    total_df = total_df[cols]
    total_df['date'] = pd.to_datetime(total_df['date'])
    return total_df


def get_graph(df, coin_name, day_interval, dates=True):
    import matplotlib.dates as mdates

    from matplotlib import pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a'))
    if dates:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=day_interval))
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price', fontsize=14)
    plt.title('{} Price History'.format(coin_name))
    y = df[coin_name]
    plt.plot(df['date'], y)


def plot_graphs(df, day_interval, dates=True):
    cols = [col for col in df.columns if col not in ['time', 'date']]
    for coin_name in cols:
        get_graph(df, coin_name, day_interval)


if __name__ == '__main__':
    from datetime import date, timedelta

    coin_list = list(COIN_DATA_DF['coin'].unique())

    end_date = date.today() - timedelta(1)

    df = get_price_history(coin_list, end_date)

    df.to_csv('historical_data.csv', index=False)
