import logging
from bot.client import BinanceFuturesClient
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price
)

logger = logging.getLogger("trading_bot")

def execute_order(
    api_key: str = None,
    api_secret: str = None,
    coingecko_key: str = None,
    symbol: str = None,
    side: str = None,
    order_type: str = None,
    quantity = None,
    price=None,
    stop_price=None,
    mock_mode: bool = False
) -> dict:
    """
    Validates inputs, logs request details, executes order via BinanceFuturesClient,
    and returns/logs response details.
    """
    logger.info("Initializing order validation...")
    
    # 1. Validation
    try:
        validated_symbol = validate_symbol(symbol)
        validated_side = validate_side(side)
        validated_type = validate_order_type(order_type)
        validated_qty = validate_quantity(quantity)
        validated_price = validate_price(price, validated_type)
        validated_stop_price = validate_stop_price(stop_price, validated_type)
    except ValueError as e:
        logger.error(f"Validation Failure: {str(e)}")
        raise ValueError(f"Input Validation Error: {str(e)}")

    # 2. Log Order Request Summary
    logger.info("--- Order Request Summary ---")
    logger.info(f"Symbol:     {validated_symbol}")
    logger.info(f"Side:       {validated_side}")
    logger.info(f"Type:       {validated_type}")
    logger.info(f"Quantity:   {validated_qty}")
    if validated_price is not None:
        logger.info(f"Price:      {validated_price}")
    if validated_stop_price is not None:
        logger.info(f"Stop Price: {validated_stop_price}")
    logger.info("-----------------------------")

    # 3. Execution
    try:
        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            coingecko_key=coingecko_key,
            mock_mode=mock_mode
        )
        
        logger.info(f"Submitting order to client...")
        response = client.place_order(
            symbol=validated_symbol,
            side=validated_side,
            order_type=validated_type,
            quantity=validated_qty,
            price=validated_price,
            stop_price=validated_stop_price
        )
        
        # 4. Extract Response Details
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", "0.0000")
        avg_price = response.get("avgPrice", "0.00")
        
        # Formatting output
        avg_price_num = float(avg_price)
        avg_price_display = f"{avg_price_num:.2f}" if avg_price_num > 0 else "N/A"
        
        logger.info("=== Order Execution Success ===")
        logger.info(f"Order ID:     {order_id}")
        logger.info(f"Status:       {status}")
        logger.info(f"Executed Qty: {executed_qty}")
        logger.info(f"Avg Price:    {avg_price_display}")
        logger.info("==============================")
        
        return response

    except Exception as e:
        logger.error(f"=== Order Execution Failure ===")
        logger.error(f"Error Details: {str(e)}")
        logger.error("===============================")
        raise e
