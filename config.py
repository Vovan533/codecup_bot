import os
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.getenv('TOKEN')

ADMINS = [int(e) for e in os.getenv('ADMINS').strip().split(',') if e]

DB_INFO = (os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_HOST"))

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---

# уровень логирования в консоль
CONSOLE_LOGGING_LEVEL = 'DEBUG'
# Настройка формата логирования
LOGGING_SETUP = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'log_formatter': {
            'format': '[{asctime}][{levelname}] ::: {filename}({lineno}) -> {message}',
            'style': '{',
        },
    },
    'handlers': {
        'all_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/bot.log',  # путь до файла логирования
            'formatter': 'log_formatter',
        },
        'error_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/err_bot.log',  # путь до файла логирования ошибок
            'formatter': 'log_formatter',
        },
        'console': {
            'level': CONSOLE_LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'log_formatter',
        },
    },
    'loggers': {
        'logger': {
            'handlers': ['all_file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# Временные данные
START_TIME = 0
