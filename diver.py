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
from utils.map_log import map_log
from utils.update_map import update_map
from utils.utils import UniverseUtils, set_forground, notif
import os
from align_angle import main as align_angle
from functools import cmp_to_key
from utils.config import config
import datetime
import requests
import pytz
import pyuac
import utils.keyops as keyops
from utils.keyops import KeyController
import bisect

# 版本号
version = "v7.0"


class SimulatedUniverse(UniverseUtils):
    def __init__(self, debug=0, nums=-1, speed=0):
        super().__init__()
        self._stop = True
        self.floor = 0
        self.count = self.my_cnt = 0
        self.nums = nums
        self.speed = speed
        self.init_tm = time.time()
        self.area_state = 0
        self.action_history = []
        self.event_solved = self.bless_solved = 0
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
            while Text != "崩坏：星穹铁道" and not self._stop:
                self.lst_changed = time.time()
                if self._stop:
                    raise KeyboardInterrupt
                if not warn_game:
                    warn_game = True
                    log.warning("等待游戏窗口")
                time.sleep(0.5)
                cnt += 1
                if cnt == 1200:
                    set_forground()
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
            if self._stop:
                break
            # self.click_target('imgs/divergent/start.jpg',0.9,True) # 如果需要输出某张图片在游戏窗口中的坐标，可以用这个
            self.loop()
        log.info("停止运行")

    def loop(self):
        self.get_screen()
        self.ts.forward(self.screen)
        # self.ts.find_with_box()
        # exit()
        self.run_static(json_path = "actions/default.json")
        
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
            self.click(action["position"])
            return 1
        return 0

    def run_static(self, json_path="actions/default.json", json_file=None) -> str:
        if json_file is None:
            json_file = json.load(open(json_path, "r", encoding="utf-8"))
        for i in json_file:
            trigger = i["trigger"]
            text = self.ts.find_with_box(trigger["box"], redundancy=trigger.get("redundancy", 30))
            if len(text):
                if trigger["text"] in self.merge_text(text):
                    log.info(f"触发 {i['name']}:{trigger['text']}")
                    for j in i["actions"]:
                        self.do_action(j)
                    self.action_history.append(i["name"])
                    self.action_history = self.action_history[-10:]
                    return i['name']
        return ''
    
    def clean_text(self, text, char):
        symbols = r"[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~—“”‘’«»„…·¿¡£¥€©®™°±÷×¶§‰]，。！？；：（）【】「」《》、￥"
        if char:
            symbols += r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        translator = str.maketrans('', '', symbols)
        return text.translate(translator)

    def merge_text(self, text, char=1):
        def compare(item1, item2):
            x1, _, y1, _ = item1['box']
            x2, _, y2, _ = item2['box']
            if abs(y1 - y2) <= 5:
                return x1 - x2
            return y1 - y2
        text = sorted(text, key=cmp_to_key(compare))
        return self.clean_text(''.join([i['raw_text'] for i in text]), char)
    
    def close_and_exit(self, click=True):
        self.press('esc')
        time.sleep(2.5)
        if click:
            self.click_posintion([1530, 990])

    def get_text_type(self, text, types):
        for i in types:
            if i in text:
                return i
        return None

    def get_now_area(self):
        self.area_text = self.ts.find_with_box([58, 525, 9, 32], redundancy=30)
        self.area_text = self.merge_text(self.area_text, char=0)
        return self.get_text_type(self.area_text, ['长石号', '事件', '奖励', '遭遇', '商店', '首领', '战斗', '财富', '休整', '位面'])
    
    def find_portal(self):
        prefer_portal = ['事件', '奖励', '商店', '首领', '财富', '战斗', '休整', '遭遇']
        text = self.ts.find_with_box([0,1920,60,500], redundancy=0)
        portal = {'score':100}
        for i in text:
            if '区域' in i['raw_text'] and i['box'][3] - i['box'][2] < 40:
                portal_type = self.get_text_type(i['raw_text'], prefer_portal)
                if portal_type is not None:
                    i.update({'score':prefer_portal.index(portal_type), 'type':portal_type})
                    if i['score'] < portal['score']:
                        portal = i
        if portal['score'] == 100:
            return None
        else:
            return portal
        
    def portal_bias(self, portal):
        return (portal['box'][0] + portal['box'][1]) // 2 - 950
    
    def aim_portal(self, portal):
        zero = bisect.bisect_left(config.angles, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(100 * self.multi * self.scale))
        while abs(self.portal_bias(portal)) > 25:
            angle = bisect.bisect_left(config.angles, self.portal_bias(portal)) - zero
            self.mouse_move(angle)
            time.sleep(0.3)
            self.ts.forward(self.get_screen())
            portal = self.find_portal()
            if portal is None:
                return 1
        return 1

    def portal_opening_days(self, aimed=0, static=0):
        s = self.speed
        tm = time.time()
        portal = None
        moving = 0
        if static:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(100 * self.multi * self.scale))
            for i in [0, 60, 90, 90, 90, -120, -120, -90]:
                self.mouse_move(i)
                time.sleep(0.3)
                self.ts.forward(self.get_screen())
                portal = self.find_portal()
                if portal is not None:
                    break
        while time.time() - tm < 5 or portal is not None:
            if aimed == 0:
                self.ts.forward(self.get_screen())
                portal = self.find_portal()
            else:
                self.get_screen()
                if self.check_f(check_text=0):
                    keyops.keyUp('w')
                    self.ts.forward(self.get_screen())
                    if self.check_f(is_in=[portal['type'] if portal else '区域']):
                        self.press('f')
                        for _ in range(2):
                            self.press('s',0.15)
                            self.press('f')
                        return
                    else:
                        keyops.keyDown('w')
                        time.sleep(0.5)
            if portal is not None and not aimed:
                x = self.portal_bias(portal)
                if abs(x) > 25:
                    if moving:
                        keyops.keyUp('w')
                        moving = 0
                        self.press('s',0.6)
                        continue
                    else:
                        aimed = self.aim_portal(portal)
                        moving = 1
                        keyops.keyDown('w')
                else:
                    aimed = 1
                    if not moving:
                        moving = 1
                        keyops.keyDown('w')
            elif portal is None:
                if not moving:
                    keyops.keyDown('w')
                    moving = 1

    def event(self):
        self.event_solved = 1
        if self.check("arrow", 0.1828, 0.5000, mask="mask_event"):
            self.click((self.tx, self.ty))
        # 事件界面：退出
        elif self.check("arrow_1", 0.1828, 0.5000, mask="mask_event"):
            self.click((self.tx, self.ty))
        # 事件选择界面
        elif self.check("star", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
            tx, ty = self.tx, self.ty
            time.sleep(0.3)
            self.get_screen()
            if self.check("confirm", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
                self.click((self.tx, self.ty))
            else:
                self.click((tx, ty))
                time.sleep(0.3)
                self.click((0.1167, ty - 0.4685 + 0.3546))
        else:
            self.click((0.9479, 0.9565))

    def find_event_text(self):
        self.ts.forward(self.get_screen())
        print(self.ts.find_with_box())
        text = self.ts.find_with_box([300, 1920, 0, 320], redundancy=0)
        print(text)
        res = 0
        for i in text:
            box = i['box']
            if 'ms' in i['raw_text'] or (box[0] > 1800 and box[2] < 120):
                continue
            w, h = box[1] - box[0], box[3] - box[2]
            if w < 40 or h < 20 or h > 40:
                continue
            res = max(res, (box[0] + box[1]) // 2)
        print(res)
        return res
    
    def align_event(self, deep=0):
        if deep == 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, int(-300 * self.multi * self.scale))
        event_text = self.find_event_text()
        self.get_screen()
        if self.check_f(check_text=0):
            self.press('f')
            return
        if event_text:
            if abs(event_text - 950) > 40:
                self.press('a',0.2)
                event_text_after = self.find_event_text()
                if event_text_after == 0:
                    self.close_and_exit(click = False)
                    return
                sub = event_text_after - event_text
                sub = (event_text_after - 950) // sub
                for _ in range(sub):
                    self.press('d',0.2)
                for _ in range(-sub):
                    self.press('a',0.2)
        else:
            if deep < 3:
                self.press('w',[0,0.3,0.5][deep])
                self.align_event(deep+1)
            else:
                self.close_and_exit(click = False)
            return
        keyops.keyDown('w')
        self.keys.fff = 1
        tm = time.time()
        while time.time() - tm < 6:
            self.ts.forward(self.get_screen())
            if self.get_now_area() == None:
                self.keys.fff = 0
                keyops.keyUp('w')
                return

    def area(self):
        area_now = self.get_now_area()
        time.sleep(0.7)
        self.ts.forward(self.get_screen())
        if self.get_now_area() != area_now:
            return
        time.sleep(1.2)
        if self.area_state == -1:
            self.close_and_exit(click = False)
            return
        now_floor = self.floor
        for i in range(1,14):
            if self.area_text.startswith(f'{i}13'):
                now_floor = i
        if now_floor != self.floor:
            self.floor, self.area_state = now_floor, 0
            self.event_solved = 0
            self.bless_solved = 0
        if area_now == '长石号':
            self.press('f')
            self.press('F4')
        elif area_now in ['事件', '奖励', '遭遇']:
            if self.area_state==0:
                keyops.keyDown('w')
                time.sleep(1.8)
                self.press('d',0.8)
                keyops.keyUp('w')
                time.sleep(0.8)
                self.align_event()
            elif self.area_state==1:
                self.keys.fff = 1
                self.press('a', 1.3)
                self.keys.fff = 0
                self.ts.forward(self.get_screen())
                if self.check_f(check_text=0):
                    self.press('f')
                elif self.get_now_area() is not None:
                    self.press('w', 0.3)
                    self.get_screen()
                    if self.check_f(check_text=0):
                        self.press('f')
                    else:
                        self.press('s',1)
                        self.align_event()
            else:
                self.mouse_move(20)
                self.portal_opening_days(static=1)
            self.area_state += 1
        elif area_now == '休整':
            self.press('a', 0.3)
            self.press('w', 4)
            self.portal_opening_days(aimed=1)
        elif area_now == '商店':
            self.press('w', 1.5)
            self.portal_opening_days()
        elif area_now == '首领':
            if self.area_state == 0:
                self.press('w',3)
                pyautogui.click()
                time.sleep(0.2)
                pyautogui.click()
            elif self.area_state == 1:
                if self.floor == 13:
                    self.close_and_exit()
                elif self.bless_solved:
                    self.press('w', 1.8)
                    self.press('f')
                else:
                    self.area_state = 3
            elif self.area_state == 2:
                self.press('d', 0.4)
                self.press('f')
            elif self.area_state == 3:
                self.press('a', 0.8)
                self.press('f')
            elif self.area_state == 4:
                if self.bless_solved:
                    keyops.keyDown('d')
                    self.press('s', 0.2)
                    time.sleep(0.2)
                    keyops.keyUp('d')
                    self.portal_opening_days(static=1)
                else:
                    self.portal_opening_days()
            self.area_state += 1
        elif area_now == '战斗':
            if self.area_state == 0:
                self.press('w', 3.2)
                pyautogui.click()
            else:
                self.press('w', 0.5)
                self.portal_opening_days(static=1)
            self.area_state += 1
        elif area_now == '财富':
            keyops.keyDown('w')
            time.sleep(2.4)
            self.press('a', 0.6)
            time.sleep(1)
            keyops.keyUp('w')
            self.press('f')
            self.portal_opening_days(static=1)
        elif area_now == '位面':
            self.close_and_exit()
        else:
            self.press('F4')
    
    def bless_score(self, text):
        score = 0
        for i in config.team_black:
            if i in text:
                return 0
        for i in config.team_white:
            if i in text:
                score += 100-i
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
        blesses = []
        for i in text:
            box = i["box"]
            x, y = (box[0] + box[1]) // 2, (box[2] + box[3]) // 2
            box = [x - 220, x + 220, y - 350, y]
            bless_text = self.ts.find_with_box(box)
            bless_raw_text = self.merge_text(bless_text)
            blesses.append({'raw_text': bless_raw_text, 'box': box, 'score': self.bless_score(bless_raw_text)})
        blesses = sorted(blesses, key=lambda x: x['score'], reverse=reverse)
        self.click_box(blesses[0]['box'])
        time.sleep(0.5)
        self.click_posintion([1695, 962])
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
        if self.debug == 0 and self.check_bonus == 0 and self.nums <= self.my_cnt and self.nums >= 0:
            log.info('已完成上限，准备停止运行')
            self.end = 1
        self.floor = 0

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
            if self.debug:
                traceback.print_stack()
        except:
            pass
        self._stop = True
    
    def on_key_press(self, event):
        global stop_flag
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


def main():
    global nums, speed, debug
    nums = config.max_run
    log.info(f"debug: {debug}")
    su = SimulatedUniverse(debug, nums, speed)
    try:
        su.start()
    except ValueError as e:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        su.stop()


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        debug = 0
        nums = 34
        speed = 0
        for i in sys.argv[1:]:
            st = i.split("-")[-1]
            if "=" not in st:
                st = st + "=1"
            exec(st)
        main()
