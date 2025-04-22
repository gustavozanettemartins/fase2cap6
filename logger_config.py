import logging
from colorama import init, Fore, Style

init(autoreset=True)

LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        original_msg = record.msg
        color = LEVEL_COLORS.get(record.levelno, "")
        record.msg = f"{color}{original_msg}{Style.RESET_ALL}"
        formatted = super().format(record)
        record.msg = original_msg
        return formatted


file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger("sistema_agro")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter('%(asctime)s - %(levelname)s - %(message)s'))
# logger.addHandler(console_handler)

file_handler_info = logging.FileHandler('log.log')
file_handler_info.setLevel(logging.DEBUG)
file_handler_info.addFilter(lambda record: record.levelno < logging.ERROR)
file_handler_info.setFormatter(file_formatter)
# logger.addHandler(file_handler_info)

file_handler_error = logging.FileHandler('error.log')
file_handler_error.setLevel(logging.ERROR)
file_handler_error.setFormatter(file_formatter)
# logger.addHandler(file_handler_error)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler_info)
    logger.addHandler(file_handler_error)
