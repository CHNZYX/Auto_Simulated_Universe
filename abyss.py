import pyautogui
import cv2 as cv
import numpy as np
import time
import win32gui
import random
import sys
from utils.log import log
from utils.utils import UniverseUtils, set_forground
import utils.keyops as keyops
import os
import yaml
import pyuac


class Abyss(UniverseUtils):
    def __init__(self):
        super().__init__()
        self.abspath = os.path.dirname(__file__)  # 获取项目根目录../Auto_Simulated_Universe
        if getattr(sys, 'frozen', False):
            self.abspath = '.'
        self.threshold = 0.97
        self.floor = 0
        self._stop = 0
        with open(os.path.join(self.abspath, "abyss/info.yml"), "r", encoding="utf-8", errors="ignore") as f:
            config = yaml.safe_load(f)["order_text"]
            self.team = [config[:4], config[4:]]

    def start_abyss(self):
        self.fail_drag = 0
        self.end_battle_time = 0
        while self._stop == 0:
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
            warn_game = False
            cnt = 0
            while Text != "崩坏：星穹铁道" and not self._stop:
                self.lst_changed = time.time()
                if not warn_game:
                    warn_game = True
                    log.warning("等待游戏窗口")
                time.sleep(0.5)
                cnt += 1
                if cnt == 1200:
                    set_forground()
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
            self.route()
            time.sleep(0.2)
            if self.fail_drag > 4:
                self.press('esc')
                break

    def wait(self,peila=False):
        tm = time.time()
        ee = -2
        while self._stop == 0:
            self.get_screen()
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
            if self.check("auto_2", 0.0583, 0.0769) or Text != "崩坏：星穹铁道":
                tm = time.time()
            if self.check("c", 0.9464, 0.1287, threshold=0.985):
                if peila:
                    tm = time.time()
                    if self.check("peila", 0.6953,0.1880, mask="battle_mask"):
                        if ee == 3:
                            ee = 0
                        else:
                            self.press(' ')
                            time.sleep(0.2)
                            ee += 1
                        self.press('v')
                    else:
                        self.press('v')
                else:
                    self.press('v')
            if peila and self.check_auto():
                self.press('v')
                tm = time.time()
            if time.time() - tm > 14 or self.check("abyss/in", 0.9130, 0.6074):
                if self.click_text(['返回忘却之庭']):
                    time.sleep(1.5)
                self.end_battle_time = time.time()
                break
            time.sleep(0.1)

    def ready(self):
        img = self.get_screen()
        peila = self.ts.find_text(img, ['佩拉']) is not None
        for i in range(4):
            self.press(str(i + 1), 0.2)
            time.sleep(0.4)
            self.press("e")
            time.sleep(1.5)
            self.get_screen()
            if not (
                self.check("z", 0.5010, 0.9426, mask="abyss/mask_z", threshold=0.95)
                or self.check(
                    "abyss/z", 0.5010, 0.9426, mask="abyss/mask_z", threshold=0.95
                )
            ):
                break
        time.sleep(1)
        pyautogui.click()
        time.sleep(3.5)
        return peila

    def route(self):
        img = self.get_screen()
        # self.click_target('imgs/abyss/fail.jpg',0.9,True)
        if self.check("abyss/fail", 0.5995, 0.1343):
            self.click((0.5995, 0.1343))
        elif self.ts.find_text(img, ['角色编队']) is not None:
            if self.check("abyss/begin", 0.1062, 0.0815):
                self.click((0.1062, 0.0806))
                return
            if random.randint(0, 1):
                self.team = self.team[::-1]
            for i, j in enumerate([(0.4026, 0.3259), (0.4010, 0.2343)]):
                self.click(j)
                time.sleep(0.2)
                for k in self.team[i]:
                    t = k - 1
                    if t >= 0:
                        self.click(
                            (0.9427 - 0.0661 * (t % 4), 0.8102 - 0.1435 * (t // 4))
                        )
                        time.sleep(0.2)
            self.click((0.1062, 0.0806))
            time.sleep(1)
        elif self.ts.find_text(img[:600,:600], ['取得胜利时']) is not None:
            time.sleep(2)
            if time.time() - self.end_battle_time > 10:
                self.click((0.5, 0.14))
            time.sleep(2)
            self.press("w", 3.5)
            t = self.move_to_interac(1, 1)
            if abs(t) > 30:
                self.press("w", 1)
            peila = self.ready()
            self.wait(peila=peila)
            if abs(t) > 30:
                time.sleep(1)
                self.press("w")
                time.sleep(0.3)
                self.move_to_interac(1, 1)
                self.press("w", 1.7)
                peila = self.ready()
                self.wait(peila=peila)
        elif self.check("abyss/6", 0.5661, 0.5713):
            self.click((0.5, 0.2))
        elif self.check("abyss/5", 0.1125, 0.9389):
            self.click((0.9, 0.9))
            time.sleep(0.3)
            self.get_screen()
            gray = [156, 122, 126]
            gray2 = [118, 107, 111]
            bw_map = np.zeros(self.screen.shape[:2], dtype=np.uint8)
            bw_map[np.sum((self.screen - gray) ** 2, axis=-1) <= 800] = 255
            bw_map[np.sum((self.screen - gray2) ** 2, axis=-1) <= 800] = 255
            # cv.imwrite('tp.jpg',bw_map)
            res = (-1, -1)
            for i in ["3_stars", "2_stars", "1_star"]:
                target = cv.imread(self.format_path("abyss/" + i), cv.IMREAD_GRAYSCALE)
                result = cv.matchTemplate(bw_map, target, cv.TM_CCORR_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                if max_val > 0.88:
                    res = max_loc
                    break
            if res != (-1, -1):
                self.click((1 - res[0] / self.xx + 0.06, 1 - res[1] / self.yy + 0.02))
            else:
                self.drag((0.5, 0.5), (0.8 - 0.6 * random.randint(0, 1), 0.5))
                self.fail_drag += 1
        else:
            print('未知界面')
            self.click((0.5, 0.14))
            time.sleep(1)


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        abyss = Abyss()
        abyss.start_abyss()
