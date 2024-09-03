import aiohttp
from config import ALCHEMY_URLS, ALCHEMY_API_KEYS

async def fetch_gas_price(chain: str) -> float:
    if chain == 'binancecoin':
        # BNB Chain doesn't use Alchemy, so we'll return a placeholder value
        return 5  # Gwei

    url = f"{ALCHEMY_URLS[chain]}{ALCHEMY_API_KEYS[chain]}"

    async with aiohttp.ClientSession() as session:
        if chain == 'solana':
            json_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getRecentBlockhash",
                "params": []
            }
            async with session.post(url, json=json_data) as response:
                data = await response.json()
                return int(data['result']['value']['feeCalculator']['lamportsPerSignature']) / 1e9  # Convert lamports to SOL
        else:
            json_data = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_gasPrice",
                "params": []
            }
            async with session.post(url, json=json_data) as response:
                data = await response.json()
                return int(data['result'], 16) / 1e9  # Convert Wei to Gwei