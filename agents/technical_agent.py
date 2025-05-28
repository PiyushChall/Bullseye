import google.generativeai as genai
from agents.tools import get_technical_data
from dotenv import load_dotenv

load_dotenv()

technical_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[get_technical_data],
)

technical_agent = technical_model.start_chat()
