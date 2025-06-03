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
version = "v8.042"


class DivergentUniverse(UniverseUtils):
    def __init__(self, debug=0, nums=-1, speed=0):
        super().__init__()
        self.is_get_team = True #首次进入差分宇宙后,获取队伍成员
        self.team_detect = {} #队伍成员检测

        self._stop = True
        self.end = 0
        self.floor = 0

        # 允许使用秘技,秘技消耗品不足的时候就用不了
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
        self.last_action_time = 0
        self.total_empty_saves = 1

        # 对黄泉角色的优化,判断是否需要使用黄泉角色
        self.quan = 0 

        # 对大黑塔角色的优化,判断是否需要使用大黑塔角色,同时存在大黑塔和黄泉时,优先使用大黑塔,或许后面可以考虑自定义优先级
        self.da_hei_ta = False
        self.da_hei_ta_effecting = False # 秘技生效中,进战清除

        self.event_text = ''

        self.long_range = '1' # 默认角色 选用1号位

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
        self.is_get_team = True #启动后重置状态
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
            # self.click_target('imgs/zz.jpg',0.9,True) # 如果需要输出某张图片在游戏窗口中的坐标，可以用这个
            self.loop()
        log.info("停止运行")

    def loop(self):
        self.ts.forward(self.get_screen())
        # self.ts.find_with_box()
        # exit()
        res = self.run_static()
        # self.click_target("imgs/c.jpg", threshold=0.9, flag=False)
        if res == '':
            area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
            if '位面' in area_text or '区域' in area_text or '第' in area_text:
                self.area()
                self.last_action_time = time.time()

            elif self.check("c", 0.988, 0.1028, threshold=0.925):
                # 未检查到自动战斗,已经入站,清除秘技持续
                self.da_hei_ta_effecting = False
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
                else:
                    if time.time() - self.last_action_time > 60:
                        self.click((0.5, 0.1))
                        self.click((0.5, 0.25))
                        self.last_action_time = time.time()
        else:
            self.last_action_time = time.time()
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
            self.sleep(float(action["sleep"]))
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
        if self.saved_num < self.total_empty_saves:
            time.sleep(1.5)
            self.saved_num += 1
            self.click_position([1204, 959])
            time.sleep(1)
        else:
            self.click_position([716, 959])
        self.click_position([716, 959])
        time.sleep(1.5)

    def select_save(self):
        # self.click_position([186, 237 + int((self.saved_num-1) * (622 - 237) / 3)])
        time.sleep(0.5)
        self.ts.forward(self.get_screen())
        txt = self.merge_text(self.ts.find_with_box([0, 1920, 0, 1080], redundancy=0))
        empty_saves = len(txt.split('无存档')) - 1
        if self.total_empty_saves == 1:
            self.total_empty_saves = empty_saves

    def close_and_exit(self, click=True):
        self.press('esc')
        if self.debug and self.floor < 13:
            with open('test.txt', 'a') as f:
                format_string = "%H:%M:%S"
                formatted_time = time.strftime(format_string, time.localtime())
                f.write(formatted_time + '\n')
        time.sleep(2.5)
        self.init_floor()
        if not click:
            if time.time() - self.fail_tm < 90:
                click = True
                self.fail_tm = 0
                if self.debug:
                    exit()
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
    
    def test(self):
        self.find_team_member()


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

                    # 从当前队伍中,选取处于内置远程角色列表中的第一个远程角色
                    if i in config.long_range_list:
                        self.long_range = str(self.team_member[i]+1) # 更新默认远程角色
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
                if '冒' in i['raw_text'] or '险' in i['raw_text']:
                    portal['nums'] += 1
                elif portal_type is not None:
                    i.update({'score':prefer_portal[portal_type]+10*(portal_type==type), 'type':portal_type, 'nums':portal['nums']+1})
                    if i['score'] > portal['score']:
                        portal = i
                    else:
                        portal['nums'] = i['nums']
        ocr_time = time.time() - tm
        self.ocr_time_list = self.ocr_time_list[-5:] + [ocr_time]
        print(f'识别时间:{int(ocr_time*1000)}ms', text, portal)
        return portal
    
    def sleep(self, tm=2):
        time.sleep(tm)
        self.ts.forward(self.get_screen())
        
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
    
    def forward_until(self, text_list=[], timeout=5, moving=0, chaos=0):
        tm = time.time()
        if not moving:
            keyops.keyDown('w')
        while time.time() - tm < timeout:
            self.get_screen()
            if self.check_f(check_text=0):
                keyops.keyUp('w')
                print(text_list)
                if chaos:
                    if self.check_f(is_in=['混沌', '战利品']):
                        self.press('f')
                        for _ in range(1):
                            self.press('s',0.2)
                            self.press('f')
                        time.sleep(0.8)
                        tmm = time.time()
                        while time.time() - tmm < 8:
                            self.ts.forward(self.get_screen())
                            area_text = self.clean_text(self.ts.ocr_one_row(self.screen, [50, 350, 3, 35]), char=0)
                            if '位面' in area_text or '区域' in area_text or '第' in area_text:
                                break
                            self.run_static()
                        time.sleep(0.6)
                        tm = time.time()
                        keyops.keyDown('w')
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

    # 这个方法是通过本层么?
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
                if self.forward_until([portal['type']] if portal['score'] else ['区域','结束','退出'], timeout=2.5, moving=moving):
                    self.init_floor()
                    return
                else:
                    keyops.keyUp('w')
                    moving = 0
                    self.press('d', 0.6)
                    self.portal_opening_days(aimed=0, static=1, deep=deep+1)
                    return
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
                log.info(f"event:{event_id},start:{start}")
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
                    with open('test.txt', 'a') as f:
                        format_string = "%H:%M:%S"
                        formatted_time = time.strftime(format_string, time.localtime())
                        f.write(formatted_time + ' new event' + '\n')
                    # while 1:
                    #     time.sleep(1)
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
                    time.sleep(0.4)
                    if self.check("confirm", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
                        self.click((self.tx, self.ty))
                    else:
                        self.click((0.1167, ty - 0.4685 + 0.3546 + 0.02))
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
        self.get_screen()
        res = self.get_text_position(clean=1)
        res = sorted(res, key=lambda x: x[0])
        if len(res):
            return res[-1][0]
        else:
            return 0
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
            if w < 40 or h > 45:
                continue
            if (box[0] + box[1]) // 2 > res or self.event_text in i['raw_text'] or i['raw_text'] in self.event_text:
                res = (box[0] + box[1]) // 2
                event_text = i['raw_text']
            debug_res.append(i)
        if self.debug:
            print(debug_res, res, event_text)
        if res == 0:
            scr = np.copy(self.screen)
            mask = np.zeros(scr.shape[:2], dtype=np.uint8)
            mask[np.sum((scr - np.array([255, 255, 255])) ** 2, axis=-1) <= 400] = 255
            kernel = np.ones((20, 6), np.uint8)
            mask = cv.dilate(mask, kernel, iterations=2)
            contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, rect_w, rect_h = cv.boundingRect(contour)
                box = [x, x + rect_w, y, y + rect_h]
                if rect_w < 90 or rect_h > 70 or box[0] < 400 or box[1] > 1470:
                    continue
                if abs(res - 950) > abs((box[0] + box[1]) // 2 - 950):
                    res = (box[0] + box[1]) // 2
        if save:
            self.event_text = event_text
        return res
    
    def check_pop(self):
        in_time = time.time()
        while True:
            time.sleep(0.5)
            self.ts.forward(self.get_screen())
            if self.get_now_area() is not None:
                break
            if self.run_static(action_list=['点击空白处关闭']):
                time.sleep(0.3)
            elif time.time() - in_time > 3:
                break
    
    def align_event(self, key, deep=0, event_text=None, click=0):
        find = 0
        if deep == 0 and key == 'd' and (event_text is None or event_text != 950):
            # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(-200 * self.multi * self.scale))
            event_text = self.find_event_text(1)
            if not event_text:
                self.press('s', 1)
            else:
                find = 1
        if not find and not event_text:
            event_text = self.find_event_text(1)
        self.get_screen()
        if self.check_f(is_in=['事件','奖励','遭遇','交易']):
            self.press('f')
            return

        if not event_text:
            event_text = 950
        if event_text and event_text < 910 and key == 'd':
            key = 'a'

        log.info(f"align_event: {event_text}, key: {key}")

        if event_text:
            if abs(950-event_text) >= 50:
                self.press(key,0.2)
            event_text_after = self.find_event_text()
            if event_text_after:
                sub = event_text - event_text_after
                if key == 'a':
                    sub = -sub
                print('sub:', sub)
                log.info(f"event_text_after: {event_text_after}, sub: {sub}")
            else:
                sub = 100000

            if sub < 60:
                sub = 100

            if sub < 400:
                sub = int((event_text_after - 950) / sub)
                sub = min(3, max(-3, int(sub)))
            else:
                sub = 2

            if abs(950-event_text) < 50:
                sub = 0

            for _ in range(sub):
                self.press('d',0.2)
                time.sleep(0.1)

            for _ in range(-sub):
                self.press('a',0.2)
                time.sleep(0.1)

            if click:
                pyautogui.click()
                self.check_pop()

            self.forward_until(['事件','奖励','遭遇','交易'], timeout=2.5, moving=0, chaos=1)

        else:
            if deep < 3:
                self.press('w',[0,0.3,0.5][deep])
                self.align_event(key, deep+1)
            return
            
    def skill(self, quan=0):
        if not self.allow_e:
            return
        self.press('e')
        time.sleep(0.4)
        self.get_screen()
        if self.check('e',0.4995,0.7500):
            self.solve_snack()
            if quan and self.allow_e:
                time.sleep(0.4)
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
            return 0
        if self.area_state == -1:
            self.close_and_exit(click = False)
            return 1
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
            # 判断队伍成员状态
            da_hei_ta_in_team = '大黑塔' in self.team_member
            huang_quan_in_team = '黄泉' in self.team_member

            # 判断秘技状态
            da_hei_ta_has_skill = '大黑塔' in config.skill_char
            huang_quan_has_skill = '黄泉' in config.skill_char            

            # 优先级: 大黑塔 -> 黄泉 -> 远程角色
            if da_hei_ta_in_team and da_hei_ta_has_skill:
                # 使用大黑塔
                self.da_hei_ta = True

            elif huang_quan_in_team and huang_quan_has_skill:
                # 使用黄泉
                self.quan = 1

            else:
                # 使用远程角色
                self.da_hei_ta = False
                self.quan = 0

            # 决策站场角色
            # 大黑塔:通用  黄泉:战斗

            if self.allow_e:

                # 存在大黑塔时,直接使用大黑塔作为站场角色
                if self.da_hei_ta:
                    self.press(str(self.team_member['大黑塔']+1))

                elif self.quan and area_now == '战斗':
                    # 无大黑塔,那就切黄泉
                    self.press(str(self.team_member['黄泉']+1))
                else:
                    # 切远程角色
                    self.press(self.long_range)
            
            else:
                # 无秘技,切远程角色
                self.press(self.long_range)

        self.get_screen()
        if self.check("divergent/arrow", 0.7833,0.9231, threshold=0.95):
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
            # 这里考虑的是全局异常暂离次数达到2次,就结束本次探索,或许可以考虑改为单个区域
            self.close_and_exit(click = False)
            return 1
        
        log.info(f"floor:{self.floor}, state:{self.area_state}, area:{area_now}, text:{self.area_text}")

        if area_now in ['事件', '奖励', '遭遇']:
            # 如果存在大黑塔,还是切过来,毕竟这些事件都可能入战
            if self.da_hei_ta and self.allow_e and not self.da_hei_ta_effecting:
                self.skill()
                self.da_hei_ta_effecting = True

            # 这些层都可能存在单或者双的情况,同时还可能存在宝箱,抽奖机,后面再考虑
            # 单的情况,事件在最中间,双的情况,分为两边,而且事件距离人物的距离也不一致
            # 基本思想是前进,监视中间区域出现汉字,确定事件数量,分为单和双逻辑进行寻路
            # 如果是单事件,一直前进,然后寻找F
            # 如果是双事件,优先右侧事件,然后再左侧事件


            if self.area_state==0:
                keyops.keyDown('w')
                tm = time.time()
                self.get_screen()
                self.get_text_position()
                total_events = None

                while time.time() - tm < 15:
                    self.get_screen()
                    if self.get_text_position():
                        keyops.keyUp('w')
                        # self.press('s', 0.25)
                        time.sleep(0.5)
                        self.get_screen()
                        total_events = self.get_text_position(1)
                        if len(total_events) and total_events[0][0] < 1600:
                            # 有时候会锁定到右边的状态效果那个字
                            break
                        else:
                            keyops.keyDown('w')
                            time.sleep(1)
                            tm += 1.5

                keyops.keyUp('w')
                if total_events is None:
                    self.close_and_exit()
                    return 1
                log.info(f"total_events step: {total_events}")
                
                if not total_events or not (933 <= total_events[0][0] <= 972):
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(-100 * self.multi * self.scale))
                    time.sleep(0.3)
                    self.get_screen()
                    total_events_after = self.get_text_position(1)
                    if len(total_events_after) <= 2 and len(total_events_after) >= len(total_events):
                        total_events = total_events_after
                    else:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(100 * self.multi * self.scale))

                if total_events is None:
                    self.press('d', 0.5)
                    return 1
                
                if not total_events:
                    total_events = [(950, 0)]

                portal = self.find_portal()
                log.info(f"portal_detail: {portal['nums']}")
                log.info(f"area_state_update: {self.area_state}")

                if portal['nums'] > 0:
                    self.area_state = 2
                else:
                    log.info('对齐中...')
                    self.align_event('d', event_text=total_events[-1][0], click=1)
                    self.area_state += 1 + (len(total_events) == 1)
                    log.info(f"对齐完成, area_state: {self.area_state}")

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
            self.check_pop()
            time.sleep(0.3)
            keyops.keyDown('w')
            self.press('a', 0.45)
            time.sleep(1.5)
            keyops.keyUp('w')
            time.sleep(0.25)
            self.portal_opening_days(static=1)

        elif area_now == '商店':
            pyautogui.click()
            self.check_pop()
            time.sleep(0.3)
            keyops.keyDown('w')
            time.sleep(1.8)
            # self.press('d',0.4)
            keyops.keyUp('w')
            time.sleep(0.6)
            self.portal_opening_days(static=1)

        elif area_now == '首领':
            if self.floor == 13 and self.area_state > 0:
                # 已经结束战斗了
                self.close_and_exit()
                self.end_of_uni()
                return 1

            if self.area_state == 0:
                self.press('w',3)
                for c in config.skill_char:
                    if (c in self.team_member or c.isdigit()) and self.allow_e:
                        if c == '大黑塔' and self.da_hei_ta_effecting:
                            # 大黑塔秘技生效中,跳过
                            continue
                        self.press(int(c) if c.isdigit() else str(self.team_member[c]+1))
                        time.sleep(0.8)
                        self.check_dead()
                        self.skill()
                        time.sleep(1.5)

                pyautogui.click()
                time.sleep(0.2)
                pyautogui.click()
                self.area_state += 1
            else:
                time.sleep(1)
                self.portal_opening_days(static=1)

        elif area_now == '战斗':
            # 如果大黑塔秘技使能,先使用秘技,前面应该已经切换到了大黑塔
            if self.da_hei_ta and self.allow_e and not self.da_hei_ta_effecting:
                self.skill()
                self.da_hei_ta_effecting = True

            if self.area_state == 0:                
                keyops.keyDown('w')
                time.sleep(0.2)
                keyops.keyDown('shift')
                tm = time.time()
                while time.time() - tm < 3:
                    self.get_screen()
                    if self.check("divergent/z",0.5771,0.9546,mask="mask_z",threshold=0.96):
                        break
                time.sleep(0.8)
                keyops.keyUp('w')
                keyops.keyUp('shift')
                if self.quan and self.allow_e:
                    for _ in range(4):
                        self.skill(1)
                    self.press('w')
                    time.sleep(1.5)
                else:
                    pyautogui.click()
                self.area_state += 1
            else:
                if not (self.quan and self.allow_e):
                    self.press('w', 0.25)
                self.portal_opening_days(static=1)

        elif area_now == '财富':
            keyops.keyDown('w')
            time.sleep(1.6)
            self.press('a', 0.5)
            keyops.keyUp('w')
            pyautogui.click()
            self.check_pop()
            time.sleep(0.7)
            res = self.forward_until(text_list=['战利品', '药箱'], timeout=3.0, moving=0)
            if not res:
                pyautogui.click()
                self.check_pop()
                time.sleep(0.7)
                self.forward_until(text_list=['战利品', '药箱'], timeout=1.0, moving=0)
            time.sleep(1.4)
            self.portal_opening_days(static=1)

        elif area_now == '位面':
            pyautogui.click()
            time.sleep(2)
            self.close_and_exit()
        else:
            self.press('F4')
        return 1
    
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
        self.bless(reverse=0)
        
    def bless_blood(self):
        self.bless(blood=1)

    def bless(self, reverse=1, blood=0):
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
        if not self.click_img("new"):
            self.click_position([(box[0] + box[1]) // 2, 500])
        if blood:
            self.click_position([960, 975])
        else:
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

    def screen_test(self):
        cv.imshow("screen", self.get_screen())
        cv.waitKey(0)

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
