import os
import argparse
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

# Set up path resolution to import package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.orders import execute_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price
)

# Custom color theme
custom_theme = Theme({
    "success": "bold green",
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "accent": "bold magenta"
})

console = Console(theme=custom_theme)
logger = setup_logging()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--symbol", type=str, help="Ticker symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="Order side (BUY or SELL)")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT", "STOP_LIMIT"], help="Order type")
    parser.add_argument("--qty", type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price (required for LIMIT & STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, help="Trigger price (required for STOP_LIMIT)")
    parser.add_argument("--mock", action="store_true", help="Force Mock/Dry-Run execution")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive wizard mode")
    return parser.parse_args()

def interactive_wizard():
    console.print(Panel("[accent]Binance Futures Simulator (CoinGecko Price Feed)[/accent]\nFollow the prompts to configure your order.", title="Interactive Wizard"))
    
    # 1. Symbol
    while True:
        symbol = Prompt.ask("[info]Enter Symbol[/info] (e.g., BTCUSDT)").strip().upper()
        try:
            symbol = validate_symbol(symbol)
            break
        except ValueError as e:
            console.print(f"[error]Error:[/error] {e}")
            
    # 2. Side
    side = Prompt.ask("[info]Enter Side[/info]", choices=["BUY", "SELL", "buy", "sell"], default="BUY").upper()
    
    # 3. Order Type
    order_type = Prompt.ask("[info]Enter Order Type[/info]", choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"], default="MARKET").upper()
    
    # 4. Quantity
    while True:
        qty_str = Prompt.ask("[info]Enter Quantity[/info]")
        try:
            quantity = validate_quantity(qty_str)
            break
        except ValueError as e:
            console.print(f"[error]Error:[/error] {e}")
            
    # 5. Price (if LIMIT or STOP_LIMIT)
    price = None
    if order_type in ["LIMIT", "STOP_LIMIT"]:
        while True:
            price_str = Prompt.ask(f"[info]Enter Price for {order_type}[/info]")
            try:
                price = validate_price(price_str, order_type)
                break
            except ValueError as e:
                console.print(f"[error]Error:[/error] {e}")

    # 6. Stop Price (if STOP_LIMIT)
    stop_price = None
    if order_type == "STOP_LIMIT":
        while True:
            stop_price_str = Prompt.ask("[info]Enter Stop (Trigger) Price[/info]")
            try:
                stop_price = validate_stop_price(stop_price_str, order_type)
                break
            except ValueError as e:
                console.print(f"[error]Error:[/error] {e}")

    return symbol, side, order_type, quantity, price, stop_price

def main():
    # Load API keys from .env if present
    load_dotenv()
    
    binance_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_API_SECRET")
    coingecko_key = os.getenv("API_KEY") or os.getenv("COINGECKO_API_KEY")
    
    args = parse_args()
    
    # Determine if we should trigger interactive mode
    is_interactive = args.interactive or (
        args.symbol is None and 
        args.side is None and 
        args.type is None and 
        args.qty is None
    )
    
    mock_mode = args.mock
    
    if is_interactive:
        symbol, side, order_type, quantity, price, stop_price = interactive_wizard()
    else:
        symbol = args.symbol
        side = args.side
        order_type = args.type
        quantity = args.qty
        price = args.price
        stop_price = args.stop_price
        
        # Verify required arguments for CLI non-interactive mode
        if not symbol or not side or not order_type or quantity is None:
            console.print("[error]Error: Missing required arguments.[/error]")
            console.print("Run [accent]python cli.py --help[/accent] for details, or run [accent]python cli.py[/accent] without arguments to start the interactive wizard.")
            sys.exit(1)

    # Resolve active execution mode for console notification
    has_binance = binance_key and binance_secret and binance_key != "YOUR_API_KEY" and binance_secret != "YOUR_API_SECRET"
    has_coingecko = coingecko_key and coingecko_key != "YOUR_API_KEY" and coingecko_key.strip() != ""

    if not mock_mode:
        if has_binance:
            console.print("[success]Active Mode: Live Binance Testnet Execution[/success]")
        elif has_coingecko:
            console.print("[info]Active Mode: CoinGecko Price Simulation[/info]")
        else:
            console.print("[warning]Active Mode: Offline Fallback Simulation (missing API credentials)[/warning]")
    else:
        console.print("[warning]Active Mode: Forced Simulation Mode[/warning]")

    try:
        # Execute order placement
        response = execute_order(
            api_key=binance_key,
            api_secret=binance_secret,
            coingecko_key=coingecko_key,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            mock_mode=mock_mode
        )
        
        # Format response outputs
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", "0.0000")
        avg_price = response.get("avgPrice", "0.00")
        
        avg_price_num = float(avg_price)
        avg_price_display = f"{avg_price_num:.2f}" if avg_price_num > 0 else "N/A"
        
        # Mode label resolution
        if mock_mode:
            mode_label = "[warning]FORCED SIMULATION[/warning]"
        elif has_binance:
            mode_label = "[success]LIVE TESTNET[/success]"
        elif has_coingecko:
            mode_label = "[info]COINGECKO SIMULATION[/info]"
        else:
            mode_label = "[warning]OFFLINE FALLBACK[/warning]"
        
        result_text = (
            f"Execution Mode: {mode_label}\n"
            f"Order ID:       [info]{order_id}[/info]\n"
            f"Symbol:         [info]{symbol}[/info]\n"
            f"Side:           [accent]{side}[/accent]\n"
            f"Type:           [accent]{order_type}[/accent]\n"
            f"Status:         [success]{status}[/success]\n"
            f"Executed Qty:   [info]{executed_qty}[/info]\n"
            f"Avg Price:      [info]{avg_price_display}[/info]"
        )
        
        console.print(Panel(result_text, title="Order Response Details", border_style="green"))
        
    except Exception as e:
        console.print(Panel(f"[error]Order Placement Failed[/error]\n{str(e)}", title="Execution Error", border_style="red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
