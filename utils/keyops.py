import pyautogui
from utils.config import config

def get_mapping(x):
    if x in config.origin_key:
        x = config.mapping[config.origin_key.index(x)]
    return x

def keyDown(x):
    pyautogui.keyDown(get_mapping(x))
def keyUp(x):
    pyautogui.keyUp(get_mapping(x))