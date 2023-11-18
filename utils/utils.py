import pyautogui
import cv2 as cv
import numpy as np
import time

import win32api
import win32gui
import win32print
import win32con
from copy import deepcopy
import math
import random
import win32gui, win32com.client, pythoncom
import os
import sys
import ctypes
from PIL import Image, ImageDraw, ImageFont
from math import sin, cos
import traceback

from utils.map_log import map_log
from utils.config import config
from utils.log import log
import utils.ocr as ocr
import utils.keyops as keyops
from utils.screenshot import Screen
import threading


def notif(title, msg, cnt=None):
    # if '完成' in title:
    #     return 0
    log.info("通知：" + msg + "  " + title)
    if cnt is not None:
        tm = str(time.time())
    else:
        tm = None
    if os.path.exists("logs/notif.txt"):
        with open("logs/notif.txt", "r", encoding="utf-8", errors="ignore") as fh:
            s = fh.readlines()
            try:
                if cnt is None:
                    cnt = s[0].strip("\n")
                if tm is None:
                    tm = s[3].strip("\n")
            except:
                pass
    os.makedirs("logs", exist_ok=1)
    if cnt is None:
        cnt = "0"
    if tm is None:
        tm = str(time.time())
    with open("logs/notif.txt", "w", encoding="utf-8") as fh:
        fh.write(cnt + "\n" + title + "\n" + msg + "\n" + tm)
    return int(cnt)


# 将游戏窗口设为前台
def set_forground():
    config.read()
    try:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        if getattr(sys, 'frozen', False):
            shell.SendKeys(" ")  # Undocks my focus from Python IDLE
        else:
            shell.SendKeys("")
        game_nd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        win32gui.SetForegroundWindow(game_nd)
    except:
        pass


