# =============================================================================
#          File: mails.py
#        Author: Andre Brener
#       Created: 13 Jun 2017
# Last Modified: 18 Jun 2017
#   Description: description
# =============================================================================
import os
import logging
import smtplib

from time import sleep
from datetime import date
from email.utils import COMMASPACE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import pandas as pd

from config import PROJECT_DIR
from constants import COIN_NAMES_DF
from google_credentials import GOOGLE_PASS, GOOGLE_USERNAME

logger = logging.getLogger('main_logger.' + __name__)


class User:

    def __init__(self, name, email, templates):
        self.name = name
        self.email = email
        self.coins = []
        self.user_template = templates['mail_body.html']

    def render(self):
        return self.user_template.render(
            name=get_only_name(self.name), coins=self.coins)


class Coin:

    def __init__(self, name, logo, action_type, action_currency, action_amount,
                 pred_earnings, templates):
        self.name = name
        self.action_type = action_type
        self.logo = logo
        self.pred_earnings = int(100 * pred_earnings)
        self.action_currency = action_currency
        self.action_amount = round(-1 * action_amount, 3)
        self.coin_template = templates['coin_template.html']

    def render(self):
        return self.coin_template.render(
            name=self.name,
            action_type=self.action_type,
            logo=self.logo,
            pred_earnings=self.pred_earnings,
            action_currency=self.action_currency,
            action_amount=self.action_amount)


def get_only_name(full_name):
    name_list = full_name.split()
    return name_list[0]


def get_action_type(coin_data):
    if coin_data < 0:
        return 'Sell'
    else:
        return 'Buy'


def get_currency(df):
    if df['pred_price_change'] < 0:
        return df['coin']
    else:
        return 'BTC'


def get_action_amount(df):
    if df['pred_price_change'] < 0:
        return df['coin_action']
    else:
        return df['btc_action']


def prepare_mail(user, templates):
    mail_to = user.email
    mail_subject = 'Cryptocurrency Recommendations - {}'.format(date.today())
    mail_body = user.render()
    return mail_to, mail_subject, mail_body


def send_mail(current_dir, send_to, subject, mail_body, files=None):

    try:
        user_address, password = GOOGLE_USERNAME, GOOGLE_PASS
    except (FileNotFoundError):
        user_address = os.environ.get('SES_ACCESS_KEY_ID', None)
        password = os.environ.get('SES_SECRET_ACCESS_KEY', None)

    from_address = 'Andre Finance <crypto@andre.com>'
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = COMMASPACE.join(send_to)
    msg['Subject'] = subject
    msg.attach(MIMEText(mail_body.encode('utf-8'), 'html', 'utf-8'))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=os.path.basename(f))
            part['Content-Disposition'] = \
                'attachment; filename="%s"' % os.path.basename(f)
            msg.attach(part)

    tries = 1
    while tries < 30:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(user_address, password)
                server.sendmail(from_address, send_to, msg.as_string())
                logger.info("Email sent :)")
                break
        except Exception as e:
            logger.error("Mail failed. ERROR: {}".format(e))
            tries += 1
            sleep(70 * tries)


def get_object_list(cls, df, main_col, columns, templates):
    return [
        cls(i, * [j[col] for col in columns], templates)
        for i in df[main_col].unique()
        for j in [df[df[main_col] == i][columns].iloc[0]]
    ]


def send_recommendations_mail(df, templates):

    current_dir = os.path.dirname(os.path.realpath(__file__))
    df['action_type'] = df['coin_action'].apply(get_action_type)
    df['action_currency'] = df.apply(get_currency, axis=1)
    df['action_amount'] = df.apply(get_action_amount, axis=1)
    df['user'] = 'Andre Brener'
    df['usr_email'] = 'brener.andre@gmail.com'

    df = pd.merge(df, COIN_NAMES_DF)

    usrs = get_object_list(User, df, 'user', ['usr_email'], templates)

    for usr in usrs:
        usr_df = df[df['user'] == usr.name]
        coins = get_object_list(Coin, usr_df, 'coin', [
            'coin_logo', 'action_type', 'action_currency', 'action_amount',
            'pred_earnings'
        ], templates)

        usr.coins = coins

    for usr in usrs:
        mail_to, mail_subject, mail_body = prepare_mail(usr, templates)

        # with open('html_example.html', 'w') as f:
        # f.write(mail_body)

        send_mail(current_dir, [mail_to], mail_subject, mail_body)


if __name__ == '__main__':
    from jinja_customs import load_templates

    templates_dir = PROJECT_DIR + '/mail_templates'

    templates = load_templates(templates_dir)

    df = pd.read_csv('recommendation_test.csv')

    send_recommendations_mail(df, templates)
