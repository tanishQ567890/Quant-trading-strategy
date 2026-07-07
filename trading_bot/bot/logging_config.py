import logging
import os

def setup_logging(log_filename="trading_bot.log"):
    """
    Sets up a logger for the trading bot that logs to both:
    1. A detailed log file (trading_bot.log) at DEBUG level.
    2. A clean CLI console output at INFO level.
    """
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Resolve log path
    log_path = os.path.abspath(log_filename)
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # File Handler (Detailed)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler (Clean/Informational)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
