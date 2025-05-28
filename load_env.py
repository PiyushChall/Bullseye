# load_env.py
import os
from dotenv import load_dotenv

def load_environment():
    load_dotenv()

    # Set explicitly in case some libraries need these in os.environ
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
    os.environ["FRED_API_KEY"] = os.getenv("FRED_API_KEY")
