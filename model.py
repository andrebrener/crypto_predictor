# =============================================================================
#          File: model.py
#        Author: Andre Brener
#       Created: 07 Jun 2017
# Last Modified: 18 Jun 2017
#   Description: description
# =============================================================================
import pandas as pd

from rsi import get_rsi_decision
from constants import (BTC_GRADIENT_DAYS, COIN_MK_CAPS, COIN_NAMES_DF, MODELS,
                       PRICE_PERIODS, TECHNICAL_ANALYSIS)
from rolling_mean import get_macd_decision, get_roll_mean_decision
from google_trends import get_trend_df
from bollinger_bands import get_bollinger_decision
from google_credentials import GOOGLE_PASS, GOOGLE_USERNAME
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split


def clean_df(df, tech_analysis):
    clean_df = df[['date', 'price', 'signal']]
    col_name = '{}_signal'.format(tech_analysis)
    clean_df.columns = ['date', 'price', col_name]
    clean_df['date'] = pd.to_datetime(clean_df['date'])
    return clean_df


def get_coin_decision(df):
    final_df = pd.DataFrame()
    for key, params in TECHNICAL_ANALYSIS.items():
        if 'bollinger' in key:
            analysis_df = get_bollinger_decision(df, params)
        elif 'roll_mean' in key:
            analysis_df = get_roll_mean_decision(df, params)
        elif 'rsi' in key:
            analysis_df = get_rsi_decision(df, params)
        elif 'macd' in key:
            analysis_df = get_macd_decision(df, params)

        stat_df = clean_df(analysis_df, key)

        if final_df.empty:
            final_df = stat_df
        else:
            final_df = pd.merge(final_df, stat_df)

    return final_df


def get_dataset_df(df, backtest=True):

    btc_price_df = df[['date', 'BTC']]
    btc_price_df['date'] = pd.to_datetime(btc_price_df['date'])
    btc_price_df['btc_rolling_mean'] = btc_price_df['BTC'].ewm(span=10).mean()
    btc_price_df['btc_gradient'] = (
        btc_price_df['btc_rolling_mean'] -
        btc_price_df['btc_rolling_mean'].shift(BTC_GRADIENT_DAYS)
    ) / BTC_GRADIENT_DAYS
    btc_trend = get_trend_df(GOOGLE_USERNAME, GOOGLE_PASS, ['bitcoin'])
    btc_trend.columns = ['date', 'btc_trend']

    btc_price_df = pd.merge(btc_price_df, btc_trend)

    coin_cols = [
        col for col in df.columns if all(w not in col for w in ['date', 'BTC'])
    ]
    df_list = []
    backtests = {}

    for col in coin_cols:
        coin_df = df[['date', col]]
        coin_df = coin_df[coin_df[col] > 0]

        if coin_df.shape[0] < 30:
            continue

        result_coin_df = get_coin_decision(coin_df)

        mk_cap_df = COIN_MK_CAPS[['date', col]]

        mk_cap_df.columns = ['date', 'market_cap']

        result_coin_df = pd.merge(result_coin_df, mk_cap_df)

        result_coin_df = pd.merge(
            result_coin_df, btc_price_df[['date', 'btc_gradient',
                                          'btc_trend']])

        coin_name = COIN_NAMES_DF[COIN_NAMES_DF['coin'] == col][
            'coin_name'].iat[0]
        coin_trend_df = get_trend_df(GOOGLE_USERNAME, GOOGLE_PASS, [coin_name])
        coin_trend_df.columns = ['date', 'coin_trend']

        result_coin_df = pd.merge(result_coin_df, coin_trend_df)

        result_coin_df = result_coin_df.sort_values('date')

        result_coin_df['price_after'] = result_coin_df['price'].shift(
            -PRICE_PERIODS)
        result_coin_df['price_change'] = (
            result_coin_df['price_after'] - result_coin_df['price']
        ) / result_coin_df['price']

        if backtest:
            result_coin_df.dropna(inplace=True)

            if result_coin_df.shape[0] < 15:
                continue

            backtest_columns = 15

        else:
            backtest_columns = 1

        backtest_df = result_coin_df.tail(backtest_columns)
        result_coin_df = result_coin_df.head(result_coin_df.shape[0] -
                                             backtest_columns)

        # backtest_df['target_decision'] = backtest_df['price_change'].apply(
        # rules_definitions)
        backtest_df['target_decision'] = backtest_df['price_change']
        backtests[col] = backtest_df

        result_coin_df['target_decision'] = result_coin_df['price_change']

        df_list.append(result_coin_df)

    return df_list, backtests


def get_dataset(final_df):
    x_cols = [col for col in final_df.columns if 'signal' in col]
    for col in ['btc_trend', 'btc_gradient', 'coin_trend']:
        x_cols.append(col)

    X = final_df[x_cols]
    y = final_df['target_decision']

    return X, y


def get_best_model(model, parameters, X_train, y_train):
    clf = GridSearchCV(model, parameters, cv=4, n_jobs=-1)
    clf.fit(X_train, y_train)
    # print(clf.best_params_)
    return clf.best_estimator_


def get_model(df):

    df_list, backtests = get_dataset_df(df)

    final_df = pd.concat(df_list)

    X, y = get_dataset(final_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0)

    l = []

    for model in MODELS:
        # print('\nTraining Model', model)
        (clf, parameters) = MODELS[model]
        l.append((model, get_best_model(clf, parameters, X_train, y_train)))

    return l[0]


if __name__ == '__main__':

    df = pd.read_csv('example_data/historical_data.csv')

    logistic_params = {
        'C': [0.5, 1.0, 5, 10, 100, 500, 1000],
        'penalty': ['l1', 'l2'],
        'class_weight': ['balanced', None]
    }

    get_model(df)
