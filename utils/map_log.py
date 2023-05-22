import os,time
from logging import getLogger, StreamHandler, FileHandler, Formatter, basicConfig, INFO, DEBUG, CRITICAL

map_log = getLogger('map_logger')
map_log.setLevel(INFO)
logging_format = "%(levelname)s %(message)s"

# 根据日期生成日志文件
filename = os.path.dirname(os.path.abspath(__file__))[:-5] + "\\logs\\log_" \
           + time.strftime("%Y-%m-%d_%H:%M", time.localtime()) + ".txt"
# 创建文件
if not os.path.exists(filename):
    open(filename, 'w').close()
file_handler = FileHandler(filename=filename, mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
map_log.addHandler(file_handler)