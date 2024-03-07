import pandas as pd
import sqlite3
import re
from bs4 import BeautifulSoup


def read_articles_from_db(database_file: str) -> pd.DataFrame:
    """
    Read the articles table from the given SQLite database file 
    and return the data as a pandas DataFrame.

    Args:
        database_file (str): The path to the SQLite database file.

    Returns:
        pd.DataFrame: The DataFrame containing the data from the articles table.
    """
    # Connect to the SQLite database
    with sqlite3.connect(database_file) as con:
        # Execute the SQL query and read the results into a DataFrame
        articles_df = pd.read_sql_query("SELECT * from articles", con)

    return articles_df


def find_companies(html: str) -> str:
    """
    Extracts a list of company names from the given HTML content.

    Parameters:
        html (str): The HTML content from which to extract the company names.

    Returns:
        str: A semicolon-separated string of company names found in the HTML content.
    """
    ticker_pattern = re.compile(r'reuters\.com/markets/companies/(\w+)')
    soup = BeautifulSoup(html)
    candidates = soup.find_all('a')
    companies = [ticker_pattern.search(c['href']).group(1) for c in candidates if ticker_pattern.search(c['href'])]
    return ";".join(companies)


def process_articles(database_file: str) -> pd.DataFrame:
    articles_df = read_articles_from_db(database_file)
    articles_df['companies'] = articles_df['contentHTML'].apply(find_companies)
    return articles_df


articles_df = process_articles("DB.sqlite3")
print(articles_df)

