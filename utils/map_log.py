import os,time
from logging import getLogger, FileHandler, Formatter, INFO

map_log = getLogger('map_logger')
map_log.setLevel(INFO)
logging_format = "%(levelname)s %(message)s"

# 根据日期生成日志文件名
if not os.path.exists('logs'):
    os.mkdir('logs')
filename = "logs\\log_"  + time.strftime("%Y-%m-%d-%H-%M", time.localtime()) + ".txt"
file_handler = FileHandler(filename=filename, mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
map_log.addHandler(file_handler)