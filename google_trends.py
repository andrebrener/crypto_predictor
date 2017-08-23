import pandas as pd

from google_credentials import GOOGLE_PASS, GOOGLE_USERNAME
from pytrends.request import TrendReq


def get_trend_df(usr_name, usr_pass, kw_list, cat=1138):
    pytrend = TrendReq(usr_name, usr_pass)
    pytrend.build_payload(kw_list=kw_list, cat=cat)

    df = pytrend.interest_over_time().reset_index()
    df['week_number'] = df['date'].dt.week
    df['year'] = df['date'].dt.year

    dates = list(df['date'])

    new_df = pd.DataFrame()
    new_df['date'] = pd.date_range(dates[0], dates[-1])
    new_df['week_number'] = new_df['date'].dt.week
    new_df['year'] = new_df['date'].dt.year

    cols = [col for col in df.columns if 'date' not in col]

    final_df = pd.merge(
        df[cols], new_df, on=['week_number', 'year']).sort_values('date')

    final_cols = [
        col for col in df.columns
        if all(kw not in col for kw in ['week_number', 'year'])
    ]

    final_df = final_df[final_cols]

    return final_df


if __name__ == '__main__':

    kw_list = ['bitcoin', 'ethereum', 'btc', 'eth', 'monero']

    df = get_trend_df(GOOGLE_USERNAME, GOOGLE_PASS, kw_list)

    print(df.head())
