import os
from dotenv import load_dotenv

# Specify the path to the .env file inside the config folder
load_dotenv(dotenv_path='config/.env')

API_KEY_SERPAPI = os.getenv("API_KEY_SERPAPI")
API_KEY_GROQ = os.getenv("API_KEY_GROQ")