from logging import getLogger, StreamHandler, FileHandler, Formatter, basicConfig, INFO, DEBUG, CRITICAL

log = getLogger()
logging_format = "%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s"
logging_handler = StreamHandler()
logging_handler.setFormatter(Formatter(logging_format))
file_handler = FileHandler(filename="log.txt", mode="w", encoding="utf-8")
file_handler.setFormatter(Formatter(logging_format))
flet = getLogger("flet")
flet.setLevel(CRITICAL)
flet_core = getLogger("flet_core")
flet_core.setLevel(CRITICAL)
log.addHandler(logging_handler)
log.addHandler(file_handler)
basicConfig(level=INFO)


def set_debug(debug: bool = False):
    log.setLevel(DEBUG if debug else INFO)


set_debug()
