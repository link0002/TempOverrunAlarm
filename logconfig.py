import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger()
logger.setLevel(level=logging.ERROR)

log_file_name_local = './logs/log_lyq'

formatter = '%(asctime)s - %(message)s'

# 本地轮转日志代码
time_rotate_file = TimedRotatingFileHandler(filename=log_file_name_local, when='H', interval=24, backupCount=24)
time_rotate_file.setFormatter(logging.Formatter(formatter))
time_rotate_file.setLevel(logging.ERROR)
logger.addHandler(time_rotate_file)

# 控制台日志代码
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter(formatter))
logger.addHandler(console_handler)

"""
    S - Seconds
    M - Minutes
    H - Hours
    D - Days
"""
