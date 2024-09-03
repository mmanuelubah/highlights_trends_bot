import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Alchemy API Keys
ALCHEMY_API_KEYS = {
    'ethereum': os.getenv('ALCHEMY_ETH_API_KEY'),
    'optimism': os.getenv('ALCHEMY_OPTIMISM_API_KEY'),
    'arbitrum': os.getenv('ALCHEMY_ARBITRUM_API_KEY'),
    'polygon': os.getenv('ALCHEMY_POLYGON_API_KEY'),
    'solana': os.getenv('ALCHEMY_SOLANA_API_KEY'),
}

# Alchemy API URLs
ALCHEMY_URLS = {
    'ethereum': 'https://eth-mainnet.g.alchemy.com/v2/',
    'optimism': 'https://opt-mainnet.g.alchemy.com/v2/',
    'arbitrum': 'https://arb-mainnet.g.alchemy.com/v2/',
    'polygon': 'https://polygon-mainnet.g.alchemy.com/v2/',
    'solana': 'https://solana-mainnet.g.alchemy.com/v2/',
}

# CoinGecko API URL
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'