import aiohttp
from config import COINGECKO_API_URL

COINGECKO_IDS = {
    'ethereum': 'ethereum',
    'binancecoin': 'binancecoin',
    'solana': 'solana',
    'optimism': 'ethereum',  # Uses ETH price
    'arbitrum': 'ethereum',  # Uses ETH price
    'polygon': 'matic-network',
}

async def fetch_coin_price(coin_id: str) -> float:
    params = {'ids': coin_id, 'vs_currencies': 'usd'}
    async with aiohttp.ClientSession() as session:
        async with session.get(COINGECKO_API_URL, params=params) as response:
            data = await response.json()
            return data[coin_id]['usd']