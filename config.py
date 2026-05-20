from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

CIVETTA_CHANNEL = int(os.getenv("CIVETTA_CHANNEL"))
MAIN_CHANNEL = int(os.getenv("MAIN_CHANNEL"))

AFFILIATE_TAG = os.getenv("AFFILIATE_TAG")