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
        self.floor = 0
        with open('abyss/info.yml', "r", encoding="utf-8",errors='ignore') as f:
            config = yaml.safe_load(f)['order_text']
            self.team=[config[:4],config[4:]]
        
    def start_abyss(self):
        while True:
            self.route()
            time.sleep(0.7)
    def wait(self):
        tm = time.time()
        while True:
            self.get_screen()
            if self.check("auto_2", 0.3755,0.0333):
                tm = time.time()
            if self.check("c", 0.9464,0.1287, threshold=0.985):
                #self.press('v')
                pass
            if time.time() - tm > 10 or self.check("abyss/in",0.9130,0.6074):
                print(time.time() - tm)
                break
            time.sleep(0.15)
    def ready(self):
        for i in range(4):
            self.press(str(i+1))
            time.sleep(0.4)
            self.press('e')
            time.sleep(1)
            self.get_screen()
            if not self.check("z",0.5010,0.9426,mask="abyss/mask_z") or self.check("abyss/z",0.5010,0.9426,mask="abyss/mask_z"):
                break
        time.sleep(1)
        pyautogui.click()
        time.sleep(3.5)
    def route(self):
        self.get_screen()
        #self.click_target('imgs/abyss/fail.jpg',0.9,True)
        if self.check("run", 0.9844, 0.7889, threshold=0.93):
            self.press('F4')
        elif self.check("abyss/fail",0.5995,0.1343):
            self.click((0.5995,0.1343))
        elif self.check("abyss/in",0.9130,0.6074):
            self.press('w',3.5)
            t = self.move_to_interac(1,1)
            self.press('w',1)
            self.ready()
            self.wait()
            if abs(t)<=30:
                time.sleep(1)
                self.press('w')
                self.move_to_interac(1,1)
                self.press('w',1)
                self.ready()
                self.wait()
        elif self.check("abyss/team",0.6500,0.4019):
            if self.check("abyss/begin",0.1062,0.0815):
                self.click((0.1062,0.0806))
                return
            if random.randint(0,1):
                self.team=self.team[::-1]
            for i,j in enumerate([(0.4026,0.3259),(0.4010,0.2343)]):
                self.click(j)
                time.sleep(0.2)
                for k in self.team[i]:
                    t=k-1
                    self.click((0.9427-0.0661*(t%4),0.8102-0.1435*(t//4)))
                    time.sleep(0.2)
            self.click((0.1062,0.0806))
        elif self.check("abyss/6",0.5661,0.5713):
            self.click((0.5,0.2))
        elif self.check("abyss/5",0.1125,0.9389):
            self.click((0.9,0.9))
            time.sleep(0.3)
            self.get_screen()
            gray = [156,122,126]
            gray2 = [118,107,111]
            bw_map = np.zeros(self.screen.shape[:2], dtype=np.uint8)
            bw_map[np.sum((self.screen - gray) ** 2, axis=-1) <= 800]=255
            bw_map[np.sum((self.screen - gray2) ** 2, axis=-1) <= 800]=255
            #cv.imwrite('tp.jpg',bw_map)
            res = (-1,-1)
            for i in ['3_stars','2_stars','1_star']:
                target = cv.imread(self.format_path('abyss/'+i),cv.IMREAD_GRAYSCALE)
                result = cv.matchTemplate(bw_map, target, cv.TM_CCORR_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                print(max_val)
                if max_val>0.88:
                    res = max_loc
                    break
            if res!=(-1,-1):
                self.click((1-res[0]/self.xx+0.06,1-res[1]/self.yy+0.02))
            else:
                self.drag((0.5,0.5),(0.8-0.6*random.randint(0,1),0.5))
        elif self.check("abyss/4",0.7865,0.3028):
            self.click((0.2208,0.4296))
        elif self.check("abyss/3",0.7865,0.3028):
            self.click((0.7865,0.3028))
        elif self.check("abyss/2",0.4297,0.8213):
            self.drag((0.7750,0.3750),(0.7750,0.6750))
        elif self.check("abyss/1",0.8568,0.6769):
            self.click((0.6260,0.8167))
        else:
            self.click((0.5,0.14))
            time.sleep(1)

test = Abyss()
test.start_abyss()