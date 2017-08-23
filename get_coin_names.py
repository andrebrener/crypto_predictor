# =============================================================================
#          File: get_coin_names.py
#        Author: Andre Brener
#       Created: 17 Jun 2017
# Last Modified: 17 Jun 2017
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

    coin_logos = [
        tag['src'] for tag in soup.find_all("img", {"class": "currency-logo"})
    ]

    names_df = pd.DataFrame()
    names_df['coin'] = coin_symbols
    names_df['coin_name'] = coin_names
    names_df['coin_name'] = names_df['coin_name'].str.lower()
    names_df['coin_logo'] = coin_logos

    return names_df


if __name__ == '__main__':

    names_url = 'https://coinmarketcap.com/all/views/all/'
    print(get_names(names_url))
