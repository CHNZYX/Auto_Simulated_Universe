import logging
import io
import traceback
from logging import (
    getLogger,
    StreamHandler,
    FileHandler,
    Formatter,
    basicConfig,
    INFO,
    DEBUG,
    CRITICAL,
)
from pathlib import Path
from datetime import datetime

logs_path = Path("logs")
logs_path.mkdir(exist_ok=True, parents=True)

current_time_str = datetime.now().strftime("%Y-%m-%d-%H-%M")

log = getLogger()
log.setLevel(INFO)

logging_format = "%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s"
formatter = Formatter(logging_format)

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = FileHandler(filename=logs_path / "log.txt", mode="w", encoding="utf-8")
file_handler.setFormatter(formatter)

timestamped_file_handler = FileHandler(filename=logs_path / f"log_{current_time_str}.txt", mode="w", encoding="utf-8")
timestamped_file_handler.setFormatter(formatter)

log.addHandler(stream_handler)
log.addHandler(file_handler)
log.addHandler(timestamped_file_handler)

flet = getLogger("flet")
flet.setLevel(CRITICAL)
flet_core = getLogger("flet_core")
flet_core.setLevel(CRITICAL)

basicConfig(level=INFO)

def set_debug(debug: bool = False):
    log.setLevel(DEBUG if debug else INFO)

set_debug()

def my_print(*args, **kwargs):
    log.info(" ".join(map(str, args)))
    if len(kwargs):
        print(*args, **kwargs)

def print_exc():
    with io.StringIO() as buf, open("logs/error_log.txt", "a") as f:
        traceback.print_exc(file=buf)
        f.write(buf.getvalue())