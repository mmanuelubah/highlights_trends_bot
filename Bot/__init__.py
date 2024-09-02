"""
Telegram Bot for Gas Fee Alerts

This package contains modules for fetching gas fees,
managing user preferences, and running the Telegram bot.


    your-repo-name/
    ├── bot/
    │   ├── init.py
    │   ├── main.py
    │   ├── gas_fee_fetcher.py
    │   └── user_preferences.py
    ├── requirements.in
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    └── .env
"""

__version__ = "1.0.0"

#from .main import start_bot
from .gas_fee_fetcher import GasFeeFetcher
from .user_preferences import UserPreferences

# Initialization code
import logging
logging.basicConfig(level=logging.INFO)
