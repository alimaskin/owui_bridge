import os
from dotenv import load_dotenv

load_dotenv()

# Для чтения из langfuse_db
READ_DATABASE_URL = os.getenv("READ_DATABASE_URL")

# Для записи в owui_bridge
WRITE_DATABASE_URL = os.getenv("WRITE_DATABASE_URL")

print(f"Read from db: {READ_DATABASE_URL}")
print(f"Write to db: {WRITE_DATABASE_URL}")

LOTUS_API_KEY = os.getenv("LOTUS_API_KEY")
LOTUS_API_URL = os.getenv("LOTUS_API_URL")
