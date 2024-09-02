import os
import requests
import time
from requests.exceptions import RequestException
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class GasFeeFetcher:
    def __init__(self):
        self.chains = {
            'ethereum': 'https://api.etherscan.io/api',
            'binance': 'https://api.bscscan.com/api',
            'solana': 'https://api.solscan.io/api',
            'optimism': 'https://api.optimistic.etherscan.io/api',
            'arbitrum': 'https://api.arbiscan.io/api',
            'polygon': 'https://api.polygonscan.com/api',
            'tron': 'https://api.tronscan.org/api'
        }
        self.api_keys = {
            'ethereum': os.getenv('BIS5WSS9AUK4PM937TPJSJPKE1PTT9I9JQ'),
            'binance': os.getenv('8H1WZRSRB62NJ83F6QBY5ZRTWI6K59426M'),
            'solana': os.getenv('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE3MjUyNjc0MTk4NzcsImVtYWlsIjoidWJhaGNoaW5hemFAZ21haWwuY29tIiwiYWN0aW9uIjoidG9rZW4tYXBpIiwiYXBpVmVyc2lvbiI6InYxIiwiaWF0IjoxNzI1MjY3NDE5fQ.8BefrEiD6rfKH_jXWN3-uUp86rXM4iEhQJ4SeVZ7cxM'),
            'optimism': os.getenv('8ACEHFPVNQITMCETME9HPW6XWIU79AG6ES'),
            'arbitrum': os.getenv('5EJS66NYEMK3HH4MV3SA8GKMY6FHDQ4D8W'),
            'polygon': os.getenv('MQTKYD6UP9TFGHZCYTM5865NEQ1DNCA5GW'),
            'tron': os.getenv('4f0ba44b-380b-4cf5-8ddd-5c0753400833'),
        }
        self.coin_ids = {
            'ethereum': 'ethereum',
            'binance': 'binancecoin',
            'solana': 'solana',
            'optimism': 'optimism',
            'arbitrum': 'arbitrum-one',
            'polygon': 'matic-network',
            'tron': 'tron',
        }
        self.coingecko_api = 'https://api.coingecko.com/api/v3'
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def fetch_with_retry(self, url, params=None):
        response = None
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                return response.json()
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    raise  # Re-raise the last exception if all retries failed
                print(f"Attempt {attempt+1} failed with error: {str(e)}")
                if response.status_code == 429:  # Too Many Requests
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    time.sleep(self.retry_delay)

    def fetch_gas_fee(self, chain):
        url = self.chains[chain]
        params = {
            'module': 'gastracker',
            'action': 'gasoracle',
            'apikey': self.api_keys[chain]
        }

        try:
            data = self.fetch_with_retry(url, params)

            if data['status'] == '1':
                gas_price_gwei = int(data['result']['SafeGasPrice'])
                gas_price_usd = self.convert_gwei_to_usd(chain, gas_price_gwei)
                return gas_price_usd
            else:
                print(f"Error fetching gas fee for {chain}: {data.get('message', 'Unknown error')}")
                return None
        except RequestException as e:
            print(f"Error fetching gas fee for {chain}: {str(e)}")
            return None

    def convert_gwei_to_usd(self, chain, gwei):
        coin_id = self.coin_ids[chain]
        url = f"{self.coingecko_api}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd'
        }

        try:
            data = self.fetch_with_retry(url, params)

            if coin_id in data and 'usd' in data[coin_id]:
                price_usd = data[coin_id]['usd']

                # Set a default base_unit value
                base_unit = None

                # Convert Gwei to the base unit (ETH, BNB, etc.)
                if chain == 'ethereum':
                    base_unit = gwei / 1e9  # 1 ETH = 10^9 Gwei
                elif chain == 'binance':
                    base_unit = gwei / 1e9  # 1 BNB = 10^9 Gwei
                elif chain == 'arbitrum':
                    base_unit = gwei / 1e9  # 1 BNB = 10^9 Gwei
                elif chain == 'optimism':
                    base_unit = gwei / 1e9  # 1 BNB = 10^9 Gwei
                elif chain == 'solana':
                    base_unit = gwei / 1e9
                elif chain == 'polygon':
                    base_unit = gwei / 1e9
                elif chain == 'tron':
                    base_unit = gwei / 1e6

                if base_unit is not None:
                    usd_value = base_unit * price_usd
                    return usd_value
                else:
                    print(f"Error converting gas fee to USD for {chain}: Unknown chain")
                    return None
            else:
                print(f"Error converting gas fee to USD for {chain}: Price data not available")
                return None
        except RequestException as e:
            print(f"Error converting gas fee to USD for {chain}: {str(e)}")
            return None

    def get_all_gas_fees(self):
        gas_fees = {}
        for chain in self.chains:
            fee = self.fetch_gas_fee(chain)
            if fee is not None:
                gas_fees[chain] = fee
        return gas_fees
