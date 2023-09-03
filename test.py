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
from utils.utils import UniverseUtils

pyautogui.FAILSAFE=False

su = UniverseUtils()
su.threshold = 0.97
su.get_screen()
su.check("z",0.5906,0.9537,mask="mask_z")