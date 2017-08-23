# =============================================================================
#          File: bollinger_bands.py
#        Author: Andre Brener
#       Created: 03 Jun 2017
# Last Modified: 07 Jun 2017
#   Description: description
# =============================================================================
import pandas as pd


def bollinger_bands(price_series, window_size, std_devs):

    rolling_mean = price_series.rolling(window=window_size).mean()
    rolling_std = price_series.rolling(window=window_size).std()

    upper_band = rolling_mean + (rolling_std * std_devs)
    lower_band = rolling_mean - (rolling_std * std_devs)

    return rolling_mean, upper_band, lower_band


def upper_positive_to_negative(df):
    if df['upper_bol_difference'] > 0 and df['prev_upper_bol_difference'] < 0:
        return -1
    else:
        return 0


def lower_positive_to_negative(df):
    if df['lower_bol_difference'] > 0 and df['prev_lower_bol_difference'] < 0:
        return 1
    else:
        return 0


def get_bollinger_decision(df, bollinger_params):

    df.columns = ['date', 'price']

    window_size, std_devs = bollinger_params

    df['average'], df['upper'], df['lower'] = bollinger_bands(
        df['price'], window_size, std_devs)

    df['upper_bol_difference'] = df['price'] - df['upper']
    df['lower_bol_difference'] = df['lower'] - df['price']

    df['prev_lower_bol_difference'] = df['lower_bol_difference'].shift(1)
    df['prev_upper_bol_difference'] = df['upper_bol_difference'].shift(1)

    df['bol_buy'] = df.apply(lower_positive_to_negative, axis=1)
    df['bol_sell'] = df.apply(upper_positive_to_negative, axis=1)

    df['signal'] = df['bol_buy'] + df['bol_sell']

    return df


if __name__ == '__main__':
    df = pd.read_csv('test_series.csv')
    df = df[['date', 'ETH']]

    window_size = 4
    std_devs = 2

    bollinger_params = [window_size, std_devs]

    bb_df = get_bollinger_decision(df, bollinger_params)

    print(bb_df)
