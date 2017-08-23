# =============================================================================
#          File: get_fees.py
#        Author: Andre Brener
#       Created: 12 Jun 2017
# Last Modified: 18 Jun 2017
#   Description: description
# =============================================================================
import os

import requests
import pandas as pd

from bs4 import BeautifulSoup


def get_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    lists = soup.find_all("li", {"class": "text-center"})

    links = []
    for li in lists:
        a_tags = li.find_all("a")
        href = a_tags[0]['href']
        day_link = href.split('/')[-2]
        links.append('{}{}'.format(url, day_link))

    return links


def get_market_value(week_date, url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    coin_symbols = [
        tag.text.strip() for tag in soup.find_all("td", {"class": "text-left"})
        if len(tag.text.strip()) > 0
    ]

    market_caps = [
        tag.text.strip()[1:].replace(',', '')
        for tag in soup.find_all("td",
                                 {"class": "no-wrap market-cap text-right"})
        if len(tag.text.strip()) > 0
    ]

    df = pd.DataFrame()

    df['coin'] = coin_symbols
    df['market_cap'] = market_caps
    df['market_cap'] = df['market_cap'].apply(
        lambda x: int(x) if x != '' else 0)

    df['date'] = week_date
    df['date'] = pd.to_datetime(df['date'])

    return df


def get_data(main_url, current_df):
    links = get_links(main_url)

    df_list = []
    for url in links:
        week_date = url.split('/')[-1]
        # if week_date in list(current_df['date'].dt.strftime('%Y%m%d')):
        # continue
        print(url)
        df = get_market_value(week_date, url)
        df_list.append(df)

    if len(df_list) == 0:
        result_df = current_df

    else:
        total_df = pd.concat(df_list)
        total_df = total_df.pivot_table(
            index='date', columns='coin', values='market_cap',
            aggfunc='max').reset_index()

        total_df['week_number'] = total_df['date'].dt.week
        total_df['year'] = total_df['date'].dt.year

        total_dates = list(total_df['date'])

        new_df = pd.DataFrame()
        new_df['date'] = pd.date_range(total_dates[0], total_dates[-1])
        new_df['week_number'] = new_df['date'].dt.week
        new_df['year'] = new_df['date'].dt.year

        cols = [col for col in total_df.columns if 'date' not in col]

        final_df = pd.merge(
            total_df[cols], new_df,
            on=['week_number', 'year']).sort_values('date')

        final_cols = [
            col for col in total_df.columns
            if all(kw not in col for kw in ['week_number', 'year'])
        ]

        final_df = final_df[final_cols].fillna(0)

        if current_df.empty:
            result_df = final_df
        else:
            result_df = pd.concat([current_df, final_df])

    coin_list = [col for col in result_df.columns if 'date' not in col]

    btc_market_caps = pd.DataFrame()
    btc_market_caps['date'] = result_df['date']

    for col in coin_list:
        btc_market_caps[col] = result_df[col] / result_df['BTC']

    return result_df, btc_market_caps


if __name__ == '__main__':
    historical_url = 'https://coinmarketcap.com/historical/'

    # current_df = pd.read_csv('data/historical_market_caps.csv')

    # current_df['date'] = pd.to_datetime(current_df['date'])
    current_df = pd.DataFrame()
    df, btc_df = get_data(historical_url, current_df)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/historical_market_caps.csv', index=False)
    btc_df.to_csv('data/historical_market_caps_btc.csv', index=False)
