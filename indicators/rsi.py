# =============================================================================
#          File: rsi.py
#        Author: Andre Brener
#       Created: 03 Jun 2017
# Last Modified: 07 Jun 2017
#   Description: description
# =============================================================================
import pandas as pd


def get_upward_movement(df):
    if df['price'] > df['price_diff']:
        return df['price'] - df['price_diff']
    else:
        return 0


def get_downward_movement(df):
    if df['price'] < df['price_diff']:
        return df['price_diff'] - df['price']
    else:
        return 0


def get_rsi(df, window_size):

    df['price_diff'] = df['price'].shift(1)

    df['upward_movement'] = df.apply(get_upward_movement, axis=1)

    df['downward_movement'] = df.apply(get_downward_movement, axis=1)

    df['average_upward'] = df['upward_movement'].rolling(
        window=window_size).mean()
    df['average_downward'] = df['downward_movement'].rolling(
        window=window_size).mean()

    df['rs'] = df['average_upward'] / df['average_downward']

    df['rsi'] = 100 - (100 / (1 + df['rs']))

    return df


def get_signal(n):
    if n > 85:
        return -1
    elif n < 15:
        return 1
    else:
        return 0


def get_rsi_decision(df, rsi_params):

    window_size = rsi_params

    rsi_df = get_rsi(df, window_size)

    rsi_df['signal'] = rsi_df['rsi'].apply(get_signal)

    return rsi_df


if __name__ == '__main__':
    df = pd.read_csv('test_series.csv')
    df = df[['date', 'ETH']]

    window_size = 14

    rsi_params = (window_size)

    rsi_df = get_rsi_decision(df, rsi_params)

    print(rsi_df)
