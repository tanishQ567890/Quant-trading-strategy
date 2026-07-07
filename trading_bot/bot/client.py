import time
import hmac
import hashlib
import urllib.parse
import requests
import logging
import random

logger = logging.getLogger("trading_bot")

# Simple in-memory cache for mapping exchange symbols to CoinGecko IDs
SYMBOL_TO_COINGECKO = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "XRP": "ripple",
    "DOT": "polkadot",
    "LTC": "litecoin",
    "LINK": "chainlink",
    "BNB": "binancecoin",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "TRX": "tron",
    "UNI": "uniswap",
    "ETC": "ethereum-classic",
    "USDT": "tether",
    "USDC": "usd-coin"
}

class BinanceFuturesClient:
    """
    Unified Binance Futures Testnet Client.
    Supports:
    1. LIVE Mode: Places real orders on Binance Testnet if active API keys are provided.
    2. CoinGecko Simulation Mode: Runs price simulations via CoinGecko API key.
    3. Offline Mode: Fallback pricing simulations when no keys are configured.
    """
    BASE_URL = "https://testnet.binancefuture.com"
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self, api_key: str = None, api_secret: str = None, coingecko_key: str = None, mock_mode: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.coingecko_key = coingecko_key
        self.mock_mode = mock_mode

        # Check if live Binance credentials are set
        self.live_binance = False
        if self.api_key and self.api_secret:
            if self.api_key != "YOUR_API_KEY" and self.api_secret != "YOUR_API_SECRET":
                if self.api_key.strip() != "" and self.api_secret.strip() != "":
                    self.live_binance = True

        # Check if CoinGecko key is set
        self.use_coingecko = False
        if self.coingecko_key and self.coingecko_key != "YOUR_API_KEY" and self.coingecko_key.strip() != "":
            self.use_coingecko = True

        # Log operating mode
        if self.mock_mode:
            logger.info("Client initialized in explicit MOCK/SIMULATION Mode.")
        elif self.live_binance:
            logger.info("Client initialized in LIVE BINANCE TESTNET Mode.")
        elif self.use_coingecko:
            logger.info("Client initialized in COINGECKO SIMULATION Mode (Binance credentials missing).")
        else:
            logger.info("Client initialized in OFFLINE MOCK Mode (all credentials missing).")

    def _generate_signature(self, params: dict) -> str:
        """Generates HMAC-SHA256 signature for parameters."""
        query_string = urllib.parse.urlencode(params)
        secret_bytes = bytes(self.api_secret, 'utf-8')
        signature = hmac.new(secret_bytes, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def _clean_symbol(self, symbol: str) -> str:
        """Extracts the base asset from a trading pair (e.g. BTCUSDT -> BTC)."""
        symbol_upper = symbol.strip().upper()
        # Remove common stablecoin quotes
        for quote in ["USDT", "USDC", "BUSD", "USD"]:
            if symbol_upper.endswith(quote) and symbol_upper != quote:
                return symbol_upper[:-len(quote)]
        return symbol_upper

    def _resolve_coingecko_id(self, symbol: str) -> str:
        """Maps a symbol to a CoinGecko ID via cache or Search API."""
        base_symbol = self._clean_symbol(symbol)
        
        if base_symbol in SYMBOL_TO_COINGECKO:
            return SYMBOL_TO_COINGECKO[base_symbol]

        if not self.use_coingecko:
            return base_symbol.lower()

        # Query Search API
        url = f"{self.COINGECKO_BASE_URL}/search"
        headers = {"x-cg-demo-api-key": self.coingecko_key}
        params = {"query": base_symbol}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                coins = data.get("coins", [])
                for coin in coins:
                    if coin.get("symbol", "").upper() == base_symbol:
                        coin_id = coin.get("id")
                        SYMBOL_TO_COINGECKO[base_symbol] = coin_id
                        return coin_id
                if coins:
                    coin_id = coins[0].get("id")
                    SYMBOL_TO_COINGECKO[base_symbol] = coin_id
                    return coin_id
        except Exception as e:
            logger.error(f"Failed to query CoinGecko search for symbol '{symbol}': {e}")

        return base_symbol.lower()

    def get_live_price(self, coingecko_id: str) -> float:
        """Queries CoinGecko simple price endpoint to get the current price in USD."""
        if not self.use_coingecko:
            return self._get_offline_price(coingecko_id)

        url = f"{self.COINGECKO_BASE_URL}/simple/price"
        headers = {"x-cg-demo-api-key": self.coingecko_key}
        params = {
            "ids": coingecko_id,
            "vs_currencies": "usd"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = data.get(coingecko_id, {}).get("usd")
                if price is not None:
                    return float(price)
        except Exception as e:
            logger.error(f"Error fetching live price for ID '{coingecko_id}': {e}")

        return self._get_offline_price(coingecko_id)

    def _get_offline_price(self, coingecko_id: str) -> float:
        """Provides offline mock price fallback."""
        fallbacks = {
            "bitcoin": 64000.00,
            "ethereum": 3400.00,
            "solana": 142.50,
            "cardano": 0.45,
            "dogecoin": 0.12,
            "ripple": 0.58,
            "tether": 1.00
        }
        price = fallbacks.get(coingecko_id, 100.00)
        logger.warning(f"Using offline price fallback for '{coingecko_id}': ${price:.2f}")
        return price

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None) -> dict:
        """
        Places order on Binance Futures Testnet or runs simulation if mock_mode/offline.
        """
        # 1. Build parameters
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
            "timestamp": int(time.time() * 1000)
        }

        if order_type in ["LIMIT", "STOP_LIMIT"]:
            params["price"] = str(price)
            params["timeInForce"] = "GTC"
        if order_type == "STOP_LIMIT":
            params["stopPrice"] = str(stop_price)

        # 2. If in live mode and not forced mock, send request to actual Testnet
        if self.live_binance and not self.mock_mode:
            headers = {"X-MBX-APIKEY": self.api_key}
            params["signature"] = self._generate_signature(params)
            url = f"{self.BASE_URL}/fapi/v1/order"

            logger.debug(f"API Request URL: {url} | Params: {params}")
            try:
                response = requests.post(url, data=params, headers=headers, timeout=10)
                logger.debug(f"API Response: {response.status_code} | {response.text}")
                
                if response.status_code != 200:
                    try:
                        err_json = response.json()
                        err_msg = err_json.get("msg", response.text)
                        err_code = err_json.get("code", response.status_code)
                        raise Exception(f"Binance API Error [{err_code}]: {err_msg}")
                    except ValueError:
                        raise Exception(f"Binance Server Error: {response.status_code} - {response.text}")

                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error during order placement: {str(e)}")
                raise ConnectionError(f"Network connection failed: {str(e)}")

        # 3. Otherwise run simulation (CoinGecko / Offline)
        cg_id = self._resolve_coingecko_id(symbol)
        live_price = self.get_live_price(cg_id)

        logger.debug(f"[Simulated API Request] Symbol: {symbol} | Side: {side} | Type: {order_type} | Qty: {quantity} | Target Price: {price} | Stop: {stop_price} | Live Price: {live_price}")
        time.sleep(random.uniform(0.05, 0.2))

        order_id = random.randint(1000000000, 9999999999)
        executed_qty = 0.0
        avg_price = 0.0
        status = "NEW"

        if order_type == "MARKET":
            status = "FILLED"
            executed_qty = quantity
            avg_price = live_price
        elif order_type == "LIMIT":
            if side == "BUY" and price >= live_price:
                status = "FILLED"
                executed_qty = quantity
                avg_price = price
            elif side == "SELL" and price <= live_price:
                status = "FILLED"
                executed_qty = quantity
                avg_price = price
        elif order_type == "STOP_LIMIT":
            if side == "BUY" and live_price >= stop_price:
                if price >= live_price:
                    status = "FILLED"
                    executed_qty = quantity
                    avg_price = price
            elif side == "SELL" and live_price <= stop_price:
                if price <= live_price:
                    status = "FILLED"
                    executed_qty = quantity
                    avg_price = price

        mock_response = {
            "orderId": order_id,
            "symbol": symbol,
            "status": status,
            "clientOrderId": f"cg_sim_{random.randint(100000, 999999)}",
            "price": f"{price:.2f}" if price else "0.00",
            "avgPrice": f"{avg_price:.2f}",
            "origQty": f"{quantity:.4f}",
            "executedQty": f"{executed_qty:.4f}",
            "cumQty": f"{executed_qty:.4f}",
            "cumQuote": f"{(executed_qty * (avg_price if avg_price > 0 else (price if price else live_price))):.2f}",
            "timeInForce": "GTC",
            "type": order_type,
            "reduceOnly": False,
            "closePosition": False,
            "side": side,
            "positionSide": "BOTH",
            "stopPrice": f"{stop_price:.2f}" if stop_price else "0.00",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": order_type,
            "updateTime": int(time.time() * 1000)
        }

        logger.debug(f"[Simulated API Response] Body: {mock_response}")
        return mock_response
