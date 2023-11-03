"""Module to generate logger"""
import logging
import os


def get_logger(class_name: str = "MAIN") -> logging.Logger:
    """Generate and return a logger object for a given class name."""

    logger = logging.getLogger(class_name)

    # Ensure the logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a file handler for the logger
    file_handler = logging.FileHandler(f"logs/{class_name}.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    return logger
