import requests
import os
from dotenv import load_dotenv
from fredapi import Fred
from google.adk.tools import FunctionTool
import google.generativeai as genai
import yfinance as yf
import numpy as np
import pandas as pd

# Load .env and API key
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")
Alpha = os.getenv("ALPHA_VANTAGE_API_KEY")

if not FRED_API_KEY:
    raise ValueError("FRED_API_KEY is not set in .env")

fred = Fred(api_key=FRED_API_KEY)

# Call Gemini with a prompt
model = genai.GenerativeModel("gemini-1.5-flash")

def get_macro_data(ticker: str) -> dict:
    """Fetch raw macroeconomic indicators for a stock. No reasoning, just raw values."""
    interest_rate = fred.get_series_latest_release('FEDFUNDS').iloc[-1]
    inflation = fred.get_series_latest_release('CPIAUCSL').iloc[-1]
    gdp = fred.get_series_latest_release('GDP').iloc[-1]

    return {
        "ticker": ticker,
        "interest_rate": float(interest_rate),
        "inflation": float(inflation),
        "gdp": float(gdp)
    }

BASE_URL = "https://www.alphavantage.co/query"

def fetch_indicator(params, key_name):
    response = requests.get(BASE_URL, params={**params, "apikey": Alpha})
    data = response.json()

    if key_name not in data:
        print(f"⚠️ Missing key '{key_name}' in response. Full response: {data}")
        return None

    try:
        return list(data[key_name].values())[-1]
    except Exception as e:
        print(f"⚠️ Error parsing '{key_name}': {e}")
        return None


def get_technical_data(ticker: str) -> dict:
    """
    Collects technical indicators (SMA, RSI) using Alpha Vantage,
    and uses Gemini to compute MACD from historical closing prices.
    """
    # Step 1: SMA
    sma_params = {
        "function": "SMA",
        "symbol": ticker,
        "interval": "daily",
        "time_period": 20,
        "series_type": "close",
        "apikey": Alpha
    }
    sma_data = requests.get(BASE_URL, params=sma_params).json()
    sma_20 = None
    try:
        sma_20 = list(sma_data["Technical Analysis: SMA"].values())[-1]["SMA"]
    except Exception as e:
        print(f"⚠️ SMA error: {e}")

    # Step 2: RSI
    rsi_params = {
        "function": "RSI",
        "symbol": ticker,
        "interval": "daily",
        "time_period": 14,
        "series_type": "close",
        "apikey": Alpha
    }
    rsi_data = requests.get(BASE_URL, params=rsi_params).json()
    rsi_14 = None
    try:
        rsi_14 = list(rsi_data["Technical Analysis: RSI"].values())[-1]["RSI"]
    except Exception as e:
        print(f"⚠️ RSI error: {e}")

    # yfinance - Historical closing prices
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")
        closing_prices = df["Close"].tolist()
    except Exception as e:
        print(f"⚠️ yfinance error: {e}")
        closing_prices = []

    # Manual MACD Calculation
    try:
        ema_12 = np.array(pd.Series(closing_prices).ewm(span=12).mean())
        ema_26 = np.array(pd.Series(closing_prices).ewm(span=26).mean())
        macd_line = ema_12 - ema_26
        signal_line = pd.Series(macd_line).ewm(span=9).mean()
        macd_hist = float(macd_line[-1] - signal_line.iloc[-1])
    except Exception as e:
        print(f"⚠️ MACD error: {e}")
        macd_hist = None

    # Final JSON
    return {
        "ticker": ticker.upper(),
        "sma_20": sma_20,
        "rsi_14": rsi_14,
        "macd_hist": macd_hist
    }



# ✅ Wrap in a FunctionTool (needed for GADK agents)
macro_tool = FunctionTool(func=get_macro_data)
technical_tool = FunctionTool(func=get_technical_data)