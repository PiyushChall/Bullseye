from fredapi import Fred
from google.agents.tools import tool
import os


fred = Fred(api_key=os.getenv("FRED_API_KEY"))

@tool
def get_macro_data(_: str) -> dict:
    """Pulls expanded macroeconomic indicators"""
    return {
        "interest_rate": round(fred.get_series("FEDFUNDS").dropna().iloc[-1], 2),
        "inflation": round(fred.get_series("CPIAUCSL").pct_change().dropna().iloc[-1] * 100, 2),
        "gdp_growth": round(fred.get_series("GDP").pct_change().dropna().iloc[-1] * 100, 2),
        "unemployment": round(fred.get_series("UNRATE").dropna().iloc[-1], 2),
        "consumer_sentiment": round(fred.get_series("UMCSENT").dropna().iloc[-1], 2),
        "leading_index": round(fred.get_series("USSLIND").dropna().iloc[-1], 2),
        "treasury_yield_10yr": round(fred.get_series("GS10").dropna().iloc[-1], 2),
    }
