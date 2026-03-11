import logging
import os

# CRIAR PASTA DE LOGS
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/sistema.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    encoding="utf-8"
)

def log_info(msg):
    logging.info(msg)

def log_warning(msg):
    logging.warning(msg)

def log_error(msg):
    logging.error(msg)