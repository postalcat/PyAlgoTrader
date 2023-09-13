
#TODO: FINISH FORMATTING CODE+ DOCSTRINGS
#TODO: ADD TTK INSTEAD OF TK WIDGETS
#TODO: allow graphing/predictions to take all stock exchanges( only takes S&P 500 tickers atms)
#// SAVE TO CSV FIX(done)
import datetime as dt
import yfinance as yf
import tkinter as tk
import ttkbootstrap as ttk
import talib as ta
import matplotlib.pyplot as plt
from data_analysis.news_scraper import find_headlines
from data_analysis.LSTM import predict_lstm
from data_analysis.linearreg import predict_linearreg
from utils_misc.definitions import definitions1 as defs1,definitions2 as defs2
from utils_misc.stock_utils import load_stocks_from_csv, add_stock, remove_stock,update_stock_info

yf.pdr_override()
END_PERIOD = dt.datetime.now() # for graphs
START_PERIOD = dt.datetime.now() - dt.timedelta(days=995)
#!REMINDER: THE REASON THAT LSTM ONLY DISPLAYS X AMOUNT OF MONTHS IS BECAUSE OF THE 20% RULE.
#IT ONLY DISPLAYS TESTING DATA. e.g, 900 days = 180 days of testing, therefore 6 months shown.
#439 is the lowest number of days it can be set to, as the predicted prices line(orange one) grows so small 
#that the values cannot compute and iterate further in order to generate the red line(the future prediction)
class MAINGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyAlgoTrader")
        self.resizable(False, False)
        self.theme = ttk.Style(theme="superhero")
        self.notebook = ttk.Notebook(self, height=550, width=500)
        self.notebook.grid(column=0, row=0, padx=10, pady=10)
        self.current_ticker = tk.StringVar(value="AAPL")
        self.current_chart_type = tk.StringVar(value="Close Price")
        df = yf.download(self.current_ticker.get(), START_PERIOD, END_PERIOD)
        self.chart_types = {#! adding or removing charts here allows for new chart types to be added/removed as long as talib supports
            "Volume": df['Volume'],
            "Close Price": df['Close'],
            "MACD": ta.MACD(df['Close'])[0],  
            "RSI": ta.RSI(df['Close']),
            "Stochastic": ta.STOCH(df['High'], df['Low'], df['Close'])[0],  
            "SMA": ta.SMA(df['Close'], timeperiod=20),  
        }
        # calling setup methods for each page+ loading stocks saved in csv file.
        self.stocks = load_stocks_from_csv() #going into stock_list.csv and reducing number of stocks to load will speed up lkoading time of the gui
        self.setup_main_page()
        self.setup_graph_page()
        self.setup_news_scraper_page()
        self.setup_predictions_page()
    def setup_graph_page(self):
        """
        Shows a graph based on the current ticker and chart type selected by the user.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception: If there is an error when retrieving or plotting the graph.
        """
        def show_graph():
            """
            Shows a graph based on the current ticker and chart type selected by the user.

            Parameters:
                None

            Returns:
                None

            Raises:
                Exception: If there is an error when retrieving or plotting the graph.
            """
            try:
                ticker = self.current_ticker.get()
                full_ticker = ticker  # by default, assume no extension
                df = yf.download(full_ticker, START_PERIOD, END_PERIOD)
                chart_type = self.current_chart_type.get()
                fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
                ax.plot(df.index, self.chart_types[chart_type], label=chart_type, color='b')
                ax.set_xlabel('Date')
                ax.set_ylabel(chart_type)
                ax.set_title(f'{ticker} {chart_type}')
                ax.legend()
                ax.grid(True)
                plt.show()
            except Exception as e:
                error_message = f"Invalid ticker(if you're seeing this you probably used .AX, which yfinance doesnt support)"
                #display the error message to the user, e.g., in a messagebox or label
                tk.messagebox.showerror("Error", error_message)

        self.stock_page = ttk.Frame(self.notebook)
        self.notebook.add(self.stock_page, text="Stock Graphing")
        ttk.Label(self.stock_page, text="Enter a stock ticker:").pack(pady=10)
        self.ticker_entry = ttk.Entry(self.stock_page, textvariable=self.current_ticker)
        self.ticker_entry.pack()
        ttk.Label(self.stock_page, text="Select Chart Type:").pack(pady=10)
        self.chart_type_menu = ttk.OptionMenu(self.stock_page, self.current_chart_type, "")
        self.chart_type_menu.pack()
        self.chart_type_menu["menu"].delete(0, "end")
        for chart_type in self.chart_types.keys():
            self.chart_type_menu["menu"].add_command(label=chart_type, command=lambda value=chart_type: self.current_chart_type.set(value))
        ttk.Button(self.stock_page, text="Show Graph", command=show_graph).pack(pady=10)
        for key,value in defs2.items():
            ttk.Label(self.stock_page, text=f"{key}: {value}",wraplength=400).pack(pady=10)
    def setup_main_page(self):
        """
        Sets up the main page of the application.

        This function creates and configures the main page of the application. It adds a frame to the notebook widget, sets the text for the tab representing the main page, and configures the layout of the main page.

        Parameters:
            self (object): The instance of the class.
        
        Return:
            None
        """
        self.main_page = ttk.Frame(self.notebook)
        self.notebook.add(self.main_page, text="Main Page")
        ttk.Label(self.main_page, text="Python Stock Analysis GUI",font="Helvetica 30 bold").grid(row=0, column=0,columnspan=2, pady=20)
        self.stocks_listbox = tk.Listbox(self.main_page)
        for stock in self.stocks:
            update_stock_info(self.stocks_listbox, [stock])
        self.stocks_listbox.grid(row=1, column=0, padx=10, pady=10)
        self.new_stock_entry = ttk.Entry(self.main_page, textvariable=self.current_ticker)
        self.new_stock_entry.grid(row=2, column=0, padx=10, pady=10)
        #use lambda functions to directly call functions from stock_utils
        add_stock_button = ttk.Button(self.main_page, text="Add Stock", command=lambda: add_stock(self.current_ticker, self.stocks_listbox, self.stocks))
        remove_stock_button = ttk.Button(self.main_page, text="Remove Stock", command=lambda: remove_stock(self.stocks_listbox.curselection(), self.stocks_listbox, self.stocks))
        add_stock_button.grid(row=3, column=0, padx=10, pady=10,ipadx=11)
        remove_stock_button.grid(row=4, column=0, padx=10, pady=10)
        description = "Thanks for using my stock analysis platform. " \
                        "This platform was created for educational purposes, please don't take any of these predictions seriously. " \
                        "On the left is a stock viewing device. Enter the stock ticker and you can get the current price in USD of the security."
        description_label = ttk.Label(self.main_page, text=description, wraplength=200)
        description_label.grid(row=1, column=1, padx=10, pady=20)
    def setup_news_scraper_page(self):
        """
        Sets up the news scraper page.

        This function sets up the news scraper page by creating a new frame within the notebook and adding it to the notebook. It also adds a label and an entry field for the user to input search parameters for the news website. Finally, it creates a submit button that calls the `generate_news` function when clicked.

        Parameters:
            self: The current instance of the class.

        Returns:
            None
        """
        def generate_news():
            """
            Generate the news by finding headlines based on the scraper parameters entry.

            :return: None
            """
            values = find_headlines(self.scraper_params_entry.get())
            newlevel = tk.Toplevel(self.news_page)
            newlevel.title("News Scraper Results")
            print(values)
            tk.Label(newlevel, text="Scraped Headlines- see finviz.com/news.ashx for links",font="Helvetica 20 bold").pack()
            tk.Label(newlevel, text=values,wraplength=300).pack()
        self.news_page = ttk.Frame(self.notebook)
        self.notebook.add(self.news_page, text="News Scraper")
        ttk.Label(self.news_page, text="News scraper tool",font="Helvetica 20 bold").pack()
        ttk.Label(self.news_page,text="Enter parameter to search news website for").pack()
        self.scraper_params_entry = ttk.Entry(self.news_page)
        self.scraper_params_entry.pack()
        submit_params_button = ttk.Button(self.news_page, text="Submit", command=generate_news)
        submit_params_button.pack()
        ttk.Label(self.news_page,text = "You could input 'Stock' or 'Apple' to test it out").pack(pady=30)
    def setup_predictions_page(self):
        """
        Sets up the predictions page.

        This function creates the GUI elements for the predictions page, including labels,
        entry fields, spinboxes, and buttons. It also defines the behavior of the buttons
        when clicked.

        Parameters:
        - self: The instance of the class.
        
        Returns:
        - None
        """
        def enter_results(model, ticker, n_days):
            """
            Executes the prediction model to generate results for a given ticker and number of days.

            Parameters:
                model (str): The prediction model to use. Can be "LSTM" or any other model.
                ticker (str): The ticker symbol for the stock.
                n_days (int): The number of days to predict.

            Returns:
                None
            """
            if model == "LSTM":
                predict_lstm(ticker,START_PERIOD,END_PERIOD,int(n_days))
            else:
                predict_linearreg(ticker,START_PERIOD,END_PERIOD,int(n_days))
        self.predicts_page = tk.Frame(self.notebook)
        self.notebook.add(self.predicts_page, text="Machine Learning Predictions")
        ttk.Label(self.predicts_page,text="Enter a stock ticker:").grid(column=0, row=0, pady=10)
        self.new_ticker_entry = ttk.Entry(self.predicts_page,width=10)
        self.new_ticker_entry.grid(column=0, row=1, pady=10)
        ttk.Label(self.predicts_page,text="Prediction length(days):").grid(column=0, row=3, pady=10)
        self.days_entry = ttk.Spinbox(self.predicts_page,increment=1,from_=1,to=100,width=5)
        self.days_entry.grid(column=0, row=4, pady=10)
        submit_params_button1 = ttk.Button(self.predicts_page, text="Generate Chart(LSTM)",command=lambda: enter_results("LSTM", self.new_ticker_entry.get(),self.days_entry.get()))
        submit_params_button1.grid(column=2, row=4, pady=20,padx=10)
        submit_params_button2 = ttk.Button(self.predicts_page, text="Generate Chart(Linear Regression)",command=lambda: enter_results("linearreg", self.new_ticker_entry.get(),self.days_entry.get()))
        submit_params_button2.grid(column=2, row=1, pady=20,padx=10)
        tk.Label(self.predicts_page,text = defs1["LSTM"],wraplength=200).grid(column=2, row=5)
        tk.Label(self.predicts_page,text = defs1["Linear Regression"],wraplength=200).grid(column=2, row=2)
        tk.Label(self.predicts_page,text="Please keep in mind that none of these predictions can be verified to be accurate.",wraplength=200).grid(column=0, row=5)


if __name__ == "__main__":
    app = MAINGUI()
    app.mainloop()
