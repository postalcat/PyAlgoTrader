# stock_utils.py
import yfinance as yf
import tkinter as tk
import pandas as pd


def load_stocks_from_csv():
    """
    Load stocks from a CSV file.

    This function reads a CSV file named 'STOCK_LIST.csv' located in the 'PyAlgoTrader/utils_misc' directory.
    It retrieves the list of stocks from the 'Stocks' column in the CSV file and returns it.

    Returns:
        list: A list of stocks read from the CSV file.

    Raises:
        FileNotFoundError: If the CSV file 'STOCK_LIST.csv' is not found, an empty list is returned.

    """
    try:
        stocks_df = pd.read_csv('PyAlgoTrader/utils_misc/STOCK_LIST.csv')
        stocks = stocks_df['Stocks'].tolist()
        return stocks
    except FileNotFoundError:
        return []


def save_stocks_to_csv(stocks):
    """
    Saves the given list of stocks to a CSV file.

    Parameters:
        stocks (list): A list of stock names.

    Returns:
        None
    """
    stocks_df = pd.DataFrame({'Stocks': stocks})
    stocks_df.to_csv('PyAlgoTrader/utils_misc/STOCK_LIST.csv', index=False)

def update_stock_info(stocks_listbox, stocks):
    """
    Updates the stock information in the stocks_listbox.

    Parameters:
        stocks_listbox (tk.Listbox): The listbox where the stock information will be displayed.
        stocks (list): A list of stock symbols.

    Returns:
        None
    """
    for stock in stocks:
        ticker = yf.Ticker(stock)
        if ticker.info: #if ticker has information
            stock_info = f"{stock} - {ticker.history(period='1d')['Close'].iloc[-1]:.2f} USD"
            stocks_listbox.insert(tk.END, stock_info)

def add_stock(current_ticker, stocks_listbox, stocks):
    """
    Add a stock to the stock list.

    Parameters:
    - current_ticker (str): The ticker symbol of the stock to be added.
    - stocks_listbox (Listbox): The GUI listbox widget displaying the stocks.
    - stocks (List[str]): The list of stocks.

    Returns:
    None
    """
    ticker = current_ticker.get()
    stocks.append(ticker)
    save_stocks_to_csv(stocks)
    update_stock_info(stocks_listbox, [ticker])

def remove_stock(lb_curselection,stocks_listbox, stocks):
    """
    Remove a stock from the stocks listbox and the stocks list.

    Parameters:
    - lb_curselection (tuple): The index of the selected item in the stocks listbox.
    - stocks_listbox (Listbox): The listbox widget containing the stocks.
    - stocks (list): The list of stocks.

    Returns:
    None
    """
    stocks_listbox.delete(lb_curselection)
    stocks.remove(stocks[lb_curselection[0]])
    save_stocks_to_csv(stocks)
