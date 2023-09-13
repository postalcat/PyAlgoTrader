import yfinance as yf
import pandas as pd
from datetime import timedelta
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

RATIO = 0.8

def predict_linearreg(STOCK_SYMBOL, START_DATE, END_DATE, N_DAYS):
    """
    Predicts the future stock prices using linear regression.

    Parameters:
    - STOCK_SYMBOL (str): The symbol of the stock to predict.
    - START_DATE (str): The start date of the historical data to consider.
    - END_DATE (str): The end date of the historical data to consider.
    - N_DAYS (int): The number of days to predict the future stock prices for.

    Returns:
    None
    """
    data = yf.download(STOCK_SYMBOL, start=START_DATE, end=END_DATE)
    df = data[['Close']]
    df.loc[:, 'Next Close'] = df['Close'].shift(-1).values
    df = df[:-1]
    X = df[['Close']]
    y = df['Next Close']
    split_index = int(RATIO * len(df))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    # Give names to the features (columns) for X_train and X_test
    X_train.columns = ['Close']
    X_test.columns = ['Close']

    model = LinearRegression()
    model.fit(X_train.values, y_train.values)  # Use .values to work with raw data

    last_close_price = df['Close'].iloc[-1]
    future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, N_DAYS + 1)]
    future_prices = []
    for _ in range(N_DAYS):
        future_close_price = model.predict([[last_close_price]])[0]
        future_prices.append(future_close_price)
        last_close_price = future_close_price
    future_df = pd.DataFrame({'Date': future_dates, 'Predicted Price': future_prices})
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Historical Close Prices')
    plt.plot(future_df['Date'], future_df['Predicted Price'], label='Predicted Prices', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title(f'{STOCK_SYMBOL} Linear Regression Prediction for Next {N_DAYS} Days')
    plt.legend()
    plt.grid(True)
    plt.show()
