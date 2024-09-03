# Gas Price Alert Telegram Bot
This Telegram bot provides real-time gas price updates for various blockchain networks. 
Users can set custom alert thresholds and receive continuous updates on gas prices in 
USD.
## Features
- Real-time gas price updates for multiple blockchain networks - Custom alert thresholds 
for each chain - Continuous updates with emoji indicators based on price relative to 
threshold - Automatic stopping of updates after user inactivity
## Supported Chains
- Ethereum - BNB Chain - Solana - Optimism - Arbitrum - Polygon
## Commands
- `/start`: Begin interaction with the bot and select a chain for updates - `/alert 
<chain> <threshold>`: Set an alert threshold for a specific chain - `/stop`: Stop 
receiving updates
## Setup
1. Clone this repository 2. Install required packages: `pip install -r requirements.txt` 
3. Set up your Telegram Bot Token in `config.py` 4. Run the bot: `python bot.py`
## Dependencies
- python-telegram-bot - asyncio - tenacity
## Contributing
Contributions, issues, and feature requests are welcome. Feel free to check [issues 
page](https://github.com/mmanuelubah/GAS_FeesBot/issues) if you want to contribute.
## Author
Developed by mmanuelubah
## License
This project is licensed under the MIT License - see the [LICENSE](nil) file for details.n
