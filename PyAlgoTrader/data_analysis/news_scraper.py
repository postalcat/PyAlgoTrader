import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import ssl
import io  # Import io module

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Set up scraper
url = "https://finviz.com/news.ashx"
req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
webpage = urlopen(req).read()
html = soup(webpage, "html.parser")

# Define function to scrape and process headlines
def scrape_headlines(html, idx):
    """
    Scrapes headlines from a given HTML and returns a specific index of news.

    Parameters:
        html (str): The HTML content to scrape headlines from.
        idx (int): The index of the news to return.

    Returns:
        pandas.DataFrame or None: The scraped news as a DataFrame if successful, None otherwise.
    """
    try:
        # Wrap the HTML in a StringIO object
        html_str = str(html)
        html_io = io.StringIO(html_str)
        
        news = pd.read_html(html_io)[idx]
        news.columns = ["0", "Time", "Headlines"]
        news = news.drop(columns=["0"])
        return news
    except Exception as e:
        print(f"Error: {e}")
        return None


def find_headlines(*searchparameters):
    """
    Finds headlines that match the given search parameters and returns them as a single string.
    
    Args:
        *searchparameters: Variable number of search parameters to filter the headlines.
        
    Returns:
        str: A string containing the headlines that match the search parameters. If no headlines are found, 
        it returns "No headlines found.". If an error occurs while scraping headlines, it returns 
        "Error occurred while scraping headlines.".
    """
    search_query = ' '.join(searchparameters)  # Combine search parameters into a single string
    headlines_df = scrape_headlines(html, 5)
    if headlines_df is not None:
        headlines = []
        for _, row in headlines_df.iterrows():
            if search_query in row['Headlines']:
                headline = f"{row['Time']} - {row['Headlines']}"
                headlines.append(headline)
        if headlines:
            headlines_text = "\n".join(headlines)
        else:
            headlines_text = "No headlines found."
    else:
        headlines_text = "Error occurred while scraping headlines."
    return headlines_text