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

if not Alpha:
    raise ValueError("ALPHA_API_KEY is not set in .env")
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

def get_from_alpha(function, symbol, **params):
    """Request data from Alpha Vantage."""
    url = f"https://www.alphavantage.co/query"
    query = {
        "function": function,
        "symbol": symbol,
        "apikey": Alpha,
        **params
    }
    try:
        response = requests.get(url, params=query, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        print(f"⚠️ Alpha Vantage error: {e}")
        return None


def get_technical_data(ticker: str) -> dict:
    result = {"ticker": ticker.upper()}

    # SMA 20
    sma_data = get_from_alpha("SMA", ticker, interval="daily", time_period=20, series_type="close")
    try:
        result["sma_20"] = list(sma_data["Technical Analysis: SMA"].values())[-1]["SMA"]
    except Exception:
        result["sma_20"] = None

    # RSI 14
    rsi_data = get_from_alpha("RSI", ticker, interval="daily", time_period=14, series_type="close")
    try:
        result["rsi_14"] = list(rsi_data["Technical Analysis: RSI"].values())[-1]["RSI"]
    except Exception:
        result["rsi_14"] = None

    # MACD
    macd_data = get_from_alpha("MACD", ticker, interval="daily", series_type="close")
    try:
        result["macd_hist"] = list(macd_data["Technical Analysis: MACD"].values())[-1]["MACD_Hist"]
    except Exception:
        result["macd_hist"] = None

    # ADX
    adx_data = get_from_alpha("ADX", ticker, interval="daily", time_period=14)
    try:
        result["adx"] = list(adx_data["Technical Analysis: ADX"].values())[-1]["ADX"]
    except Exception:
        result["adx"] = None

    # ATR
    atr_data = get_from_alpha("ATR", ticker, interval="daily", time_period=14)
    try:
        result["atr"] = list(atr_data["Technical Analysis: ATR"].values())[-1]["ATR"]
    except Exception:
        result["atr"] = None

    # OBV
    obv_data = get_from_alpha("OBV", ticker, interval="daily")
    try:
        result["obv"] = list(obv_data["Technical Analysis: OBV"].values())[-1]["OBV"]
    except Exception:
        result["obv"] = None

    # Fallback to yfinance where needed
    try:
        data = yf.download(ticker, period="6mo", progress=False)
        close = data["Close"]

        if result["sma_20"] is None:
            result["sma_20"] = float(close.rolling(window=20).mean().iloc[-1])

        if result["rsi_14"] is None:
            delta = close.diff().dropna()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            result["rsi_14"] = float(100 - (100 / (1 + rs.iloc[-1])))

        if result["macd_hist"] is None:
            ema_12 = close.ewm(span=12, adjust=False).mean()
            ema_26 = close.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            result["macd_hist"] = float((macd_line - signal_line).iloc[-1])

        result["ema_20"] = float(close.ewm(span=20).mean().iloc[-1])
        result["ema_50"] = float(close.ewm(span=50).mean().iloc[-1])
        result["ema_200"] = float(close.ewm(span=200).mean().iloc[-1])

        sma = close.rolling(window=20).mean()
        std = close.rolling(window=20).std()
        result["bollinger_upper"] = float((sma + 2 * std).iloc[-1])
        result["bollinger_lower"] = float((sma - 2 * std).iloc[-1])

        result["volume"] = float(data["Volume"].iloc[-1])
        result["avg_volume_20d"] = float(data["Volume"].rolling(20).mean().iloc[-1])

    except Exception as e:
        print(f"⚠️ yfinance fallback error: {e}")

    return result



# ✅ Wrap in a FunctionTool (needed for GADK agents)
macro_tool = FunctionTool(func=get_macro_data)
technical_tool = FunctionTool(func=get_technical_data)