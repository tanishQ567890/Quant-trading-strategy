# Binance Futures Simulator (CoinGecko Price Feed)

A clean, structured Python application to simulate placing Market, Limit, and Stop-Limit orders on the **Binance Futures Testnet (USDT-M)**, using the **CoinGecko API** as a live price oracle. It features strict input validation, detailed logging of all requests/responses, clear command line interaction, and an interactive CLI prompt wizard.

---

##  Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # API layer: handles signing, REST requests, and mock simulation fallback
│   ├── orders.py            # Order layer: handles input validation routing and execution orchestration
│   ├── validators.py        # Validation utility: validates symbol, side, order type, qty, and prices
│   └── logging_config.py    # Log configurations: logs detailed logs to file and clean logs to console
├── cli.py                   # Command Line Interface (accepts arguments and runs interactive wizard)
├── verify.py                # Verification script to place sample mock orders and generate logs
├── requirements.txt         # Required third-party libraries
├── .env.example             # Template env file for credentials
└── trading_bot.log          # Detailed execution log (generated automatically)
```

---

##  Setup Steps

### 1. Prerequisite
Ensure Python 3.9+ is installed on your system.

### 2. Navigate to the Directory
```bash
cd trading_bot
```

### 3. Initialize Virtual Environment
```bash
python -m venv .venv
```

### 4. Activate Virtual Environment
* **Windows (cmd/PowerShell)**:
  ```powershell
  .venv\Scripts\activate
  ```
* **macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration (Optional)

The bot dynamically selects its operating mode based on configured environment variables in your `.env` file:

1. **Live Binance Futures Testnet Mode**:
   Enable this to place real testnet orders on Binance (default if keys are present).
   ```text
   BINANCE_API_KEY=your_binance_testnet_api_key
   BINANCE_API_SECRET=your_binance_testnet_api_secret
   ```
2. **CoinGecko price-simulation Mode**:
   Enable this if you do not have Binance keys but want live pricing updates for simulation.
   ```text
   API_KEY=your_coingecko_api_key
   ```
3. **Offline Fallback Mode**:
   If no keys are configured, the bot automatically simulates executions offline using default asset prices (e.g. BTC at $64k, ETH at $3.4k).

**Setup Instructions**:
1. Copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the credentials for your desired mode of operation.

---

##  How to Run Examples

### 1. Interactive Wizard Mode (Recommended)
Simply execute the script without any parameters (or pass `-i` / `--interactive`). It will prompt you step-by-step with real-time validation:
```bash
python cli.py
```

### 2. CLI Parameter Mode
Pass the arguments directly to place orders from the command line:

#### A. Place a MARKET Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.05
```

#### B. Place a LIMIT Order
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 1.5 --price 3500.00
```

#### C. Place a STOP_LIMIT Order (Bonus Feature)
```bash
python cli.py --symbol SOLUSDT --side BUY --type STOP_LIMIT --qty 10.0 --price 145.00 --stop-price 140.00
```

### 3. Force Mock Mode
You can explicitly force the dry-run mock mode even if you have keys configured by adding the `--mock` flag:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.05 --mock
```

---

##  Assumptions

1. **Auto-Mock Fallback**: If the CoinGecko `API_KEY` is not set or left blank, the application runs in an offline mock mode using default local asset prices.
2. **USDT-M Futures Contract Specifications**: Order quantities and prices are evaluated against real-time prices fetched from CoinGecko. The basic validator enforces positive numeric values.
3. **Time-in-Force (TIF)**: Standard `GTC` (Good 'Til Cancelled) is default-applied to LIMIT and STOP_LIMIT orders.
