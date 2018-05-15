# Crypto Predictor

Crypto Predictor is an application that generates financial recommendations for cryptocurrencies using Machine Learning models to predict cryptocurrency prices.

This prediction does not take BTC into account, and the price of the other coins is measured in BTC. This is done to avoid BTC price volatility.

By running the code, the application will automatically extract, predict and send email with the final recommendations. See example:

![img](http://i.imgur.com/oRPiRW9.png)

## Getting Started

### 1. Clone Repo

`git clone https://github.com/andrebrener/crypto_predictor.git`

### 2. Install Packages Required

Go in the directory of the repo and run:
```pip install -r requirements.txt```

### 3. Insert Constants
In [constants.py](https://github.com/andrebrener/crypto_predictor/blob/master/constants.py) you can define:
- `BTC_GRADIENT_DAYS`: The number of days from today that will consider the change in btc price. This is a feature for the model.
- The parameters for each of the technical analysis used for features of the model.
- The parameters for the trial and error to finally pick the best model.
- `MAX_BTC_BUY`: The maximum amount of btc to buy an altcoin.
- `MIN_EARNINGS`: Minimum earning percentage for the prediction to enter in the recommendations.
- `PRICE_PERIODS`: Period of time that the model will predict the price.
- `COIN_DATA_DAYS`: Days of past data to collect. This number will also depend on the coin age too.
- `FEE_PERC`: Percentage of fee for a transaction.
- `TOP_COINS`: Number of coins ordered by market cap to analyze. The coins in your own portfolio will also be analyzed.
- `MAIL_NAME`: Name of the user that will receive the recommendation email.
- `MAIL_ADDRESS`: Email address of the user that will receive the mail. This can be a list of many email addresses.
- `MAIL_SENDER`: Email name & address that you like to put to the sender.
- `MAIL_SUBJECT`: Email subject.
- `MAIL_SIGNATURE`: Email name signature.
- `MAIL_RESPONSE_ADDRESS`: Email to receive doubts or suggestions.

### 4. Insert Google Data
You will need credentials for google drive, gmail and google trends. For this you have to:
- Create a file in the repo called `google_credentials.py` where you name the variables `GOOGLE_PASS` and `GOOGLE_USERNAME`. In this file you will also have to define:
  - `SPREADSHEET_LINK`: Link of the google spreadsheet that you have your portfolio.
  - `RANGE_NAME`: Name of the tab and range where your portfolio is in the spreadsheet.
- Generate credentials for [Google Spreadsheet](https://console.developers.google.com/flows/enableapi?apiid=sheets.googleapis.com&pli=1) and save the file called `client_secret.json` in the repo directory.
- Enable gmail access to non secure apps. For more info read this [tutorial](https://support.google.com/cloudidentity/answer/6260879?hl=en)

### 5. Get Recommendations
- Run [get_market_cap.py](https://github.com/andrebrener/crypto_predictor/blob/master/get_market_cap.py) to get the historical weekly market caps.
- To see if the model works, first run [backtest.py](https://github.com/andrebrener/crypto_predictor/blob/master/backtest.py) and check if the recommendations would have been successful in the past.
- Run [main.py](https://github.com/andrebrener/crypto_predictor/blob/master/main.py).
- When the script finishes, if there are recommendations you will receive an email to the address defined in constants. There will be no email if there are no recommendations. You can check the script log in the console or in the log file created.

## Disclaimer

This application was created for informational purposes only and is not a sure-fire profit machine. I am in no way responsable for what the application recommends, so please use it at your own risk.

The Crypto market is very volatile and still in development, meaning that both the market and the application may fail at any time.
