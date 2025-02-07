import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logger(name):
    logger = logging.getLogger(name)
    
    # Set logging level
    logger.setLevel(logging.INFO)
    
    # Create handlers
    # Console handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    
    # File handler - new file for each day
    log_filename = f"logs/contract_analyzer_{datetime.now().strftime('%Y-%m-%d')}.log"
    f_handler = logging.FileHandler(log_filename)
    f_handler.setLevel(logging.INFO)
    
    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(log_format)
    f_handler.setFormatter(log_format)
    
    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    
    return logger 