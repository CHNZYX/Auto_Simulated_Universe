import threading
import traceback
import keyboard
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32gui, win32api, win32con
import random
import sys
from copy import deepcopy
from utils.log import log, set_debug
from utils.map_log import map_log
from utils.update_map import update_map
from utils.utils import UniverseUtils, set_forground, notif
import os
from align_angle import main as align_angle
from utils.config import config
import datetime
import pytz
import yaml

pyautogui.FAILSAFE=False

class Abyss(UniverseUtils):
    def __init__(self):
        super().__init__()
        self.threshold = 0.97
        with open('abyss/info.yml', "r", encoding="utf-8",errors='ignore') as f:
            config = yaml.safe_load(f)['order_text']
            self.team=[config[:4],config[4:]]
        
    def start_abyss(self):
        while True:
            self.route()
            time.sleep(0.7)
    def route(self):
        self.get_screen()
        #self.click_target('imgs/abyss_5.jpg',0.9,True)
        if self.check("run", 0.9844, 0.7889, threshold=0.93):
            self.press('F4')
        elif self.check("abyss_5",0.1125,0.9389):
            self.click_text(["00"])
            pass
        elif self.check("abyss_4",0.7865,0.3028):
            self.click((0.2208,0.4296))
        elif self.check("abyss_3",0.7865,0.3028):
            self.click((0.7865,0.3028))
        elif self.check("abyss_2",0.4297,0.8213):
            self.drag((0.7750,0.3750),(0.7750,0.6750))
        elif self.check("abyss_1",0.8568,0.6769):
            self.click((0.6260,0.8167))

test = Abyss()
test.start_abyss()