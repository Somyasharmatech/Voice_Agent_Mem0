import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger with standard formatting.
    Logs to both console and standard rotating file 'app.log'.
    
    Args:
        name (str): The name of the module invoking the logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicating logs if logger already has handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (Rotating, max 5MB per file, max 3 backups)
    log_file = "app.log"
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # Ignore file handler creation failure in restricted environments
        pass
        
    return logger
