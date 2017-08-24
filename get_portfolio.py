# =============================================================================
#          File: gsheets.py
#        Author: Andre Brener
#       Created: 19 May 2017
# Last Modified: 14 Jun 2017
#   Description: description
# =============================================================================
from __future__ import print_function

import os
import logging
import logging.config

import httplib2
import pandas as pd

from config import config, PROJECT_DIR
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

os.chdir(PROJECT_DIR)

logger = logging.getLogger('main_logger')

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(
        credential_dir, 'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def read_data(service, spreadsheet_id, range_name):

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()

    values = result.get('values', [])

    if not values:
        return None

    return values


def get_id_from_link(link):
    spreadsheet_id = link.split('/')[5]
    return spreadsheet_id


def get_positions(spreadsheet_link, range_name):
    spreadsheet_id = get_id_from_link(spreadsheet_link)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build(
        'sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    values = read_data(service, spreadsheet_id, range_name)
    logger.info("Got values from Sheet")

    if not values:
        return None

    coin_dict = {}
    for coin, val in values:
        coin_dict[coin] = [val]

    coin_df = pd.DataFrame(coin_dict).T.reset_index()
    coin_df.columns = ['coin', 'coin_position']
    coin_df['coin_position'] = coin_df['coin_position'].astype(float)
    btc_position = coin_df[coin_df['coin'] == 'BTC']['coin_position'].iloc[0]
    coin_df = coin_df[coin_df['coin'] != 'BTC']

    return coin_df, float(btc_position)


if __name__ == '__main__':
    logging.config.dictConfig(config['logger'])
    
    from google_credentials import POSITION_SHEET_LINK, RANGE_NAME

    df, btc_position = get_positions(POSITION_SHEET_LINK, RANGE_NAME)

    print(df.dtypes)

    print(type(btc_position))
