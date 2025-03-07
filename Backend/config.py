import os
from dotenv import load_dotenv
import json
from pathlib import Path
import pickle

load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama3-70b-8192"
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    FIRE_CRAWL_API_KEY = os.getenv("FIRE_CRAWL_API_KEY")
