from google.adk import Agent
from agents.tools import get_macro_data
import os

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")

class MacroAgent(Agent):
    def __init__(self):
        super().__init__(tools=[get_macro_data])

    async def run(self, task, scratchpad):
        ticker = task.inputs["ticker"]
        macro_data = get_macro_data(ticker)

        prompt = f"""
You are an economic strategist for a hedge fund evaluating {ticker}.

Here is the latest macroeconomic snapshot:
- Interest Rate: {macro_data['interest_rate']}%
- Inflation: {macro_data['inflation']}%
- GDP Growth: {macro_data['gdp_growth']}%
- Unemployment: {macro_data['unemployment']}%
- Consumer Sentiment: {macro_data['consumer_sentiment']}
- Leading Economic Index: {macro_data['leading_index']}
- 10-Year Treasury Yield: {macro_data['treasury_yield_10yr']}%

Analyze the state of the U.S. economy and answer the following:
1. What are the dominant macroeconomic risks?
2. What is the likely market impact for a company like {ticker}?
3. What sectors (if any) should an investor overweight or underweight?
4. What is the final macro sentiment rating? (bullish, neutral, bearish)

Return your response as structured JSON like:
{{
  "summary": "...",
  "risk_flags": ["..."],
  "sector_recommendation": "...",
  "rating": "..."
}}
"""

        response = await self.respond(prompt)
        return {
            "raw_data": macro_data,
            "insight": response.output
        }
