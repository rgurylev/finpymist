import os
from dotenv import load_dotenv
from pathlib import Path

if os.path.exists(".env"):
    load_dotenv(dotenv_path=".env")

TINKOFF_TOKEN = os.environ["TINKOFF_TOKEN"]
ROOT_DIR = Path(__file__).resolve().parents[0]
LOG_DIR = ROOT_DIR / 'log'
DATA_DIR = ROOT_DIR / 'data'


#print (LOG_DIR )


