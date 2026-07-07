import os
import sys
from dotenv import load_dotenv

# Add directory to sys.path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.orders import execute_order
from bot.logging_config import setup_logging

def run_verification():
    # Load .env file
    load_dotenv()
    
    binance_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_API_SECRET")
    coingecko_key = os.getenv("API_KEY") or os.getenv("COINGECKO_API_KEY")
    
    print("Starting Trading Bot verification and log generation...")
    if binance_key and binance_secret and binance_key != "YOUR_BINANCE_API_KEY":
        print(f"Loaded Binance API Key: {binance_key[:6]}...")
    if coingecko_key and coingecko_key != "YOUR_API_KEY":
        print(f"Loaded CoinGecko API Key: {coingecko_key[:6]}...")
    
    # Initialize logging pointing to trading_bot.log in the same folder
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading_bot.log")
    setup_logging(log_file)

    # 1. Place a MARKET BUY order
    print("\n--- Placing MARKET BUY Order ---")
    try:
        execute_order(
            api_key=binance_key,
            api_secret=binance_secret,
            coingecko_key=coingecko_key,
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.05,
            mock_mode=False
        )
    except Exception as e:
        print(f"Failed: {e}")

    # 2. Place a LIMIT SELL order
    print("\n--- Placing LIMIT SELL Order ---")
    try:
        execute_order(
            api_key=binance_key,
            api_secret=binance_secret,
            coingecko_key=coingecko_key,
            symbol="ETHUSDT",
            side="SELL",
            order_type="LIMIT",
            quantity=1.5,
            price=3500.00,
            mock_mode=False
        )
    except Exception as e:
        print(f"Failed: {e}")

    # 3. Place a STOP_LIMIT BUY order (Bonus Feature)
    print("\n--- Placing STOP_LIMIT BUY Order ---")
    try:
        execute_order(
            api_key=binance_key,
            api_secret=binance_secret,
            coingecko_key=coingecko_key,
            symbol="SOLUSDT",
            side="BUY",
            order_type="STOP_LIMIT",
            quantity=10.0,
            price=145.00,
            stop_price=140.00,
            mock_mode=False
        )
    except Exception as e:
        print(f"Failed: {e}")

    print(f"\nVerification completed. Logs saved to: {log_file}")

if __name__ == "__main__":
    run_verification()
