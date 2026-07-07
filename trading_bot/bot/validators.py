import re

def validate_symbol(symbol: str) -> str:
    """
    Validates the Binance ticker symbol.
    Must be alphanumeric, between 3 and 20 characters (e.g. BTCUSDT).
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string.")
    
    symbol_clean = symbol.strip().upper()
    
    # Binance symbols are alphanumeric (e.g., BTCUSDT, ETHUSDT)
    if not re.match(r'^[A-Z0-9]{3,20}$', symbol_clean):
        raise ValueError(f"Invalid symbol format: '{symbol}'. Must be alphanumeric (e.g. BTCUSDT).")
    
    return symbol_clean


def validate_side(side: str) -> str:
    """
    Validates order side. Must be BUY or SELL.
    """
    if not side or not isinstance(side, str):
        raise ValueError("Side must be a string ('BUY' or 'SELL').")
    
    side_clean = side.strip().upper()
    if side_clean not in ["BUY", "SELL"]:
        raise ValueError(f"Invalid side: '{side}'. Must be 'BUY' or 'SELL'.")
    
    return side_clean


def validate_order_type(order_type: str) -> str:
    """
    Validates order type. Supports MARKET, LIMIT, and STOP_LIMIT.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValueError("Order type must be a string ('MARKET', 'LIMIT', or 'STOP_LIMIT').")
    
    type_clean = order_type.strip().upper()
    if type_clean not in ["MARKET", "LIMIT", "STOP_LIMIT"]:
        raise ValueError(f"Invalid order type: '{order_type}'. Must be 'MARKET', 'LIMIT', or 'STOP_LIMIT'.")
    
    return type_clean


def validate_quantity(quantity) -> float:
    """
    Validates order quantity. Must be a positive float.
    """
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity: '{quantity}'. Must be a numeric value.")
        
    if qty_float <= 0:
        raise ValueError(f"Quantity must be greater than zero. Got: {qty_float}")
        
    return qty_float


def validate_price(price, order_type: str) -> float:
    """
    Validates order price.
    - Required and positive for LIMIT and STOP_LIMIT.
    - Must NOT be specified for MARKET.
    """
    order_type_clean = validate_order_type(order_type)
    
    if order_type_clean in ["LIMIT", "STOP_LIMIT"]:
        if price is None:
            raise ValueError(f"Price is required for {order_type_clean} orders.")
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price: '{price}'. Must be a numeric value.")
            
        if price_float <= 0:
            raise ValueError(f"Price must be greater than zero. Got: {price_float}")
        return price_float
    else:
        if price is not None:
            raise ValueError("Price cannot be specified for MARKET orders.")
        return None


def validate_stop_price(stop_price, order_type: str) -> float:
    """
    Validates stop price.
    - Required and positive for STOP_LIMIT.
    - Must NOT be specified for MARKET or LIMIT.
    """
    order_type_clean = validate_order_type(order_type)
    
    if order_type_clean == "STOP_LIMIT":
        if stop_price is None:
            raise ValueError("Stop Price is required for STOP_LIMIT orders.")
        try:
            stop_price_float = float(stop_price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid stop price: '{stop_price}'. Must be a numeric value.")
            
        if stop_price_float <= 0:
            raise ValueError(f"Stop Price must be greater than zero. Got: {stop_price_float}")
        return stop_price_float
    else:
        if stop_price is not None:
            raise ValueError(f"Stop Price cannot be specified for {order_type_clean} orders.")
        return None
