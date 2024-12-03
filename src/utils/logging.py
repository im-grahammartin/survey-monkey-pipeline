import logging
import os

def logging_init():
    logFileName='logs/mainlog.log'
    os.makedirs(os.path.dirname(logFileName), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logFileName)
        ]
    )