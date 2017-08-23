# =============================================================================
#          File: get_fees.py
#        Author: Andre Brener
#       Created: 12 Jun 2017
# Last Modified: 12 Jun 2017
#   Description: description
# =============================================================================
import requests
import pandas as pd

from bs4 import BeautifulSoup


def get_fee_number(fee_string):
    fee_list = [s for s in fee_string.split()]
    return float(fee_list[-2])


def get_fee_df(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    tag_texts = [
        tag.text.strip() for tag in soup.find_all("td")
        if len(tag.text.strip()) > 0
    ]

    coins = tag_texts[0::2]
    fees = tag_texts[1::2]

    df = pd.DataFrame()
    df['coin'] = coins
    df['coin_fee'] = fees

    df['coin_fee'] = df['coin_fee'].apply(get_fee_number)

    return df


if __name__ == '__main__':

    url = 'http://info.shapeshift.io/about'
    print(get_fee_df(url))
