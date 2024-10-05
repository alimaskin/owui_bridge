import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
LOTUS_API_KEY = os.getenv("LOTUS_API_KEY")
LOTUS_API_URL = os.getenv("LOTUS_API_URL")
