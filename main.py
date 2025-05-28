from agents.macro_agent import macro_agent
from agents.tools import get_macro_data
from agents.technical_agent import technical_agent
from agents.tools import get_technical_data

ticker = input("Stock to Analyse: ")
# Send request
macro_response = macro_agent.send_message(f"Fetch macroeconomic indicators for {ticker}", stream=False)

macro_json = None
for candidate in macro_response.candidates:
    for part in candidate.content.parts:
        if hasattr(part, "function_call"):
            func_call = part.function_call
            args = dict(func_call.args.items())
            if func_call.name == "get_macro_data":
                macro_json = get_macro_data(**args)

print("📊 Macro Data JSON:", macro_json)

technical_response = technical_agent.send_message(f"Fetch technical indicators for {ticker}", stream=False)

technical_json = None
for candidate in technical_response.candidates:
    for part in candidate.content.parts:
        if hasattr(part, "function_call"):
            func_call = part.function_call
            args = dict(func_call.args.items())
            if func_call.name == "get_technical_data":
                technical_json = get_technical_data(**args)

print("📈 Technical Indicators JSON:", technical_json)