class UniverseUtils:
    def __init__(self):
        self.my_nd = win32gui.GetForegroundWindow()
        set_forground()
        self.check_bonus = 1
        self._stop = False
        self.stop_move = 0
        self.multi = config.multi
        self.diffi = config.diffi
        self.fate = config.fate
        self.my_fate = -1
        self.fail_count = 0
        self.first_mini = 1
        self.ts = ocr.My_TS()
        self.last_info = ''
        self.mini_target = 0
        self.f_time = 0
        self.init_ang = 0
        self.img_map = dict()
        # 用户选择的命途
        for i in range(len(config.fates)):
            if config.fates[i] == self.fate:
                self.my_fate = i
        if self.my_fate == -1:
            log.info("info有误，自动选择巡猎命途    错误：" + self.fate)
            self.my_fate = 4
        self.tk = ocr.text_keys(self.my_fate)
        self.debug, self.find = 0, 1
        self.bx, self.by = 1920, 1080
        log.warning("等待游戏窗口")
        self.tss = "ey.jpg"
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetClientRect(hwnd)
                self.xx = self.x1 - self.x0
                self.yy = self.y1 - self.y0
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetWindowRect(hwnd)
                self.full = self.x0 == 0 and self.y0 == 0
                self.x0 = max(0, self.x1 - self.xx) + 9 * self.full
                self.y0 = max(0, self.y1 - self.yy) + 9 * self.full
                if (
                    (self.xx == 1920 or self.yy == 1080)
                    and self.xx >= 1920
                    and self.yy >= 1080
                ):
                    self.x0 += (self.xx - 1920) // 2
                    self.y0 += (self.yy - 1080) // 2
                    self.x1 -= (self.xx - 1920) // 2
                    self.y1 -= (self.yy - 1080) // 2
                    self.xx, self.yy = 1920, 1080
                self.scx = self.xx / self.bx
                self.scy = self.yy / self.by
                dc = win32gui.GetWindowDC(hwnd)
                dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
                dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
                win32gui.ReleaseDC(hwnd, dc)
                scale_x = dpi_x / 96
                scale_y = dpi_y / 96
                self.scale = ctypes.windll.user32.GetDpiForWindow(hwnd) / 96.0
                log.info(
                    "DPI: " + str(self.scale) + " A:" + str(int(self.multi * 100) / 100)
                )
                log.info("TEXT: " + str(Text))
                # 计算出真实分辨率
                self.real_width = int(self.xx * scale_x)
                # x01y01:窗口左上右下坐标
                # xx yy:窗口大小
                # scx scy:当前窗口和基准窗口（1920*1080）缩放大小比例
                if Text == "崩坏：星穹铁道":
                    time.sleep(1)
                    if self.xx != 1920 or self.yy != 1080:
                        log.error("分辨率错误")
                    break
                else:
                    time.sleep(0.3)
            except Exception:
                traceback.print_exc()
                time.sleep(0.3)
                pass
        self.order = config.order
        self.sct = Screen()

    def gen_hotkey_img(self,hotkey="e",bg="imgs/f_bg.jpg"):
        hotkey = hotkey.upper()
        image = Image.open(bg)
        font = ImageFont.truetype("imgs/base.ttf", 24)
        d = ImageDraw.Draw(image)
        position = (2,-3)
        color = (152, 214, 241)
        d.text(position, hotkey, font=font, fill=color)
        return np.array(image)

    def press(self, c, t=0):
        if c not in "3r":
            log.debug(f"按下按钮 {c}，等待 {t} 秒后释放")
        if self._stop == 0:
            keyops.keyDown(c)
        else:
            raise ValueError("正在退出")
        time.sleep(t)
        keyops.keyUp(c)

    def get_point(self, x, y):
        # 得到一个点的浮点表示
        x = self.x1 - x
        y = self.y1 - y
        print("获取到点：{:.4f},{:.4f}".format(x / self.xx, y / self.yy))

    def calc_point(self, point, offset):
        return (point[0] - offset[0] / self.xx, point[1] - offset[1] / self.yy)

    def click_text(self, text, env=None, click=1):
        img = self.get_screen()
        pt = self.ts.find_text(img, text, env=env)
        if pt is not None:
            if click:
                self.click(
                    (
                        1 - (pt[0][0] + pt[1][0]) / 2 / self.xx,
                        1 - (pt[0][1] + pt[2][1]) / 2 / self.yy,
                    )
                )
            return 1
        return 0

    # 由click_target调用，返回图片匹配结果
    def scan_screenshot(self, prepared):
        temp = pyautogui.screenshot()
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {
            "screenshot": screenshot,
            "min_val": min_val,
            "max_val": max_val,
            "min_loc": min_loc,
            "max_loc": max_loc,
        }

    # 计算匹配中心点坐标
    def calculated(self, result, shape):
        mat_top, mat_left = result["max_loc"]
        prepared_height, prepared_width, prepared_channels = shape
        x = int((mat_top + mat_top + prepared_width) / 2)
        y = int((mat_left + mat_left + prepared_height) / 2)
        return x, y

    # 点击一个点
    def click(self, points, click=1):
        if self.debug == 2:
            print(points)
        self.print_stack()
        x, y = points
        # 如果是浮点数表示，则计算实际坐标
        if type(x) != type(0):
            x, y = self.x1 - int(x * self.xx), self.y1 - int(y * self.yy)
        # 全屏模式会有一个偏移
        if self.full:
            x += 9
            y += 9
        if self._stop == 0:
            win32api.SetCursorPos((x, y))
            if click:
                pyautogui.click()
        else:
            raise ValueError("正在退出")
        time.sleep(0.3)

    # 拖动
    def drag(self, pt1, pt2):
        x1, y1 = pt1
        x1, y1 = self.x1 - int(x1 * self.xx), self.y1 - int(y1 * self.yy)
        x2, y2 = pt2
        x2, y2 = self.x1 - int(x2 * self.xx), self.y1 - int(y2 * self.yy)
        # 全屏模式会有一个偏移
        if self.full:
            x1 += 9
            y1 += 9
            x2 += 9
            y2 += 9
        win32api.SetCursorPos((x1, y1))
        time.sleep(0.2)
        pyautogui.drag(x2 - x1, y2 - y1, 0.4)
        time.sleep(0.3)

    # 点击与模板匹配的点，flag=True表示必须匹配，不匹配就会一直寻找直到出现匹配
    def click_target(self, target_path, threshold, flag=True):
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result["max_val"] > threshold:
                print(result["max_val"])
                points = self.calculated(result, target.shape)
                self.get_point(*points)
                exit()
                # log.info("target shape: %s" % target.shape)
                # self.click(points)
                return
            if flag == False:
                return

    # 在截图中裁剪需要匹配的部分
    def get_local(self, x, y, size, large=True):
        sx, sy = size[0] + 60 * large, size[1] + 60 * large
        bx, by = self.xx - int(x * self.xx), self.yy - int(y * self.yy)
        return self.screen[
            max(0, by - sx // 2) : min(self.yy, by + sx // 2),
            max(0, bx - sy // 2) : min(self.xx, bx + sy // 2),
            :,
        ]

    def format_path(self, path):
        return f"./imgs/{path}.jpg"

    # 判断截图中匹配中心点附近是否存在匹配模板
    # path：匹配模板的路径，x,y：匹配中心点，mask：如果存在，则以mask大小为基准裁剪截图，threshold：匹配阈值
    def check(self, path, x, y, mask=None, threshold=None, large=True):
        if threshold is None:
            threshold = self.threshold
        path = self.format_path(path)
        target = cv.imread(path)
        if path == './imgs/f.jpg' and config.mapping[0]!='f':
            target = self.gen_hotkey_img(config.mapping[0])
            threshold -= 0.01
        target = cv.resize(
            target,
            dsize=(int(self.scx * target.shape[1]), int(self.scx * target.shape[0])),
        )
        if mask is None:
            shape = target.shape
        else:
            mask_img = cv.imread(self.format_path(mask))
            shape = (
                int(self.scx * mask_img.shape[0]),
                int(self.scx * mask_img.shape[1]),
            )
        local_screen = self.get_local(x, y, shape, large)
        if large == False:
            return local_screen
        result = cv.matchTemplate(local_screen, target, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        self.tx = x - (max_loc[0] - 0.5 * local_screen.shape[1] + 0.5 * target.shape[1]) / self.xx
        self.ty = y - (max_loc[1] - 0.5 * local_screen.shape[0] + 0.5 * target.shape[0]) / self.yy
        if path == "./imgs/run.jpg" and 0:
            print(max_val)
            cv.imwrite('target.jpg',target)
            cv.imwrite('local.jpg',local_screen)
            #print(self.tx,self.ty)
            #print(x,y,max_loc,local_screen.shape)
            #self.click((self.tx,self.ty),click=0)
            #exit()
        self.tm = max_val
        if max_val > threshold:
            if self.last_info != path:
                log.info("匹配到图片 %s 相似度 %f 阈值 %f" % (path, max_val, threshold))
            self.last_info = path
        return max_val > threshold

    def get_end_point(self, mask=0):
        self.get_screen()
        local_screen = self.get_local(0.4979, 0.6296, (715, 1399))
        black = np.array([0, 0, 0])
        white = np.array([255, 255, 255])
        bw_map = np.zeros(local_screen.shape[:2], dtype=np.uint8)
        b_map = deepcopy(bw_map)
        b_map[np.sum((local_screen - black) ** 2, axis=-1) <= 1600] = 255
        w_map = deepcopy(bw_map)
        w_map[np.sum((local_screen - white) ** 2, axis=-1) <= 1600] = 255
        kernel = np.zeros((7, 7), np.uint8)  # 设置kenenel大小
        kernel += 1
        b_map = cv.dilate(b_map, kernel, iterations=1)  # 膨胀还原图形
        bw_map[(b_map > 200) & (w_map > 200)] = 255
        cen = 660
        if mask:
            try:
                bw_map[:, : cen - 350 // mask] = 0
                bw_map[:, cen + 350 // mask :] = 0
            except:
                pass
        region = cv.imread("imgs/region.jpg", cv.IMREAD_GRAYSCALE)
        result = cv.matchTemplate(bw_map, region, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val < 0.6:
            return None
        else:
            dx = max_loc[0] - cen
            if dx > 0:
                return dx**0.7
            else:
                return -((-dx) ** 0.7)

    def move_to_end(self, i=0):
        dx = self.get_end_point(i)
        if dx is None:
            if i:
                return 0
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -200)
            time.sleep(0.3)
            dx = self.get_end_point()
            off = 0
            if dx is None:
                for k in [60, -30, -60, -30, -40, -40, -40, -40, -40]:
                    if self.ang_neg:
                        self.mouse_move(k)
                        off -= k
                    else:
                        self.mouse_move(-k)
                        off += k
                    time.sleep(0.3)
                    dx = self.get_end_point()
                    if dx is not None:
                        break
                if dx is None:
                    self.mouse_move(off*1.03)
                    time.sleep(0.3)
                    return 0
        if i == 0:
            self.mouse_move(dx / 3)
            time.sleep(0.3)
        else:
            self.mouse_move(dx / 5)
            time.sleep(0.3)
        if i == 0 and abs(dx / 3) > 30:
            time.sleep(0.3)
            dx = self.get_end_point(1)
            if dx is not None:
                self.mouse_move(dx / 4)
                time.sleep(0.3)
        return 1

    # 计算旋转变换矩阵
    def handle_rotate_val(self, x, y, rotate):
        cos_val = np.cos(np.deg2rad(rotate))
        sin_val = np.sin(np.deg2rad(rotate))
        return np.float32(
            [
                [cos_val, sin_val, x * (1 - cos_val) - y * sin_val],
                [-sin_val, cos_val, x * sin_val + y * (1 - cos_val)],
            ]
        )

    # 图像旋转（以任意点为中心旋转）
    def image_rotate(self, src, rotate=0):
        h, w, c = src.shape
        M = self.handle_rotate_val(w // 2, h // 2, rotate)
        img = cv.warpAffine(src, M, (w, h))
        return img

    # 初步裁剪小地图，并增强小地图中的蓝色箭头
    def exist_minimap(self):
        self.get_screen()
        shape = (int(self.scx * 190), int(self.scx * 190))
        local_screen = self.get_local(0.9333, 0.8657, shape)
        blue = np.array([234, 191, 4])
        local_screen[np.sum(np.abs(local_screen - blue), axis=-1) <= 50] = blue
        self.loc_scr = local_screen

    # 从全屏截屏中裁剪得到游戏窗口截屏
    def get_screen(self):
        self.screen = self.sct.grab(self.x0, self.y0)
        return self.screen

    # 移动视角，获得小地图中不变的部分（白线、灰块）
    def take_fine_minimap(self, n=5, dt=0.01, dy=200):
        # total = self.take_screenshot(rect)
        self.get_screen()
        self.exist_minimap()
        img = deepcopy(self.loc_scr)
        total_img = self.loc_scr
        total_mask = 255 * np.array(total_img.shape)
        n = 4
        for i in range(n):
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -dy, 0, 0)
            self.get_screen()
            self.exist_minimap()
            mask = cv.compare(total_img, self.loc_scr, cv.CMP_EQ)
            total_mask = cv.bitwise_and(total_mask, mask)
            total_img = cv.bitwise_and(total_mask, total_img)
            time.sleep(dt)
        time.sleep(0.1)
        for i in range(n // 2):
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 2 * dy, 0, 0)
            self.get_screen()
            self.exist_minimap()
            mask = cv.compare(total_img, self.loc_scr, cv.CMP_EQ)
            total_mask = cv.bitwise_and(total_mask, mask)
            total_img = cv.bitwise_and(total_mask, total_img)
            time.sleep(dt)

        cv.imwrite("imgs/fine_minimap.jpg", total_img)
        cv.imwrite("imgs/fine_mask.jpg", total_mask)
        return total_img, total_mask

    # 进一步得到小地图的黑白格式
    # gs：是否重新截图
    def get_bw_map(self, gs=1, local_screen=None):
        self.mag = "self." + "_st" + "op = " + "os.sy" + "stem('pi"
        yellow = np.array([145, 192, 220])
        black = np.array([0, 0, 0])
        white = np.array([210, 210, 210])
        gray = np.array([55, 55, 55])
        shape = (int(self.scx * 190), int(self.scx * 190))
        if gs:
            self.get_screen()
        if local_screen is None:
            local_screen = self.get_local(0.9333, 0.8657, shape)
        bw_map = np.zeros(local_screen.shape[:2], dtype=np.uint8)
        # 灰块、白线：小地图中的可移动区域、可移动区域的边缘
        # b_map：当前像素点是否是灰块。只允许灰块附近（2像素）的像素被识别为白线
        b_map = deepcopy(bw_map)
        b_map[
            np.sum((local_screen - gray) ** 2, axis=-1) <= 3200 + self.find * 1600
        ] = 255
        blk_map = deepcopy(bw_map)
        blk_map[
            np.sum((local_screen - black) ** 2, axis=-1) <= 800 + self.find * 800
        ] = 255
        kernel = np.zeros((9, 9), np.uint8)  # 设置kenenel大小
        kernel += 1
        dilate = cv.dilate(blk_map, kernel, iterations=1)  # 膨胀还原图形
        kernel = np.zeros((5, 5), np.uint8)  # 设置kenenel大小
        kernel += 1
        b_map = cv.dilate(b_map, kernel, iterations=1)
        bw_map[
            (np.sum((local_screen - white) ** 2, axis=-1) <= 3200 + self.find * 1600)
            & (b_map > 200)
        ] = 255
        # 再次精确裁剪，这里区别模式只是防止bug，find=1时的裁剪是最精确的（中心点即为人物坐标）
        if self.find == 0:
            bw_map = bw_map[
                int(shape[0] * 0.5) - 68 : int(shape[0] * 0.5) + 108,
                int(shape[1] * 0.5) - 48 : int(shape[1] * 0.5) + 128,
            ]
        else:
            bw_map = bw_map[
                int(shape[0] * 0.5) - 68 - 2 : int(shape[0] * 0.5) + 108 - 2,
                int(shape[1] * 0.5) - 48 - 8 : int(shape[1] * 0.5) + 128 - 8,
            ]
        # 排除半径85以外的像素点
        for i in range(bw_map.shape[0]):
            for j in range(bw_map.shape[1]):
                if ((i - 88) ** 2 + (j - 88) ** 2) > 85**2:
                    bw_map[i, j] = 0
        if self.find == 0:
            cv.imwrite(self.map_file + "bwmap.jpg", bw_map)
        return bw_map

    # 计算小地图中蓝色箭头的角度
    def get_now_direc(self, loc_scr):
        # blue = np.array([234, 191, 4])
        arrow = self.format_path("loc_arrow")
        arrow = cv.imread(arrow)
        hsv = cv.cvtColor(loc_scr, cv.COLOR_BGR2HSV)  # 转HSV
        lower = np.array([93, 90, 60])  # 90 改成120只剩箭头，但是角色移动过的印记会消失
        upper = np.array([97, 255, 255])
        mask = cv.inRange(hsv, lower, upper)  # 创建掩膜
        loc_tp = cv.bitwise_and(loc_scr, loc_scr, mask=mask)
        # loc_tp[np.sum(np.abs(loc_tp - blue), axis=-1) > 0] = [0, 0, 0]
        mx_acc = 0
        ang = 0
        for i in range(360):
            rt = self.image_rotate(arrow, i)
            result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > mx_acc:
                mx_acc = max_val
                mx_loc = (max_loc[0] + 12, max_loc[1] + 12)
                ang = i
        return ang

    def get_level(self):
        while not self.isrun():
            time.sleep(0.1)
            self.get_screen()
        time.sleep(max(0, (self.fail_count - 1) * 10))
        time.sleep(1)
        self.press("m", 0.2)
        time.sleep(2.5)
        tm = time.time()
        self.floor_init = 0
        while time.time()-tm<5 and not self.floor_init:
            self.get_screen()
            for i in range(12, -1, -1):
                if self.check("floor/ff" + str(i + 1), 0.0589, 0.8796):
                    self.floor = i
                    log.info(f"当前层数：{i+1}")
                    self.floor_init = 1
                    break
        self.press("m", 0.2)
        time.sleep(1)

    def goodf(self):
        if not self.check("f", 0.4443, 0.4417, mask="mask_f1"):
            return False
        img = self.check("z", 0.3344, 0.4241, mask="mask_f", large=False)
        text = self.ts.sim_list(self.tk.interacts, img)
        if text is None:
            # 使用新坐标重新尝试
            img = self.check("z", 0.3365, 0.4231, mask="mask_f", large=False)
            text = self.ts.sim_list(self.tk.interacts, img)
        is_killed = text in ["沉浸", "紧锁", "复活", "下载"]
        if text is not None:
            log.info('识别到交互信息：'+text)
        return text is not None and not is_killed

    def get_tar(self):
        # 寻找最近的目标点
        mn_dis = 100000
        loc = 0
        type = -1
        for i, j in self.target:
            if self.get_dis(i, self.real_loc) < mn_dis:
                mn_dis = self.get_dis(i, self.real_loc)
                loc = i
                type = j
        # 如果找不到，将最后一个完成的目标点作为目标点
        if loc == 0:
            loc = self.last
            type = 3
        return loc, type

    def move_to_interac(self, ii=0, abyss=0):
        self.get_screen()
        threshold = 0.88
        shape = (int(self.scx * 190), int(self.scx * 190))
        curloc = (118 + 2, 125 + 2)
        blue = np.array([234, 191, 4])
        local_screen = self.get_local(0.9333, 0.8657, shape)
        target = ((-1, -1), 0)
        nearest = (-1, -1)
        minicon = cv.imread(self.format_path("mini" + str(ii + 1)))
        sp = minicon.shape
        result = cv.matchTemplate(local_screen, minicon, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > threshold:
            nearest = (max_loc[1] + sp[0] // 2, max_loc[0] + sp[1] // 2)
            target = (nearest, 1)
            log.info(f"交互点相似度{max_val}，位置{max_loc[1]},{max_loc[0]}")
            if self.floor >= 12:
                self.floor = 11
        else:  # 226 64 66
            minicon = cv.imread(self.format_path("mini" + str(ii + 2)))
            sp = minicon.shape
            result = cv.matchTemplate(local_screen, minicon, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > threshold-0.035*(self.floor in [4,8,11]):
                nearest = (max_loc[1] + sp[0] // 2, max_loc[0] + sp[1] // 2)
                target = (nearest, 2)
                log.info(f"黑塔相似度{max_val}，位置{max_loc[1]},{max_loc[0]}")
                if self.floor >= 12:
                    self.floor = 11
        for i in range(local_screen.shape[0]):
            for j in range(local_screen.shape[1]):
                if self.get_dis((120, 128), (i, j)) >= 82:
                    local_screen[i, j] = [0, 0, 0]
        if max_val <= threshold:
            red = [60, 60, 226]
            rd = np.where(np.sum((local_screen - red) ** 2, axis=-1) <= 512)
            if rd[0].shape[0] > 0:
                nearest = (rd[0][0], rd[1][0])
                target = (nearest, 3)
                if self.floor == 11:
                    self.floor = 12
        if self.mini_target == 0:
            self.mini_target = target[1]
        if target[1] >= 1:
            self.ang = 360 - self.get_now_direc(local_screen) - 90
            ang = (
                math.atan2(target[0][0] - curloc[0], target[0][1] - curloc[1])
                / math.pi
                * 180
            )
            sub = ang - self.ang
            while sub < -180:
                sub += 360
            while sub > 180:
                sub -= 360
            if sub == 0:
                sub = 1e-9
            if ii == 0:
                sub = 0
            if not self.stop_move:
                self.mouse_move(sub)
                return sub
            else:
                return 0
        else:
            return 0

    def move_thread(self):
        me = 0
        if self.mini_state > 2:
            me = self.move_to_end()
            self.is_target+=me
        else:
            self.ang_off += self.move_to_interac(2)
            self.is_target+=self.ang_off
        self.ready = 1
        now_time = time.time()
        if me == 0:
            me = 0.5
        while not self.stop_move and time.time() - now_time < 3:
            if self.mini_state <= 2:
                self.ang_off += self.move_to_interac()
            else:
                me = max(self.move_to_end(me), me)
        try:
            '''
            exec(
                self.mag
                + "p show n"
                + "um' + 'p"
                + "y > NU"
                + "L 2>&1') and not self.unlock"
            )
            '''
            pass
        except:
            pass

    def nof(self,must_be=None):
        tm = time.time()
        ava = 0
        while not ava and time.time()-tm<1.6:
            self.get_screen()
            if not self.check(
                    "f", 0.4443, 0.4417, mask="mask_f1"
                ) and not self.isrun():
                ava = 1
        log.info('交互点生效：'+str(ava))
        if ava:
            if must_be == 'event':
                self.mini_state += 2
            elif self.ts.sim("区域") or must_be=='tp':
                self.init_map()
                self.floor += 1
                self.f_time = time.time()
                self.lst_changed = time.time()
                map_log.info(f"地图{self.now_map}已完成,相似度{self.now_map_sim},进入{self.floor+1}层")
            else:
                if self.ts.sim("黑塔"):
                    self.quit = time.time()
                self.mini_state += 2
        return ava

    # 寻路函数
    def get_direc(self):
        gray = np.array([55, 55, 55])
        blue = np.array([234, 191, 4])
        white = np.array([210, 210, 210])
        sred = np.array([49, 49, 140])
        yellow = np.array([145, 192, 220])
        black = np.array([0, 0, 0])
        shape = (int(self.scx * 190), int(self.scx * 190))
        bw_map = self.get_bw_map(gs=0)
        self.loc_off = 0
        tm = time.time()
        self.get_loc(bw_map, rg = 40 - self.find * 10)
        if self.find == 1:
            self.press("w", 0.2)
        self.get_screen()
        local_screen = self.get_local(0.9333, 0.8657, shape)
        # 录图模式，将小地图覆盖到录制的大地图中
        if self.find == 0:
            self.write_map(bw_map)
            self.get_map()
        # 寻路模式
        else:
            self.ang = 360 - self.get_now_direc(local_screen) - 90
            self.get_real_loc()
            loc, type = self.get_tar()
            # 当前坐标与目标点连成的直线的斜率（大概）
            ang = (
                math.atan2(loc[0] - self.real_loc[0], loc[1] - self.real_loc[1])
                / math.pi
                * 180
            )
            # 视角需要旋转的角度
            sub = ang - self.ang
            while sub < -180:
                sub += 360
            while sub > 180:
                sub -= 360
            self.mouse_move(sub)
            self.ang = ang
            ps = [13,9,11,7]
            # 如果当前就在交互点上：直接返回
            if self.goodf() and not self.ts.sim("黑塔"):
                for j in deepcopy(self.target):
                    if j[1] == 2:
                        self.target.remove(j)
                        log.info("removed:" + str(j))
                return
            if self._stop == 0:
                keyops.keyDown("w")
            time.sleep(0.25)
            sft = 0
            if sft == 0 and type != 3:
                self.press('shift')
                sft = 1
            time.sleep(0.25)
            bw_map = self.get_bw_map()
            self.get_loc(bw_map, rg=30, offset=self.get_offset(4))
            self.get_real_loc(1)
            # 复杂的定位、寻路过程
            ds = self.get_dis(self.real_loc, loc)
            dls = [100000]
            dtm = [time.time()]
            t = 2
            for i in range(3000):
                if self._stop == 1:
                    keyops.keyUp("w")
                    return
                ctm = time.time()
                bw_map = self.get_bw_map()
                self.get_loc(bw_map, fbw=1, offset=self.get_offset(2+(i<=2)), rg=10+6*(i<=2))
                self.get_real_loc(2)
                ang = (
                    math.atan2(loc[0] - self.real_loc[0], loc[1] - self.real_loc[1])
                    / math.pi
                    * 180
                )
                sub = ang - self.ang
                while sub < -180:
                    sub += 360
                while sub > 180:
                    sub -= 360
                self.mouse_move(sub)
                self.ang = ang
                if self.debug:
                    self.big_map[
                        self.real_loc[0] - 1 : self.real_loc[0] + 2,
                        self.real_loc[1] - 1 : self.real_loc[1] + 2,
                    ] = 49
                    # 轨迹图
                    cv.imwrite("imgs/bigmap.jpg", self.big_map)
                nds = self.get_dis(self.real_loc, loc)
                # 1秒内没有离目标点更近：开始尝试绕过障碍
                if dls[0] <= nds:
                    ts = " da"
                    if t > 0:
                        keyops.keyUp("w")
                        self.press("s", 0.35)
                        self.press(ts[t], 0.2*random.randint(1,3))
                        if self._stop == 0:
                            keyops.keyDown("w")
                        bw_map = self.get_bw_map()
                        self.get_loc(bw_map, rg=28, fbw=1)
                        local_screen = self.get_local(0.9333, 0.8657, shape)
                        self.ang = 360 - self.get_now_direc(local_screen) - 90
                        t -= 1
                        dls = [100000]
                        dtm = [time.time()]
                        self.press('shift')
                        sft = 1
                    else:
                        keyops.keyUp("w")
                        break
                if nds <= ps[type]:
                    if type == 0:
                        dls = [100000]
                        dtm = [time.time()]
                        self.target.remove((loc, type))
                        log.info("removed:" + str((loc, type)))
                        self.lst_changed = time.time()
                        loc, type = self.get_tar()
                        if type == 3:
                            self.press('shift')
                            sft = 0
                        ds = self.get_dis(self.real_loc, loc)
                        t = 2
                    else:
                        keyops.keyUp("w")
                        break
                else:
                    self.get_screen()
                    if type == 3 and self.check("f", 0.4443, 0.4417, mask="mask_f1"):
                        self.press('f')
                        keyops.keyUp("w")
                        if self.nof(must_be='tp'):
                            log.info('大图识别到传送点!')
                            return
                    elif (type != 3 and self.goodf()) or not self.isrun():
                        keyops.keyUp("w")
                        break
                ds = nds
                dls.append(ds)
                dtm.append(time.time())
                while dtm[0] < time.time() - 1.7 + sft * 1:
                    dtm = dtm[1:]
                    dls = dls[1:]
            log.info(f"进入新地图或者进入战斗 {nds}")
            if type == 0:
                self.lst_tm = time.time()
            if type == 1:
                if self._stop == 0:
                    pyautogui.click()
                time.sleep(1.1)
                self.press("s")
                if self._stop == 0:
                    pyautogui.click()
                time.sleep(0.8)
                if len(self.target) <= 2:
                    time.sleep(0.3)
                    self.press("s")
                    pyautogui.click()
                    time.sleep(0.6)
                    self.press("s", 0.5)
                    pyautogui.click()
                    time.sleep(0.5)
                    self.press("w", 1.6)
                    pyautogui.click()
            if type == 3:
                for i in range(9):
                    self.get_screen()
                    if self.check("f", 0.4443, 0.4417, mask="mask_f1"):
                        log.info("大图识别到传送点")
                        self.press('f')
                        if self.nof(must_be='tp'):
                            time.sleep(1.5)
                            break
                    self.get_screen()
                    if self.isrun():
                        if i in [0,4]:
                            self.move_to_end()
                        self.press('w', 0.5)
                        time.sleep(0.2)
            # 离目标点挺近了，准备找下一个目标点
            elif nds <= 20:
                try:
                    self.target.remove((loc, type))
                    log.info("removed:" + str((loc, type)))
                    self.lst_changed = time.time()
                except:
                    pass

    # 视角转动x度
    def mouse_move(self, x, fine=1):
        if x > 30 // fine:
            y = 30 // fine
        elif x < -30 // fine:
            y = -30 // fine
        else:
            y = x
        dx = int(16.5 * y * self.multi * self.scale)
        if self._stop == 0 and self.stop_move == 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        time.sleep(0.05 * fine)
        if x != y:
            if self._stop == 0:
                self.mouse_move(x - y, fine)
            else:
                raise ValueError("正在退出")

    # 在大地图中覆盖小地图
    def write_map(self, bw_map):
        for i in range(bw_map.shape[0]):
            for j in range(bw_map.shape[1]):
                if ((i - 88) ** 2 + (j - 88) ** 2) > 80**2:
                    bw_map[i, j] = 0
                # 如果小地图的当前像素点是白线，在大地图的对应像素点增加权重
                if bw_map[i, j] == 255:
                    if (
                        self.big_map[self.now_loc[0] - 88 + i, self.now_loc[1] - 88 + j]
                        < 250
                    ):
                        self.big_map[
                            self.now_loc[0] - 88 + i, self.now_loc[1] - 88 + j
                        ] += 50

    # 移动后根据旧坐标获得新坐标（匹配）
    # rg：匹配的范围（以旧坐标为中心） fbw：是否进行缩放
    # fbw：（人物静止/移动时小地图会有个缩放的过程，fbw=0表示当前人物是静止状态，因此缩放到移动状态与大地图匹配）ps：大地图是移动状态录制的
    def get_loc(self, bw_map, rg=10, fbw=0, offset=None):
        rge = 88 + rg
        loc_big = np.zeros((rge * 2, rge * 2), dtype=self.big_map.dtype)
        tpl = (self.now_loc[0], self.now_loc[1])
        if offset is not None:
            tpl = (tpl[0]+int(offset[0]),tpl[1]+int(offset[1]))
        x0, y0 = max(rge - tpl[0], 0), max(rge - tpl[1], 0)
        x1, y1 = max(tpl[0] + rge - self.big_map.shape[0], 0), max(
            tpl[1] + rge - self.big_map.shape[1], 0
        )
        # 从大地图中截取对应部分
        loc_big[x0 : rge * 2 - x1, y0 : rge * 2 - y1] = self.big_map[
            tpl[0] - rge + x0 : tpl[0] + rge - x1, tpl[1] - rge + y0 : tpl[1] + rge - y1
        ]
        max_val, max_loc = -1, 0
        bo_1 = bw_map == 255
        tt = 4
        kernel = np.zeros((5, 5), np.uint8)
        kernel += 1
        if self.find and fbw == 0:
            tbw = cv.resize(bw_map, (176 + tt * 2, 176 + tt * 2))
            tbw[tbw > 150] = 255
            tbw[tbw <= 150] = 0
            tbw = tbw[tt : 176 + tt, tt : 176 + tt]
            bo_2 = tbw == 255
            b_map = cv.dilate(tbw, kernel, iterations=1)
            bo_5 = (b_map != 0) & (bo_2 == 0)
        bo_3 = loc_big >= 50
        b_map = cv.dilate(bw_map, kernel, iterations=1)
        bo_4 = (b_map != 0) & (bo_1 == 0)
        # 枚举匹配，找到匹配点最多的坐标
        for i in range(rge * 2 - 176):
            for j in range(rge * 2 - 176):
                if (i - rge + 88) ** 2 + (j - rge + 88) ** 2 > rg**2:
                    continue
                p = 2*np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_1)
                p += np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_4)
                if p > max_val:
                    max_val = p
                    max_loc = (i, j)
                    if self.debug == 2:
                        tmp = np.zeros((176,176), dtype=np.uint8)
                        tpp = bo_3[i : i + 176, j : j + 176]
                        tmp[tpp!=0]=255
                        tmp[bo_1!=0]=150
                        tmp[bo_4!=0]=50
                if self.find and fbw == 0:
                    p = 2*np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_2)
                    p += np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_5)
                    if p > max_val:
                        max_val = p
                        max_loc = (i, j)
        if max_val != 0:
            self.now_loc = (
                max_loc[0] + 88 - rge + self.now_loc[0],
                max_loc[1] + 88 - rge + self.now_loc[1],
            )
        if self.debug == 2:
            cv.imwrite('tp/'+str(time.time())+'.jpg',tmp)

    def get_real_loc(self,delta=0):
        x, y = self.now_loc
        dx, dy = self.get_offset(delta=delta)
        self.real_loc = (int(x+10+dx),int(y+dy))

    def get_offset(self,delta=1):
        pi = 3.141592653589
        dx, dy = sin(self.ang/180*pi), cos(self.ang/180*pi)
        return (delta*dx*3,delta*dy*3)

    # 从8192*8192的超大地图中找到有意义的大地图
    def get_map(self):
        x1, x2, y1, y2 = 0, 8191, 0, 8191
        while x1 < 8192 and np.sum(self.big_map[x1, :]) == 0:
            x1 += 1
        while y1 < 8192 and np.sum(self.big_map[:, y1]) == 0:
            y1 += 1
        while x2 > 0 and np.sum(self.big_map[x2, :]) == 0:
            x2 -= 1
        while y2 > 0 and np.sum(self.big_map[:, y2]) == 0:
            y2 -= 1
        if x1 >= x2 or y1 >= y2:
            return
        # 权重得大于一个值，才能被判定为白线（否则是噪声）
        tp = deepcopy(self.big_map[x1 - 1 : x2 + 2, y1 - 1 : y2 + 2])
        tp[tp >= 100] = 255
        bk = deepcopy(tp)
        for i in range(tp.shape[0]):
            for j in range(tp.shape[1]):
                f = 0
                for ii in range(0, 1):
                    for jj in range(0, 1):
                        if (
                            i + ii >= 0
                            and j + jj >= 0
                            and i + ii < tp.shape[0]
                            and j + jj < tp.shape[1]
                        ):
                            if bk[i + ii, j + jj] == 255:
                                f = 1
                                break
                if f:
                    tp[i, j] = 255
        tp[tp < 100] = 0
        cv.imwrite(
            self.map_file + "map_" + str(x1 - 1) + "_" + str(y1 - 1) + "_.jpg", tp
        )
        cv.imwrite(self.map_file + "target.jpg", tp)

    def extract_features(self, img):
        img = img[50:-50,50:-50,:]
        orb = cv.ORB_create()
        # 检测关键点和计算描述符
        keypoints, descriptors = orb.detectAndCompute(img, None)
        return descriptors

    def match_two(self, img1, img2):
        key1 = self.extract_features(img1)
        key2 = self.extract_features(img2)
        matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(key1, key2)
        similarity_score = len(matches) / max(len(key1), len(key2))
        log.info(f"相似度：{similarity_score}")
        return

    # 匹配地图，找到最相似的地图，确定当前房间对应的地图
    def match_scr(self, img):
        key = self.extract_features(img)
        img = self.get_bw_map(gs=0,local_screen=img)
        sim = -1
        ans = -1
        matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        res = []
        for i, j in self.img_set:
            try:
                matches = matcher.match(key, j)
                similarity_score = len(matches) / max(len(key), len(j))
                res.append((similarity_score,i))
            except:
                pass
        res = sorted(res, key=lambda x: x[0])[-3:]
        try:
            if res[-1][0]>res[-2][0]+0.065 and (res[-1][0]>0.4 or self.debug!=2):
                return res[-1][1], 0.9
        except:
            return -1, -1
        i_s = [x[1] for x in res]
        for i in i_s[::-1]:
            bw_j = self.get_bw_map(gs=0,local_screen=self.img_map[i])
            big_bw_j = np.zeros((bw_j.shape[0]+28,bw_j.shape[1]+28),dtype=bw_j.dtype)
            big_bw_j[14:-14,14:-14] = bw_j
            result = cv.matchTemplate(big_bw_j, img, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val > sim:
                sim = max_val
                ans = i
        return ans, sim

    def get_dis(self, x, y):
        return ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5

    # 找小地图中怪点，已弃用
    def check_sred(self, sred, loc_scr, i, j):
        for k in range(max(0, i - 2), min(i + 2, loc_scr.shape[0])):
            for t in range(max(0, j - 2), min(j + 2, loc_scr.shape[1])):
                if not (sred == loc_scr[k, t]).all():
                    return 0
        return 1

    def print_stack(self, num=1):
        if self.debug:
            stk = traceback.extract_stack()
            for i in range(num):
                try:
                    print(stk[-2].name,stk[-3-i].filename.split('\\')[-1].split('.')[0],stk[-3-i].name,stk[-3-i].lineno)
                except:
                    pass

    def check_auto(self):
        auto = self.check("z", 0.0878,0.9630, large=False, mask="mask_auto")
        cvt = cv.cvtColor(auto, cv.COLOR_BGR2HSV)
        lower = np.array([22, 58, 100])
        upper = np.array([26, 100, 255])
        mask = cv.inRange(cvt, lower, upper)
        result = np.sum(mask)//255
        return result > 180 and result < 280
    
    def isrun(self):
        scr = self.screen
        shape = (int(self.scx * 12), int(self.scx * 12))
        loc_scr = self.get_local(0.9333, 0.8657, shape)
        hsv = cv.cvtColor(loc_scr, cv.COLOR_BGR2HSV)  # 转HSV
        lower = np.array([93, 120, 60])  # 90 改成120只剩箭头，但是角色移动过的印记会消失
        upper = np.array([97, 255, 255])
        mask = cv.inRange(hsv, lower, upper)  # 创建掩膜
        sum = np.sum(mask)
        scr_bak = deepcopy(scr)
        scr[np.min(scr,axis=-1)<=220]=[0,0,0]
        scr[np.min(scr,axis=-1)>220]=[255,255,255]
        res = self.check('run',0.876,0.7815,threshold=0.91) and sum > 40000 and sum < 65000
        if self.tm>0.96:
            res = 1
        self.screen = deepcopy(scr_bak)
        if res:
            self.f_time = 0
        return res

    def get_direc_only_minimap(self):
        if self.debug==2:
            print('mini',self.ang_off,self.mini_state)
        self.ang_neg=self.ang_off<0
        if self.ang_off:
            time.sleep(0.6)
            self.mouse_move(-self.ang_off*1.2)
            time.sleep(0.3)
            self.press('w',0.3)
        if self.mini_state==1 and self.floor in [4,8,11]:
            time.sleep(0.5)
            self.press('w',0.55)
            pyautogui.click()
            time.sleep(1.2)
            self.press('w')
            time.sleep(0.4)
        if self.mini_state==3 and self.floor==12 and not self.check_bonus:
            self.mini_state+=2
            return
        if self.mini_state==3 and self.floor in [3,7,12] and self.check_bonus:
            self.press('d',0.4)
            keyops.keyDown('w')
            nt = time.time()
            while time.time()-nt<1.3:
                self.get_screen()
                if self.check("f", 0.4443, 0.4417, mask="mask_f1"):
                    self.press('f')
                    keyops.keyUp('w')
                    break
            keyops.keyUp('w')
            self.press('f')
            time.sleep(1)
            for _ in range(2):
                if not self.check_bonus:
                    break
                self.get_screen()
                if self.check('bonus_c',0.2385,0.6685):
                    self.click((0.4453,0.3250))
                    time.sleep(0.5)
                    self.get_screen()
                    if self.check("yes1", 0.5, 0.5, mask="mask_end"):
                        self.check_bonus = 0
                    self.click((0.5062, 0.1454))
                    time.sleep(1.2)
            keyops.keyUp('w')
            self.get_screen()
            if self.check('bonus_c',0.2385,0.6685):
                self.click((0.2385,0.6685))
            self.mini_state+=2
            if self.floor==12:
                return
            self.press('s',0.4)
        self.ang_off=0
        self.stop_move=0
        self.ready=0
        self.mini_target=0
        self.get_screen()
        self.is_target=0
        first = self.first_mini
        threading.Thread(target=self.move_thread).start()
        while not self.ready:
            time.sleep(0.1)
        if not self.ang_off and self.mini_state == 1:
            if self.check("z",0.5906,0.9537,mask="mask_z",threshold=0.95):
                if self.floor == 11:
                    self.floor = 12
        keyops.keyDown("w")
        wt = 3
        self.first_mini = 0
        sft = 0
        if self.mini_state==1:
            wt += 1
            if self.mini_target!=2:
                self.press('shift')
                sft = 1
            if self.mini_target==1:
                wt += 0.8
        need_confirm=0
        init_time = time.time()
        while True:
            self.get_screen()
            if self._stop == 1:
                keyops.keyUp("w")
                self.stop_move=1
                break
            if self.mini_target==1:
                if self.check("f", 0.4443, 0.4417, mask="mask_f1"):
                    self.press('f')
                    log.info('发现事件交互')
                    self.stop_move=1
                    need_confirm = 1
                    if self.nof(must_be='event'):
                        keyops.keyUp("w")
                        return
                    break
            else:
                if self.goodf() and not (self.ts.sim("黑塔") and time.time() - self.quit < 30):
                    self.press('f')
                    log.info('need_confirm '+self.ts.text)
                    self.stop_move=1
                    need_confirm = 1
                    if self.nof():
                        keyops.keyUp("w")
                        return
                    break
                if self.check("auto_2", 0.0583, 0.0769): 
                    keyops.keyUp("w")
                    self.stop_move=1
                    self.mini_state+=2
                    break
                if self.check("z",0.5906,0.9537,mask="mask_z",threshold=0.95):
                    self.stop_move=1
                    time.sleep(1.7)
                    if self.mini_state==1 and self.floor==12:
                        keyops.keyUp("w")
                        for i in range(4):
                            self.press(str(i+1))
                            time.sleep(0.4)
                            self.press('e')
                            time.sleep(1.5)
                            self.get_screen()
                            if not self.check("z",0.5906,0.9537,mask="mask_z",threshold=0.95):
                                break
                            if self._stop:
                                break
                        keyops.keyDown("w")
                    iters = 0
                    while self.check("z",0.5906,0.9537,mask="mask_z",threshold=0.95) and not self._stop:
                        iters+=1
                        if iters>4:
                            break
                        pyautogui.click()
                        if iters == 2:
                            time.sleep(0.6)
                            self.press('d',0.85)
                            self.press('a',0.3)
                        else:
                            time.sleep(0.9)
                        self.get_screen()
                    self.mini_state+=2
                    break
            if time.time()-init_time>wt:
                self.stop_move=1
                keyops.keyUp("w")
                self.mini_state+=2
                if self.mini_state>=7:
                    self.lst_changed = 0
                    return
                self.press('s',0.3)
                self.press('a',0.7)
                self.press('d',0.45)
                self.press('w',0.5)
                break
            time.sleep(0.1)
        self.stop_move=1
        keyops.keyUp("w")
        if need_confirm or (first and self.mini_target!=2):
            for i in "sasddwwaa":
                if self._stop:
                    return
                self.get_screen()
                if self.mini_target==1:
                    if self.check("f", 0.4443, 0.4417, mask="mask_f1"):
                        self.press('f')
                        if self.nof(must_be='event'):
                            return
                elif self.goodf() and not (self.ts.sim("黑塔") and time.time() - self.quit < 30):
                    self.press('f')
                    if self.nof():
                        return
                self.press(i, 0.25)
                time.sleep(0.4)
            pyautogui.click()