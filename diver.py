import threading
import traceback
import keyboard
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32gui, win32api, win32con
import random
import json
import sys
from copy import deepcopy
from utils.log import log, set_debug
from utils.log import my_print as print
from utils.log import print_exc
from utils.diver.args import args
from utils.diver.utils import UniverseUtils, set_forground, notif
import os
from align_angle import main as align_angle
from utils.diver.config import config
import datetime
import csv
import pytz
import pyuac
import utils.diver.keyops as keyops
from utils.diver.keyops import KeyController
import bisect
from collections import defaultdict

# 版本号
version = "v7.2"


class DivergentUniverse(UniverseUtils):
    def __init__(self, debug=0, nums=-1, speed=0):
        super().__init__()
        self._stop = True
        self.end = 0
        self.floor = 0
        self.allow_e = 1
        self.count = self.my_cnt = 0
        self.debug = debug
        self.nums = nums
        self.speed = speed
        self.init_tm = time.time()
        self.area_now = None
        self.action_history = []
        self.event_prior = self.read_csv("actions/event.csv", name='event')
        self.character_prior = self.read_csv("actions/character.csv", name='char')
        self.all_bless = self.read_csv("actions/bless.csv", name='bless')
        self.bless_prior = defaultdict(int)
        self.team_member = {}
        self.ocr_time_list = [0.5]
        self.fail_tm = 0
        self.quan = 0
        self.event_text = ''
        self.long_range = '1'
        self.init_floor()
        self.saved_num = 0
        self.default_json_path = "actions/default.json"
        self.default_json = self.load_actions(self.default_json_path)
        if config.weekly_mode:
            self.default_json['模式选择'][0]['actions'][1]['text'] = '周期演算'
        if debug != 2:
            pyautogui.FAILSAFE = False
        self.update_count()
        notif("开始运行", f"初始计数：{self.count}")
        set_debug(debug > 0)

    def route(self):
        self.threshold = 0.97
        while True:
            if self._stop:
                break
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
            warn_game = False
            cnt = 0
            while Text != "崩坏：星穹铁道" and Text != "云·星穹铁道" and not self._stop:
                self.lst_changed = time.time()
                if self._stop:
                    raise KeyboardInterrupt
                if not warn_game:
                    warn_game = True
                    log.warning(f"等待游戏窗口，当前窗口：{Text}")
                time.sleep(0.5)
                cnt += 1
                if cnt == 1200:
                    set_forground()
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
            if self._stop:
                break
            # self.click_target('imgs/divergent/sile.jpg',0.9,True) # 如果需要输出某张图片在游戏窗口中的坐标，可以用这个
            self.loop()
        log.info("停止运行")

    def loop(self):
        self.ts.forward(self.get_screen())
        # self.ts.find_with_box()
        # exit()
        res = self.run_static()
        if res == '':
            area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
            if '位面' in area_text or '区域' in area_text or '第' in area_text:
                self.area()
            elif self.check("c", 0.9417, 0.1204, threshold=0.965):
                self.press('v')
            else:
                text = self.merge_text(self.ts.find_with_box([400, 1920, 100, 600], redundancy=0))
                if self.speed and '转化' in text and '继续战斗' not in text and ('数据' in text or '过量' in text):
                    print('ready to stop')
                    time.sleep(6)
                    tm = time.time()
                    while time.time() - tm < 15:
                        print('trying to stop')
                        self.press('esc')
                        time.sleep(2)
                        self.ts.forward(self.get_screen())
                        static_res = self.run_static(action_list=['过量转化'])
                        if static_res != '':
                            print(static_res)
                            break
        if self.end and res == '加载界面':
            self.press('esc')
            time.sleep(2)
            self.press('esc')
            self._stop = True
        
    def do_action(self, action) -> int:
        if type(action) == str:
            return getattr(self, action)()
        if "text" in action:
            if "box" in action:
                box = action["box"]
            else:
                box = [0, 1920, 0, 1080]
            text = self.ts.find_with_box(box, redundancy=action.get("redundancy", 30))
            for i in text:
                if action["text"] in i["raw_text"]:
                    log.info(f"点击 {action['text']}:{i['box']}")
                    self.click_box(i["box"])
                    return 1
        elif "position" in action:
            log.info(f"点击 {action['position']}")
            self.click_position(action["position"])
            return 1
        elif "sleep" in action:
            time.sleep(float(action["sleep"]))
            return 1
        elif "press" in action:
            self.press(action["press"], action["time"] if "time" in action else 0)
            return 1
        return 0
    
    def load_actions(self, json_path):
        res = defaultdict(list)
        with open(json_path, "r", encoding="utf-8") as f:
            for i in json.load(f):
                res[i["name"]].append(i)
        return res

    def run_static(self, json_path=None, json_file=None, action_list=[], skip_check=0) -> str:
        if json_file is None:
            if json_path is None:
                json_file = self.default_json
            else:
                json_file = self.load_actions(json_path)
        for j in action_list if len(action_list) else json_file:
            for i in json_file[j]:
                trigger = i["trigger"]
                text = self.ts.find_with_box(trigger["box"], redundancy=trigger.get("redundancy", 30))
                if skip_check or (len(text) and trigger["text"] in self.merge_text(text)):
                    log.info(f"触发 {i['name']}:{trigger['text']}")
                    for j in i["actions"]:
                        self.do_action(j)
                    self.action_history.append(i["name"])
                    self.action_history = self.action_history[-10:]
                    return i['name']
        return ''
    
    def select_difficulty(self):
        time.sleep(0.5)
        self.click_position([125, 175+int((self.diffi-1)*(605-175)/4)])

    def read_csv(self, file_path, name):
        with open(file_path, mode='r', newline='', encoding='cp936') as file:
            reader = csv.reader(file)
            next(reader)
            if name == 'char':
                data = defaultdict(dict)
                for row in reader:
                    data[row[0]].update({white:int(row[3]) for white in row[1].replace('，',',').split(',')})
                    data[row[0]].update({black:-int(row[3]) for black in row[2].replace('，',',').split(',')})
            else:
                data = {row[0]:[s.replace('，',',') for s in row[1:]] for row in reader}
        return data

    def clean_text(self, text, char=1):
        symbols = r"[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~—“”‘’«»„…·¿¡£¥€©®™°±÷×¶§‰]，。！？；：（）【】「」《》、￥ "
        if char:
            symbols += r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        translator = str.maketrans('', '', symbols)
        return text.translate(translator)

    def merge_text(self, text, char=1):
        return self.clean_text(''.join([i['raw_text'] for i in self.ts.sort_text(text)]), char)
    
    def init_floor(self):
        self.portal_cnt = 0 
        self.area_state = 0
        self.event_solved = 0
        self.bless_solved = 0
        self.fail_cnt = 0
        self.now_event = ''
        if hasattr(self, 'keys'):
            self.keys.fff = 0
        for i in ['w','a','s','d','f']:
            keyops.keyUp(i)

    def save_or_exit(self):
        print('saved_num:', self.saved_num, 'save_cnt:', config.save_cnt)
        if self.saved_num < config.save_cnt:
            self.saved_num += 1
            self.click_position([1204, 959])
            time.sleep(1)
        else:
            self.click_position([716, 959])
        time.sleep(1.5)

    def select_save(self):
        self.click_position([186, 237 + int((self.saved_num-1) * (622 - 237) / 3)])
        time.sleep(1)
        self.ts.forward(self.get_screen())

    def close_and_exit(self, click=True):
        self.press('esc')
        if self.debug and self.floor < 13:
            with open('test.txt', 'a') as f:
                format_string = "%H:%M:%S"
                formatted_time = time.strftime(format_string, time.localtime())
                f.write(formatted_time + '\n')
            while 1:
                time.sleep(1)
        time.sleep(2.5)
        self.init_floor()
        if not click:
            if time.time() - self.fail_tm < 90:
                click = True
                self.fail_tm = 0
            else:
                self.fail_tm = time.time()
        if click:
            self.floor = 0
            self.click_position([1530, 990])
            time.sleep(1)

    def get_text_type(self, text, types, prefix=1):
        for i in types:
            if i[:prefix] in text:
                return i
        return None
    
    def find_team_member(self):
        boxes = [[1620, 1790, 289, 335],[1620, 1790, 384, 427],[1620, 1790, 478, 521],[1620, 1790, 570, 618]]
        team_member = {}
        for i,b in enumerate(boxes):
            name = self.clean_text(self.ts.ocr_one_row(self.get_screen(), b))
            if name in self.character_prior:
                team_member[name] = i
        return team_member

    def get_now_area(self, deep=0):
        team_member = self.find_team_member()
        self.area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
        print('area_text:', self.area_text, 'deep:', deep)
        if '位面' in self.area_text or '区域' in self.area_text or '第' in self.area_text:
            check_ok = 1
            for i in team_member:
                if i not in self.team_member or team_member[i] != self.team_member[i]:
                    check_ok = 0
                    break
            if not check_ok:
                self.team_member = team_member
                print('team_member:', team_member)
                for i in self.team_member:
                    if i in config.long_range_list:
                        self.long_range = str(self.team_member[i]+1)
                        break
            res = self.get_text_type(self.area_text, ['事件', '奖励', '遭遇', '商店', '首领', '战斗', '财富', '休整', '位面'])
            if (res == '位面' or res is None) and deep == 0:
                self.mouse_move(20)
                scr = self.screen
                time.sleep(0.3)
                self.get_screen()
                self.mouse_move(-20)
                res = self.get_now_area(deep=1)
                self.screen = scr
            return res
        else:
            return None
    
    def find_portal(self, type=None):
        prefer_portal = {'奖励':3, '事件':3, '战斗':2, '遭遇':2, '商店':1, '财富':1}
        if self.speed:
            prefer_portal = {'商店':3, '财富':3, '奖励':2, '事件':2, '战斗':1, '遭遇':1}
            if self.quan and self.allow_e:
                prefer_portal['战斗'] = 2
        if config.enable_portal_prior:
            prefer_portal.update(config.portal_prior)
        prefer_portal.update({'首领':4, '休整':4})
        tm = time.time()
        text = self.ts.find_with_box([0,1920,0,540], forward=1, mode=2)
        portal = {'score':0,'nums':0,'type':''}
        for i in text:
            if ('区' in i['raw_text'] or '域' in i['raw_text']) and (i['box'][0] > 400 or i['box'][2] > 60):
                portal_type = self.get_text_type(i['raw_text'], prefer_portal)
                if portal_type is not None:
                    i.update({'score':prefer_portal[portal_type]+10*(portal_type==type), 'type':portal_type, 'nums':portal['nums']+1})
                    if i['score'] > portal['score']:
                        portal = i
                elif '冒险' in i['raw_text']:
                    portal['nums'] += 1
        ocr_time = time.time() - tm
        self.ocr_time_list = self.ocr_time_list[-5:] + [ocr_time]
        print(f'识别时间:{int(ocr_time*1000)}ms', text, portal)
        return portal
    
    def sleep(self, tm=2):
        time.sleep(tm)
        
    def portal_bias(self, portal):
        return (portal['box'][0] + portal['box'][1]) // 2 - 950
    
    def aim_portal(self, portal):
        zero = bisect.bisect_left(config.angles, 0)
        # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(-200 * self.multi * self.scale))
        while abs(self.portal_bias(portal)) > 50:
            angle = bisect.bisect_left(config.angles, self.portal_bias(portal)) - zero
            self.mouse_move(angle)
            if abs(self.portal_bias(portal)) < 200:
                return portal
            time.sleep(0.2)
            portal_after = self.find_portal(portal['type'])
            if portal_after['score'] == 0:
                self.press('w', 1)
                portal_after = self.find_portal(portal['type'])
                if portal_after['score'] == 0:
                    return portal
            portal = portal_after
        return portal
    
    def forward_until(self, text_list=[], timeout=5, moving=0):
        tm = time.time()
        if not moving:
            keyops.keyDown('w')
        while time.time() - tm < timeout:
            self.get_screen()
            if self.check_f(check_text=0):
                keyops.keyUp('w')
                print(text_list)
                if self.check_f(is_in=text_list):
                    self.press('f')
                    for _ in range(1):
                        self.press('s',0.2)
                        self.press('f')
                    return 1
                else:
                    tm += 0.7
                    keyops.keyDown('w')
                    time.sleep(0.5)
        keyops.keyUp('w')
        return 0

    def portal_opening_days(self, aimed=0, static=0, deep=0):
        if deep > 1:
            self.close_and_exit(click = self.fail_count > 1)
            self.fail_count += 1
            return
        if deep == 0:
            self.portal_cnt += 1
        portal = {'score':0,'nums':0,'type':''}
        moving = 0
        if static:
            # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(100 * self.multi * self.scale))
            angles = [0, 90, 90, 90, 45, -90, -90, -90, -45]
            for i,angle in enumerate(angles):
                self.mouse_move(angle)
                time.sleep(0.2)
                portal = self.find_portal()
                if portal['score']:
                    break
            if self.floor in [1,2,4,5,6,7,9,10]:
                if portal['nums'] == 1 and portal['score'] < 2:
                    portal_pre = portal
                    portal_type = portal['type']
                    bias = 0
                    for i in range(i+1, len(angles)):
                        self.mouse_move(angles[i])
                        bias += angles[i]
                        time.sleep(0.2)
                        portal_after = self.find_portal()
                        if portal_after['score'] and portal_type != portal_after['type']:
                            portal = portal_after
                            break
                    if portal['type'] == portal_type:
                        portal = portal_pre
                        self.mouse_move(-bias)
        tm = time.time()
        while time.time() - tm < 5 + 2 * (portal['score'] != 0):
            if aimed == 0:
                if portal['score'] == 0:
                    portal = self.find_portal()
            else:
                if self.forward_until([portal['type']] if portal['score'] else ['区域','结束','退出'], timeout=3, moving=moving):
                    self.init_floor()
                    return
                else:
                    moving = 0
            if portal['score'] and not aimed:
                if moving:
                    print('stop moving')
                    keyops.keyUp('w')
                    moving = 0
                    self.press('s',min(max(self.ocr_time_list), 0.4))
                    continue
                else:
                    print('aiming...')
                    tmp_portal = self.aim_portal(portal)
                    if tmp_portal['score'] == 0:
                        self.portal_opening_days(aimed=0, static=1, deep=deep+1)
                        return
                    else:
                        portal = tmp_portal
                        aimed = 1
                    moving = 1
                    keyops.keyDown('w')
            elif portal['score'] == 0:
                if not moving:
                    keyops.keyDown('w')
                    moving = 1
        if moving:
            keyops.keyUp('w')

    def event_score(self, text, event):
        score = 0
        event_weight = [2*self.speed, 1, -10]
        for i in range(3):
            for e in event[i].split('-'):
                if e in text and len(e):
                    score += event_weight[i]
        return score

    def event(self):
        event_id = (-1, '')
        self.event_solved = 1
        tm = time.time()
        while time.time() - tm < 20:
            title_text = self.clean_text(self.ts.ocr_one_row(self.screen, [185, 820, 945, 1005]), char=0)
            print(title_text)
            if event_id[0] == -1:
                for i, e in enumerate(self.event_prior):
                    if e in title_text and len(e) > len(event_id[1]):
                        event_id = (i, e)
                start = self.now_event == event_id[1]
                self.now_event = event_id[1]
                print('event_id:', event_id)
            if '事件' not in self.merge_text(self.ts.find_with_box([92, 195, 54, 88])):
                return
            
            self.get_screen()
            if self.check("arrow", 0.1828, 0.5000, mask="mask_event"):
                self.click((self.tx, self.ty))
            # 事件界面：退出
            elif self.check("arrow_1", 0.1828, 0.5000, mask="mask_event"):
                self.click((self.tx, self.ty))
            # 事件选择界面
            elif self.check("star", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
                if self.debug and event_id[0] == -1:
                    print(self.ts.res)
                    while 1:
                        time.sleep(1)
                tx, ty = self.tx, self.ty
                self.ts.forward(self.screen)
                clicked = 0
                if event_id[0] != -1:
                    text = self.ts.find_with_box([1300, 1920, 100, 1080], redundancy=30)
                    events = []
                    event_now = None
                    last_star = 0
                    for i in text:
                        if self.check_box("star", [1250, 1460, i['box'][2]-30, i['box'][3]+30]) and last_star<self.ty-20:
                            last_star = self.ty
                            if event_now is not None:
                                events.append(event_now)
                            event_now = {'raw_text': i['raw_text'].lstrip('米'), 'box': i['box']}
                        else:
                            if event_now is not None:
                                event_now['raw_text'] += i['raw_text']
                            else:
                                event_now = {'raw_text': i['raw_text'], 'box': i['box']}
                    events.append(event_now)
                    for e in events:
                        e['raw_text'] = self.clean_text(e['raw_text'], 0)
                        e['score'] = self.event_score(e['raw_text'], self.event_prior[event_id[1]])
                    events = sorted(events, key=lambda x: x['score'], reverse=True)
                    print([{k: v for k, v in event.items() if k != 'box'} for event in events])
                    for i in events:
                        self.click_box(i['box'])
                        time.sleep(0.4)
                        self.get_screen()
                        if self.check("confirm", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
                            self.click((self.tx, self.ty))
                            clicked = 1
                            break
                if not clicked:
                    self.click((tx, ty))
                    time.sleep(0.3)
                    self.click((0.1167, ty - 0.4685 + 0.3546))
                time.sleep(0.8)
                start = 0
            else:
                if not start:
                    time.sleep(0.6)
                    self.ts.forward(self.get_screen())
                    if '事件' not in self.merge_text(self.ts.find_with_box([92, 195, 54, 88])):
                        return
                self.click((0.9479, 0.9565))
                self.click((0.9479, 0.9565))
                if start:
                    self.click((0.9479, 0.9565))
                    self.click((0.9479, 0.9565))
                self.ts.forward(self.get_screen())

    def find_event_text(self, save=0):
        time.sleep(0.3)
        text = self.ts.find_with_box([300, 1920, 0, 350], forward=1, mode=2)
        res = 0
        event_text = ''
        debug_res = []
        print('event_text:', text)
        for i in text:
            box = i['box']
            if 'ms' in i['raw_text'] or '状态效' in i['raw_text'] or len(i['raw_text']) < 2 or (box[0] > 1470 and box[2] < 75)\
                  or (box[0] > 1800 and box[2] < 120) or (box[0] > 1600 and box[2] > 290) or (box[1] < 400 and box[3] < 160):
                continue
            if '?' not in i['raw_text'] and '？' not in i['raw_text'] and len(self.clean_text(i['raw_text'], 1)) == 0:
                continue
            w, h = box[1] - box[0], box[3] - box[2]
            if w < 40 or h > 40:
                continue
            if (box[0] + box[1]) // 2 > res or self.event_text in i['raw_text'] or i['raw_text'] in self.event_text:
                res = (box[0] + box[1]) // 2
                event_text = i['raw_text']
            debug_res.append(i)
        print(debug_res, res, event_text)
        if save:
            self.event_text = event_text
        return res
    
    def align_event(self, key, deep=0):
        find = 0
        if deep == 0 and key == 'd':
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(-200 * self.multi * self.scale))
            event_text = self.find_event_text(1)
            if not event_text:
                self.press('s', 1)
            else:
                find = 1
        if not find:
            event_text = self.find_event_text(1)
        self.get_screen()
        if self.check_f(is_in=['事件','奖励','遭遇','交易']):
            self.press('f')
            return
        # elif self.check_f(is_in=['混沌','药箱']):
        #     self.press('f')
        #     time.sleep(2.5)
        #     self.run_static(action_list=['混沌药箱'], skip_check=1)
        #     tm = time.time()
        #     while time.time() - tm < 3:
        #         self.ts.forward(self.get_screen())
        #         res = self.run_static(action_list=['点击空白处关闭'])
        #         if len(res):
        #             tm = time.time()
        #     time.sleep(2)
        #     if deep == 0:
        #         self.align_event(key, deep+1)
        #     return

        if not event_text and key == 'a':
            event_text = 950

        if event_text:
            if abs(event_text - 950) > 40:
                self.press(key,0.2)
                event_text_after = self.find_event_text()
                if event_text_after:
                    sub = event_text - event_text_after
                    if key == 'a':
                        sub = -sub
                    print('sub:', sub)
                    if sub < 60:
                        sub = 100
                    if sub < 200:
                        sub = int((event_text_after - 950) / min(150, sub))
                        sub = min(5, max(-5, int(sub)))
                        for _ in range(sub):
                            self.press('d',0.2)
                            time.sleep(0.1)
                        for _ in range(-sub):
                            self.press('a',0.2)
                            time.sleep(0.1)
                else:
                    self.press('a' if key == 'd' else 'd', 0.2)
            self.forward_until(['事件','奖励','遭遇','交易'], timeout=2.5, moving=0)
        else:
            if deep < 3:
                self.press('w',[0,0.3,0.5][deep])
                self.align_event(key, deep+1)
            return
            
    def skill(self, quan=0):
        if not self.allow_e:
            return
        self.press('e')
        time.sleep(0.5)
        self.get_screen()
        if self.check('e',0.4995,0.7500):
            self.solve_snack()
            if quan and self.allow_e:
                time.sleep(0.5)
            else:
                time.sleep(1.5*self.allow_e)

    def check_dead(self):
        self.get_screen()
        if self.check("divergent/sile", 0.5010,0.7519, threshold=0.96):
            self.click_position([1188, 813])
            time.sleep(2.5)

    def area(self):
        area_now = self.get_now_area()
        time.sleep(0.5)
        if self.get_now_area() != area_now or area_now is None:
            return
        if self.area_state == -1:
            self.close_and_exit(click = False)
            return
        now_floor = self.floor
        for i in range(1,14):
            if f'{i}13' in self.area_text:
                now_floor = i
        if now_floor != self.floor:
            if now_floor < self.floor:
                self.init_floor()
            self.floor = now_floor
            if self.floor in [5,10]:
                time.sleep(3)
        time.sleep(0.8)
        if self.area_state == 0:
            if '黄泉' in self.team_member and '黄泉' in config.skill_char:
                self.quan = 1
            if area_now == '战斗' and self.quan and self.allow_e:
                self.press(str(self.team_member['黄泉']+1))
            else:
                self.press(self.long_range)
        self.get_screen()
        if self.check("divergent/arrow", 0.7833,0.9231, threshold=0.96):
            keyops.keyDown('alt')
            time.sleep(0.2)
            self.click_position([413, 79])
            keyops.keyUp('alt')
        time.sleep(0.7)
        self.check_dead()
        if area_now is not None:
            self.area_now = area_now
        else:
            area_now = self.area_now
        if self.portal_cnt > 1:
            self.close_and_exit(click = False)
            return
        print('floor:',self.floor,'state:',self.area_state,'area:',area_now,'text:',self.area_text)
        if area_now in ['事件', '奖励', '遭遇']:
            if self.area_state==0:
                keyops.keyDown('w')
                time.sleep(2.2)
                keyops.keyDown('d')
                time.sleep(0.4)
                keyops.keyUp('w')
                time.sleep(0.2)
                keyops.keyUp('d')
                time.sleep(0.2)
                self.align_event('a')
                self.area_state += 1
            elif self.area_state==1:
                self.keys.fff = 1
                self.press('a', 1.3)
                time.sleep(0.4)
                self.keys.fff = 0
                self.get_screen()
                if self.get_now_area() is not None:
                    self.press('w', 0.3)
                    time.sleep(0.6)
                    self.get_screen()
                    if self.check_f(check_text=0):
                        self.press('f')
                    else:
                        self.press('s', 0.5)
                        self.align_event('d')
                self.area_state += 1
            else:
                self.portal_opening_days(static=1)
        elif area_now == '休整':
            pyautogui.click()
            time.sleep(0.8)
            keyops.keyDown('w')
            self.press('a', 0.3)
            time.sleep(3)
            self.press('d', 0.2)
            keyops.keyUp('w')
            time.sleep(0.25)
            self.portal_opening_days(aimed=1)
        elif area_now == '商店':
            pyautogui.click()
            time.sleep(0.8)
            keyops.keyDown('w')
            time.sleep(1.6)
            self.press('d',0.4)
            keyops.keyUp('w')
            time.sleep(0.6)
            self.portal_opening_days(static=1)
        elif area_now == '首领':
            if self.floor == 13 and self.area_state > 0:
                self.close_and_exit()
                self.end_of_uni()
                return
            if self.area_state == 0:
                self.press('w',3)
                for c in config.skill_char:
                    if (c in self.team_member or c.isdigit()) and self.allow_e:
                        self.press(int(c) if c.isdigit() else str(self.team_member[c]+1))
                        time.sleep(0.8)
                        self.check_dead()
                        self.skill()
                        time.sleep(1.5)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.click()
                self.area_state += 1
            elif self.area_state == 1:
                if self.bless_solved:
                    if not self.speed:
                        keyops.keyDown('w')
                        tm = time.time()
                        while time.time() - tm < 1.8:
                            self.get_screen()
                            if self.check_f(check_text=0):
                                break
                        keyops.keyUp('w')
                        self.press('f')
                        self.area_state += 1
                    else:
                        self.press('w', 1)
                        self.press('f')
                        self.area_state = 5
                else:
                    self.press('w', 0.5)
                    self.area_state = 4
            elif self.area_state == 2:
                self.press('d', 0.55)
                self.press('f')
                self.area_state += 1
            elif self.area_state == 3:
                self.press('a', 0.95)
                self.press('f')
                self.area_state += 1
            elif self.area_state == 4:
                if self.bless_solved:
                    keyops.keyDown('d')
                    self.press('s', 0.2)
                    time.sleep(0.2)
                    keyops.keyUp('d')
                    self.portal_opening_days(static=1)
                else:
                    self.portal_opening_days(static=1)
            else:
                time.sleep(1)
                self.portal_opening_days(static=1)
        elif area_now == '战斗':
            if self.area_state == 0:
                self.press('w', 3)
                if self.quan and self.allow_e and self.floor > 1:
                    for _ in range(4):
                        self.skill(1)
                    self.press('w')
                    time.sleep(1.5)
                else:
                    pyautogui.click()
                self.area_state += 1
            else:
                self.press('w', 0.5)
                self.portal_opening_days(static=1)
        elif area_now == '财富':
            self.press('w',2.7)
            pyautogui.click()
            time.sleep(0.6)
            keyops.keyDown('w')
            time.sleep(0.2)
            self.keys.fff = 1
            self.press('a', 0.5)
            time.sleep(0.35)
            keyops.keyUp('w')
            time.sleep(0.6)
            if self.find_portal()['score'] == 0:
                self.press('a', 0.4)
                self.press('s', 0.7)
                self.press('w', 0.5)
            self.keys.fff = 0
            self.portal_opening_days(static=1)
        elif area_now == '位面':
            pyautogui.click()
            time.sleep(2)
            self.close_and_exit()
        else:
            self.press('F4')
    
    def update_bless_prior(self):
        self.bless_prior = defaultdict(int)
        for i in list(self.team_member) + ['全局', config.team]:
            if i in self.character_prior:
                prior = self.character_prior[i]
                for j in prior:
                    self.bless_prior[j] += prior[j]
    
    def bless_score(self, text):
        score = 0
        for i in self.bless_prior:
            if i in text:
                score += self.bless_prior[i]
        for i in self.all_bless:
            if i[-4:] in text:
                score += int(self.all_bless[i][0]) - 1
        return score

    def drop_bless(self):
        self.bless(0)

    def bless(self, reverse=1):
        self.bless_solved = 1
        text = self.ts.find_with_box([350, 1550, 795, 819])
        if len(text) == 0:
            text = self.ts.find_with_box([350, 1550, 480, 530])
        if len(text) == 0:
            return
        self.update_bless_prior()
        blesses = []
        for i in text:
            box = i["box"]
            x, y = (box[0] + box[1]) // 2, (box[2] + box[3]) // 2
            box = [x - 220, x + 220, 450, 850]
            bless_text = self.ts.find_with_box(box)
            bless_raw_text = self.merge_text(bless_text, char=0)
            blesses.append({'raw_text': bless_raw_text, 'box': box, 'score': self.bless_score(bless_raw_text)})
        blesses = sorted(blesses, key=lambda x: x['score'], reverse=reverse)
        print(blesses)
        box = blesses[0]['box']
        for _ in range(1):
            self.click_position([(box[0] + box[1]) // 2, 500])
        self.click_position([1695, 962])
        time.sleep(1)

    def end_of_uni(self):
        self.update_count(0)
        self.my_cnt += 1
        tm = int((time.time() - self.init_tm) / 60)
        remain_round = self.nums-self.my_cnt
        if remain_round > 0:
            remain = int(remain_round * (time.time() - self.init_tm) / self.my_cnt / 60)
        else:
            remain = 0
            remain_round = -1
        notif(
            "已完成",
            f"计数:{self.count} 剩余:{remain_round} 已使用：{tm//60}小时{tm%60}分钟  平均{tm//self.my_cnt}分钟一次  预计剩余{remain//60}小时{remain%60}分钟",
            cnt=str(self.count),
        )
        if self.nums <= self.my_cnt and self.nums >= 0:
            log.info('已完成上限，准备停止运行')
            self.end = 1
        self.floor = 0
        self.init_floor()

    def update_count(self, read=True):
        file_name = "logs/notif.txt"
        if read:
            new_cnt = 0
            if os.path.exists(file_name):
                time_cnt = os.path.getmtime(file_name)
                with open(file_name, "r", encoding="utf-8", errors="ignore") as fh:
                    s = fh.readlines()
                    try:
                        new_cnt = int(s[0].strip("\n"))
                        time_cnt = float(s[3].strip("\n"))
                    except:
                        pass
            else:
                os.makedirs("logs", exist_ok=1)
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write("0")
                    file.close()
                time_cnt = os.path.getmtime(file_name)
        else:
            new_cnt = self.count + 1
            time_cnt = self.count_tm
        dt = datetime.datetime.now().astimezone()
        """
        America: GMT-5
        Asia: GMT+8
        Europe: GMT+1
        TW, HK, MO: GMT+8
        """
        tz_info = None
        try:
            tz_dict = {
                "Default": None,
                "America": pytz.timezone("US/Central"),
                "Asia": pytz.timezone("Asia/Shanghai"),
                "Europe": pytz.timezone("Europe/London"),
            }
            tz_info = tz_dict[config.timezone]
        except:
            pass

        # convert to server time
        dt = dt.astimezone(tz_info)
        current_weekday = dt.weekday()
        monday = dt + datetime.timedelta(days=-current_weekday)
        target_datetime = datetime.datetime(
            monday.year, monday.month, monday.day, 4, 0, 0, tzinfo=tz_info
        )
        monday_ts = target_datetime.timestamp()
        if dt.timestamp() >= monday_ts and time_cnt < monday_ts:
            self.count = int(not read)
        else:
            self.count = new_cnt
        self.count_tm = time.time()

    def stop(self, *_, **__):
        log.info("尝试停止运行")
        try:
            self.init_floor()
        except:
            pass
        self._stop = True
    
    def on_key_press(self, event):
        if event.name == "f8":
            print("F8 已被按下，尝试停止运行")
            self.stop()

    def start(self):
        self._stop = False
        keyboard.on_press(self.on_key_press)
        self.keys = KeyController(self)
        try:
            self.route()
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            try:
                log.info('用户终止进程')
            except:
                pass
            if not self._stop:
                self.stop()
        except Exception as e:
            print_exc()
            traceback.print_exc()
            log.info(str(e))
            log.info("发生错误，尝试停止运行")
            self.stop()

def main():
    log.info(f"debug: {args.debug}")
    su = DivergentUniverse(args.debug, args.nums, args.speed)
    try:
        su.start()
    # except ValueError as e:
    #     pass
    except Exception:
        print_exc()
    finally:
        su.stop()


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()
