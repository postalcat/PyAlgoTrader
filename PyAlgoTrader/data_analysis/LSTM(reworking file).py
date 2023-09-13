import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import matplotlib.pyplot as plt

RATIO = 0.8

def predict_lstm(STOCK_SYMBOL, START_DATE, END_DATE, N_DAYS):
    data = yf.download(STOCK_SYMBOL, start=START_DATE, end=END_DATE)
    df = data[['Close']]
    scaler = MinMaxScaler()
    df['Close'] = scaler.fit_transform(df[['Close']])
    
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
    
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, df['Close'], label='True Prices', color='blue')
    plt.plot(future_df['Date'], future_df['Predicted Price'], label=f'Future Predictions ({N_DAYS} Days)', linestyle=':', color='red')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title(f'{STOCK_SYMBOL} Stock Price Prediction')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    STOCK_SYMBOL = 'AAPL'
    START_DATE = '2022-01-01'
    END_DATE = '2023-01-01'
    N_DAYS = 30
    predict_lstm(STOCK_SYMBOL, START_DATE, END_DATE, N_DAYS)
