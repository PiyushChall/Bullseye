import google.generativeai as genai
from agents.tools import get_macro_data
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("FRED_API_KEY is not set in .env")
genai.configure(api_key=google_api_key)  # not service account

macro_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",  # or "gemini-1.0-pro"
    tools=[get_macro_data],
)

macro_agent = macro_model.start_chat()

