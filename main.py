# =============================================================================
#          File: main.py
#        Author: Andre Brener
#       Created: 06 Jun 2017
# Last Modified: 18 Jun 2017
#   Description: description
# =============================================================================
import os
import logging
import logging.config

from datetime import date, timedelta

import pandas as pd

from mails import send_recommendations_mail
from model import get_dataset, get_dataset_df, get_model
from config import config, PROJECT_DIR
from constants import (BTC_AVAILABLE, COIN_DATA_DF, FEE_PERC, MAX_BTC_BUY,
                       MAX_SELL_PERCENTAGE, MIN_EARNINGS)
from get_coin_data import get_price_history
from jinja_customs import load_templates

os.chdir(PROJECT_DIR)

logger = logging.getLogger('main_logger')


def get_backtest_action(X, y, model):

    model_name, clf = model

    decision_df = X.copy()

    decision_type = clf.predict(X)

    decision_df['final_decision'] = decision_type

    return decision_df


def get_coin_decisions(df, backtest=True):

    model = get_model(df)

    df_list, backtests = get_dataset_df(df, backtest)

    total_decisions_df = pd.DataFrame()
    total_prices_df = pd.DataFrame()
    for coin, coin_df in backtests.items():
        X, y = get_dataset(coin_df)
        final_df = get_backtest_action(X, y, model)
        for col in ['date', 'price']:
            final_df[col] = coin_df[col]

        coin_decision_df = final_df[['date', 'final_decision']]
        coin_prices_df = final_df[['date', 'price']]
        coin_decision_df.columns = ['date', coin]
        coin_prices_df.columns = ['date', coin]

        if total_decisions_df.empty:
            total_decisions_df = coin_decision_df
        else:
            total_decisions_df = pd.merge(total_decisions_df, coin_decision_df)
        if total_prices_df.empty:
            total_prices_df = coin_prices_df
        else:
            total_prices_df = pd.merge(total_prices_df, coin_prices_df)

    df_list = []
    for df in [total_decisions_df, total_prices_df]:
        df.set_index('date', inplace=True)
        df_list.append(df.T.reset_index())

    return df_list


def get_action_per_coin(pred_price_change, price, coin_position):
    if pred_price_change < 0:
        if coin_position == 0:
            return 0, 0, 0
        coin_action = MAX_SELL_PERCENTAGE * coin_position * pred_price_change
        btc_action = -1 * coin_action * price
        pred_earnings = (btc_action *
                         (1 - FEE_PERC)) / (-1 * coin_action * price *
                                            (1 + pred_price_change)) - 1

    else:
        btc_action = -1 * MAX_BTC_BUY * pred_price_change
        coin_action = -1 * btc_action / price
        pred_earnings = ((coin_action * (1 - FEE_PERC)) * price *
                         (1 + pred_price_change) / (-1 * btc_action)) - 1

    return coin_action, btc_action, pred_earnings


def get_day_decision(day_decision_df, day_price_df):
    day_decision_df.columns = ['coin', 'pred_price_change']
    day_price_df.columns = ['coin', 'price']
    df = pd.merge(day_decision_df, day_price_df)
    df = pd.merge(df, COIN_DATA_DF)

    action_results = df.apply(
        lambda df: get_action_per_coin(df['pred_price_change'], df['price'], df['coin_position']),
        axis=1)
    action_results_df = action_results.apply(pd.Series)
    action_results_df.columns = ['coin_action', 'btc_action', 'pred_earnings']
    action_results_df['coin'] = df['coin']

    df = pd.merge(df, action_results_df)

    df = df[df['pred_earnings'] > MIN_EARNINGS]

    buy_df = df[df['pred_price_change'] > 0].sort_values(
        'pred_earnings', ascending=False)
    sell_df = df[df['pred_price_change'] < 0].sort_values(
        'pred_earnings', ascending=False)

    return buy_df, sell_df


def get_daily_recommendations(starting_position, day_decision_df, day_price_df,
                              btc_available):

    buy_df, sell_df = get_day_decision(day_decision_df, day_price_df)

    btc_available += sell_df['btc_action'].sum()

    buy_df['cumulative_btc'] = buy_df['btc_action'].cumsum()
    buy_df['new_btc_position'] = btc_available + buy_df['cumulative_btc']

    buy_df = buy_df[buy_df['new_btc_position'] > 0]

    new_btc_available = btc_available + buy_df['btc_action'].sum()

    total_df = pd.concat([buy_df, sell_df])

    new_coin_data_df = pd.merge(
        starting_position, total_df[['coin', 'coin_action']],
        how='left').fillna(0)

    new_coin_data_df['coin_position'] = new_coin_data_df[
        'coin_position'] + new_coin_data_df['coin_action']

    new_coin_data_df = new_coin_data_df[['coin', 'coin_position']]

    return total_df, new_coin_data_df, new_btc_available


def main():

    logger.info("Getting Coin Data")
    coin_list = list(COIN_DATA_DF['coin'].unique())
    end_date = date.today() - timedelta(1)
    logger.info("Getting predictions")
    df = get_price_history(coin_list, end_date)
    total_decisions_df, total_prices_df = get_coin_decisions(
        df, backtest=False)
    logger.info("Predictions done")

    day_cols = [
        col for col in total_decisions_df.columns if 'index' not in str(col)
    ]
    day_decision_df = total_decisions_df[['index', day_cols[-1]]]
    day_price_df = total_prices_df[['index', day_cols[-1]]]
    total_df, new_coin_data_df, new_btc_available = get_daily_recommendations(
        COIN_DATA_DF, day_decision_df, day_price_df, BTC_AVAILABLE)

    templates_dir = PROJECT_DIR + '/mail_templates'

    templates = load_templates(templates_dir)

    if not total_df.empty:
        send_recommendations_mail(total_df, templates)
        logger.info("Email Sent :)")
    else:
        logger.info("No Recommendations")


if __name__ == '__main__':
    logging.config.dictConfig(config['logger'])

    # df = pd.read_csv('historical_data.csv')

    # total_decisions_df = pd.read_csv('backtest_decisions.csv')
    # total_prices_df = pd.read_csv('backtest_prices.csv')

    main()
