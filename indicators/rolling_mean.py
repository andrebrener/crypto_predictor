# =============================================================================
#          File: rolling_mean.py
#        Author: Andre Brener
#       Created: 03 Jun 2017
# Last Modified: 07 Jun 2017
#   Description: description
# =============================================================================
import pandas as pd


def get_signal(df):
    if df['average_difference'] > 0 and df['prev_diff'] < 0:
        return 1
    elif df['average_difference'] < 0 and df['prev_diff'] > 0:
        return -1
    else:
        return 0


def get_rolling_mean(df, fast_window, slow_window, macd=False):

    df['fast_average'] = df['price'].ewm(span=fast_window).mean()
    df['slow_average'] = df['price'].ewm(span=slow_window).mean()

    col_name = 'average_difference'
    if macd:
        col_name = 'roll_mean_diff'

    df[col_name] = df['fast_average'] - df['slow_average']

    return df


def get_roll_mean_decision(df, roll_mean_params):

    fast_window, slow_window = roll_mean_params

    rm_df = get_rolling_mean(df, fast_window, slow_window)

    rm_df['prev_diff'] = rm_df['average_difference'].shift(1)

    rm_df['signal'] = rm_df.apply(get_signal, axis=1)

    return rm_df


def get_macd_decision(df, macd_params):

    fast_window, slow_window, comparison_window = macd_params

    macd_df = get_rolling_mean(df, fast_window, slow_window, macd=True)

    macd_df['comparison_average'] = macd_df['price'].ewm(
        span=comparison_window).mean()

    macd_df['average_difference'] = macd_df['comparison_average'] - macd_df[
        'roll_mean_diff']

    macd_df['prev_diff'] = macd_df['average_difference'].shift(1)

    macd_df['signal'] = macd_df.apply(get_signal, axis=1)

    return macd_df


if __name__ == '__main__':
    df = pd.read_csv('test_series.csv')
    df = df[['date', 'ETH']]

    fast_window = 12
    slow_window = 29
    comparison_window = 9

    roll_mean_params = (fast_window, slow_window)
    rm_df = get_roll_mean_decision(df, roll_mean_params)

    macd_params = (fast_window, slow_window, comparison_window)
    macd_df = get_macd_decision(df, macd_params)

    print(macd_df)
