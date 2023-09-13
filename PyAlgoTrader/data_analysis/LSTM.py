import yfinance as yf
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import matplotlib.pyplot as plt



RATIO = 0.8 #changing this value will affect the train/test ratio, and therefore the accuracy.
# too high or low will affect accuracy, 0.8 is considered balanced.

def predict_lstm(STOCK_SYMBOL, START_DATE, END_DATE, N_DAYS):
    """
    The main function of this file : Predicts future stock prices of a chosen security using 
    the machine learning model LSTM (Long Short-Term Memory).

    Args:
        STOCK_SYMBOL (str): The symbol of the stock.
        START_DATE (str): The start date of the historical data.
        END_DATE (str): The end date of the historical data.
        N_DAYS (int): The number of days to predict the future stock prices for.

    Returns:
        dataframe of predicted stock prices + automatically plot with matplot lib .show().
    """
    data = yf.download(STOCK_SYMBOL, start=START_DATE, end=END_DATE)
    df = data[['Close']]
    scaler = MinMaxScaler()
    df.loc[:, 'Close'] = scaler.fit_transform(df[['Close']])
    def create_sequences(data, sequence_length):
        sequences = []
        targets = []
        for i in range(len(data) - sequence_length):
            sequences.append(data[i:i+sequence_length])
            targets.append(data[i+sequence_length])
        return np.array(sequences), np.array(targets)
    sequence_length = 60
    train_size = int(len(df) * RATIO)
    train_data = df.iloc[:train_size]
    test_data = df.iloc[train_size:]
    train_sequences, train_targets = create_sequences(train_data.values, sequence_length)
    test_sequences, test_targets = create_sequences(test_data.values, sequence_length)
    model = Sequential()
    model.add(LSTM(50, input_shape=(sequence_length, 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(train_sequences, train_targets, epochs=10, batch_size=64, verbose=2)
    test_predictions = model.predict(test_sequences)
    test_predictions = scaler.inverse_transform(test_predictions)
    test_data = scaler.inverse_transform(test_data)

    #calculate RMSE (Root Mean Squared Error) - the lower the better  the stock is, generally
    rmse = np.sqrt(np.mean((test_data[sequence_length:] - test_predictions) ** 2))
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    last_data_point = df.values[-sequence_length:].reshape(1, sequence_length, 1)
    future_predictions = []
    for _ in range(N_DAYS):
        future_price = model.predict(last_data_point)
        future_predictions.append(future_price[0, 0])
        last_data_point = np.roll(last_data_point, shift=-1, axis=1)
        last_data_point[0, -1, 0] = future_price[0, 0]
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    last_date = data.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, N_DAYS + 1)]
    future_df = pd.DataFrame({'Date': future_dates, 'Predicted Price': future_predictions.ravel()})
    #plotting
    plt.figure(figsize=(12, 6))
    plt.plot(data.index[-len(test_data):], test_data, label='True Prices')
    plt.plot(data.index[-len(test_data):][sequence_length:], test_predictions, label='Predicted Prices', linestyle='--')
    plt.plot(future_df['Date'], future_df['Predicted Price'], label=f'Future Predictions ({N_DAYS} Days)', linestyle=':', color='red')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title(f'{STOCK_SYMBOL} Stock Price Prediction')
    plt.legend()
    plt.show()
