import time
from logging import getLogger, FileHandler, Formatter, INFO

from utils.log import logs_path

map_log = getLogger("map_logger")
map_log.setLevel(INFO)
logging_format = "[%(levelname)s] [%(asctime)s] %(message)s"

# 根据日期生成日志文件名
filename = logs_path / (
    "log_" + time.strftime("%Y-%m-%d-%H-%M", time.localtime()) + ".txt"
)
file_handler = FileHandler(filename=filename, mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
map_log.addHandler(file_handler)
