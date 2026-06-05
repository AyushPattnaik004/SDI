from os import getenv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env'))

GEMINI_API_KEY = getenv("GEMINI_API_KEY")