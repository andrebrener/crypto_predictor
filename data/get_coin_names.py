# =============================================================================
#          File: get_coin_names.py
#        Author: Andre Brener
#       Created: 17 Jun 2017
# Last Modified: 23 Sep 2017
#   Description: description
# =============================================================================
import requests
import pandas as pd

from bs4 import BeautifulSoup


def get_names(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    coin_names = [
        tag.text.strip()
        for tag in soup.find_all("td", {"class": "no-wrap currency-name"})
        if len(tag.text.strip()) > 0
    ]

    coin_symbols = [
        tag.text.strip() for tag in soup.find_all("td", {"class": "text-left"})
        if len(tag.text.strip()) > 0
    ]

    names_df = pd.DataFrame()
    names_df['coin'] = coin_symbols
    names_df['coin_name'] = coin_names
    names_df['coin_name'] = names_df['coin_name'].str.lower()

    return names_df


def get_logos(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    coin_names = [
        tag.text.strip()
        for tag in soup.find_all("span", {"class": "coin-name"})
    ]

    class_name = "coin-list__body__row__cryptocurrency__prepend__icon__img"

    coin_logos = [
        tag['src'] for tag in soup.find_all("img", {"class": class_name})
    ]

    logos_df = pd.DataFrame()
    logos_df['coin_logo'] = coin_logos
    logos_df['coin_name'] = coin_names
    logos_df['coin_name'] = logos_df['coin_name'].str.lower()

    return logos_df


def get_coin_info(names_url, logos_url):
    names_df = get_names(names_url)
    logos_df = get_logos(logos_url)

    final_df = pd.merge(names_df, logos_df, how='left')

    return final_df


if __name__ == '__main__':

    names_url = 'https://coinmarketcap.com/all/views/all/'
    logos_url = 'https://coinranking.com/'

    get_coin_info(names_url, logos_url)
