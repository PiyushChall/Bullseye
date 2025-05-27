from google.agents import Task

def macro_task(ticker: str):
    return Task(
        name="MacroEconomicAnalysis",
        description=f"Perform deep macroeconomic analysis with expanded indicators for {ticker}.",
        inputs={"ticker": ticker}
    )
