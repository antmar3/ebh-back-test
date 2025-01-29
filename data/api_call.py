import pandas as pd
import random
import requests as r
import datetime as dt
import time as t
import matplotlib.pyplot as plt

# API Key
api_key = "ZY8gNgR0v6gv2oac"

# Base URL for the IVolatility API endpoint
BASE_URL = "https://restapi.ivolatility.com/equities/eod/nearest-option-tickers-with-prices-nbbo"

# Function to get market data for a given symbol and parameters
def get_market_data(symbol, startDate=None, dte=1000, moneyness=0, cp='P', retries=3):
    params = {
        "apiKey": api_key,
        "symbol": symbol,
        "startDate": startDate,=
        "dte": dte,
        "moneyness": moneyness,
        "cp": cp
    }

    for attempt in range(retries):
        try:
            response = r.get(BASE_URL, params=params, timeout=300)
            if response.status_code == 200:
                return response.json()
            else:
                return {"Error": f"HTTP {response.status_code} - {response.text}"}
        except Exception as e:
            print(f"Error fetching data for {startDate} (Attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                t.sleep(60 + random.randint(1, 30))

# Adjust for weekend dates
def adjust_for_weekend(start_date):
    weekday = start_date.weekday()  # Monday is 0, Sunday is 6
    if weekday == 5:  # Saturday
        return start_date - dt.timedelta(days=1)
    elif weekday == 6:  # Sunday
        return start_date - dt.timedelta(days=2)
    else:
        return start_date

# Generate a list of January 5th dates from 2004 to 2025
def generate_dates():
    start_year = 2005
    end_year = 2025
    return [
        adjust_for_weekend(dt.date(year, 1, 24)).strftime('%Y-%m-%d')
        for year in range(start_year, end_year + 1)
    ]

# Fetch market data for each date
def fetch_market_data(dates):
    all_market_data = pd.DataFrame()

    for date in dates:
        print(f"Fetching data for {date}...", end='')
        market_data = get_market_data(
            symbol='SPY',
            startDate=date,
            dte=1000,
            moneyness=0,
            cp='P'
        )

        if 'Error' in market_data:
            print(f"Error fetching data for {date}: {market_data['Error']}")
        else:
            data_list = market_data.get('data', [])
            if data_list:
                temp_df = pd.DataFrame(data_list)
                temp_df["start_date"] = date  # Add the startDate as a column for traceability
                all_market_data = pd.concat([all_market_data, temp_df], ignore_index=True)
                print()
                print(f"Collected data for {date} ✔")
            else:
                print(f"No data found for {date}")

        t.sleep(5)  # Adjust sleep interval to avoid hitting API limits

    return all_market_data

# Main script
if __name__ == "__main__":
    dates = generate_dates()
    market_data = fetch_market_data(dates)

    # Save the data to an Excel file
    market_data.to_excel('ebh_strategy_backtest\\SPY_ATM_Puts_MarketData_2005_2025.xlsx', header=True, index=False)
    print("Data saved to SPY_ATM_Puts_MarketData_2005_2025.xlsx")
