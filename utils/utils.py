import pyautogui
import cv2 as cv
import numpy as np
import time

import pywintypes
import win32api
import win32gui
import win32print
import win32con
from copy import deepcopy
import math
import random
import win32gui, win32com.client, pythoncom
import os
import threading

from utils.config import config
from utils.log import log


def notif(title,msg,cnt=None):
    if cnt is not None:
        tm=str(time.time())
    else:
        tm=None
    if os.path.exists('logs/notif.txt'):
        with open('logs/notif.txt','r', encoding="utf-8") as fh:
            s=fh.readlines()
            try:
                cnt=s[0].strip('\n')
                if tm is None:
                    tm=s[3].strip('\n')
            except:
                pass
    os.makedirs('logs',exist_ok=1)
    if cnt is None:
        cnt = '0'
    if tm is None:
        tm=str(time.time())
    with open('logs/notif.txt','w', encoding="utf-8") as fh:
        fh.write(cnt+'\n'+title+'\n'+msg+'\n'+tm)

# 将游戏窗口设为前台
def set_forground():
    config.read()
    try:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys(" ")  # Undocks my focus from Python IDLE
        game_nd = win32gui.FindWindow("UnityWndClass", "崩坏：星穹铁道")
        win32gui.SetForegroundWindow(game_nd)
    except:
        pass


class UniverseUtils:
    def __init__(self):
        self.my_nd = win32gui.GetForegroundWindow()
        set_forground()
        self._stop = 0
        self.opt = 0
        self.multi = config.multi
        self.diffi = config.diffi
        self.fate = config.fate
        self.my_fate = 4
        # 用户选择的命途
        for i in range(len(config.fates)):
            if config.fates[i] == self.fate:
                self.my_fate = i
        # 是否对命途回响构音做出优化，目前支持存护和巡猎
        if self.my_fate in [0, 4]:
            self.opt = 1
        self.debug, self.find = 0, 1
        self.bx, self.by = 1920, 1080
        log.warning("等待游戏窗口")
        self.ts = 'ey.jpg'
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetClientRect(hwnd)
                self.xx = self.x1 - self.x0
                self.yy = self.y1 - self.y0
                self.x0, self.y0, self.x1, self.y1 = win32gui.GetWindowRect(hwnd)
                self.full = self.x0 == 0 and self.y0 == 0
                self.x0 = max(0, self.x1 - self.xx)
                self.y0 = max(0, self.y1 - self.yy)
                self.scx = self.xx / self.bx
                self.scy = self.yy / self.by
                dc = win32gui.GetWindowDC(hwnd)
                dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
                dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
                win32gui.ReleaseDC(hwnd, dc)
                scale_x = dpi_x / 96
                scale_y = dpi_y / 96
                # 计算出真实分辨率
                self.real_width = int(self.xx * scale_x)
                # x01y01:窗口左上右下坐标
                # xx yy:窗口大小
                # scx scy:当前窗口和基准窗口（1920*1080）缩放大小比例
                if Text == "崩坏：星穹铁道":
                    time.sleep(1)
                    break
                else:
                    time.sleep(0.3)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                time.sleep(0.3)
        self.order = config.order

    def press(self, c, t=0):
        log.debug(f"按下按钮 {c}，等待 {t} 秒后释放")
        if self._stop == 0:
            pyautogui.keyDown(c)
        time.sleep(t)
        pyautogui.keyUp(c)

    def get_point(self, x, y):
        # 得到一个点的浮点表示
        x = self.x1 - x
        y = self.y1 - y
        log.debug("获取到点：{:.4f},{:.4f}".format(x / self.xx, y / self.yy))

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
    def click(self, points):
        x, y = points
        # 如果是浮点数表示，则计算实际坐标
        if type(x) != type(0):
            x, y = self.x1 - int(x * self.xx), self.y1 - int(y * self.yy)
        # 全屏模式会有一个偏移
        if self.full:
            x += 11
            y += 11
        if self._stop == 0:
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.3)
        if self._stop == 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.5)

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
    def get_local(self, x, y, size):
        sx, sy = size[0] + 60, size[1] + 60
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
    def check(self, path, x, y, mask=None, threshold=None):
        if threshold is None:
            threshold = self.threshold
        path = self.format_path(path)
        target = cv.imread(path)
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
        local_screen = self.get_local(x, y, shape)
        if path == "./imgs/f.jpg":
            cv.imwrite("imgs/tmp.jpg", local_screen)
            cv.imwrite("imgs/tmp1.jpg", target)
        result = cv.matchTemplate(local_screen, target, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # print(max_loc,target.shape,max_val,local_screen.shape)
        self.tx = x - (max_loc[0] - 0.5 * local_screen.shape[1]) / self.xx
        self.ty = y - (max_loc[1] - 0.5 * local_screen.shape[0]) / self.yy
        self.tm = max_val
        if max_val > threshold and path != "./imgs/run.jpg" and path != "./imgs/auto_2.jpg":
            log.info("匹配到图片 %s 相似度 %f 阈值 %f" % (path, max_val, threshold))
        return max_val > threshold

    def get_end_point(self,mask=0):
        self.get_screen()
        local_screen = self.get_local(0.4979,0.6296, (715, 1399))
        black = np.array([0, 0, 0])
        white = np.array([255, 255, 255])
        bw_map = np.zeros(local_screen.shape[:2], dtype=np.uint8)
        b_map = deepcopy(bw_map)
        b_map[np.sum((local_screen - black) ** 2, axis=-1) <= 1600]=255
        w_map = deepcopy(bw_map)
        w_map[np.sum((local_screen - white) ** 2, axis=-1) <= 1600]=255
        kernel = np.zeros((7,7),np.uint8)              #设置kenenel大小
        kernel += 1
        b_map = cv.dilate(b_map,kernel,iterations=1)   # 膨胀还原图形
        bw_map[(b_map>200) & (w_map>200)]=255
        cen = 660
        if mask:
            try:
                bw_map[:,:cen-250//mask]=0
                bw_map[:,cen+250//mask:]=0
            except:
                pass
        region = cv.imread('imgs/region.jpg',cv.IMREAD_GRAYSCALE)
        result = cv.matchTemplate(bw_map, region, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val<0.6:
            return None
        else:
            dx=max_loc[0]-cen
            if dx>0:
                return dx**0.7
            else:
                return -((-dx)**0.7)
        
    def move_to_end(self,i=0):
        dx=self.get_end_point(i)
        if dx is None:
            if i:
                return 0
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -200)
            time.sleep(0.5)
            dx=self.get_end_point()
            off = 0
            if dx is None:
                for k in range(8):
                    if self.ang_neg:
                        self.mouse_move(45)
                        off-=45
                    else:
                        self.mouse_move(-45)
                        off+=45
                    time.sleep(0.5)
                    dx=self.get_end_point()
                    if dx is not None:
                        break
                while off>180:
                    off-=360
                while off<-180:
                    off+=360
                if dx is None:
                    self.mouse_move(off)
                    self.press('a',1.4)
                    self.press('d',0.7)
                    return 0
        if not self.stop_move:
            if i==0:
                self.mouse_move(dx/2)
            else:
                self.mouse_move(dx/3)
        if i==0:
            time.sleep(0.5)
            dx=self.get_end_point(1)
            if dx is not None:
                self.mouse_move(dx/2.5)
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
        screen_raw = pyautogui.screenshot()
        screen_raw = np.array(screen_raw)
        screen_raw = screen_raw[self.y0 : self.y1, self.x0 : self.x1, :]
        if self.full:
            screen_raw[:-11, :-11] = screen_raw[11:, 11:]
        self.screen = cv.cvtColor(screen_raw, cv.COLOR_BGR2RGB)
        # cv.imwrite("imgs/screen.jpg", self.screen)
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
    # gs：是否重新截图 sbl：是否识别最近的轨迹点
    def get_bw_map(self, gs=1, sbl=0):
        yellow = np.array([145, 192, 220])
        black = np.array([0, 0, 0])
        white = np.array([210, 210, 210])
        sblue = np.array([222, 198, 121])
        gray = np.array([55, 55, 55])
        shape = (int(self.scx * 190), int(self.scx * 190))
        if gs:
            self.get_screen()
        local_screen = self.get_local(0.9333, 0.8657, shape)
        bw_map = np.zeros(local_screen.shape[:2], dtype=np.uint8)
        # 灰块、白线：小地图中的可移动区域、可移动区域的边缘
        # b_map：当前像素点是否是灰块。只允许灰块附近（2像素）的像素被识别为白线
        b_map = deepcopy(bw_map)
        b_map[np.sum((local_screen - gray) ** 2, axis=-1) <= 3200 + self.find * 1600]=255
        blk_map = deepcopy(bw_map)
        blk_map[np.sum((local_screen - black) ** 2, axis=-1) <= 800 + self.find * 800]=255
        kernel = np.zeros((9,9),np.uint8)              #设置kenenel大小
        kernel += 1
        dilate = cv.dilate(blk_map,kernel,iterations=1) # 膨胀还原图形
        kernel = np.zeros((5,5),np.uint8)              #设置kenenel大小
        kernel += 1
        b_map = cv.dilate(b_map,kernel,iterations=1)
        # 黄色：包括小地图中的交互点、传送点
        bw_map[
            (np.sum((local_screen - yellow) ** 2, axis=-1) <= 800 + self.find * 800)
            & (dilate>200)
        ] = 200
        bw_map[
            (np.sum((local_screen - white) ** 2, axis=-1) <= 3200 + self.find * 1600)
            & (b_map>200)
        ] = 255
        if sbl:
            bw_map[np.sum((local_screen - sblue) ** 2, axis=-1) <= 400] = 150
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
        # 识别淡蓝色轨迹点：小地图中人物移动时留下的一串轨迹
        # 很多时候小地图中心点不是人物坐标，似乎有一个偏移量，所以通过识别最近的淡蓝色轨迹点确定人物0.3秒前的坐标，计算偏移量
        # 这里的偏移量存疑，但是不加就是会出问题
        if sbl:
            ii, jj = 30, 30
            cv.imwrite("imgs/sbl.jpg", bw_map)
            for i in range(-20, 21):
                for j in range(-20, 21):
                    if (
                        bw_map[88 + i, 88 + j] == 150
                        and i**2 + j**2 < ii**2 + jj**2
                    ):
                        ii, jj = i, j
            bw_map[bw_map == 150] = 0
            if ii**2 + jj**2 < self.his_loc[0] ** 2 + self.his_loc[1] ** 2:
                self.his_loc = (ii, jj)
        bw_map[bw_map == 200] = 255
        if self.find == 0:
            cv.imwrite(self.map_file + "bwmap.jpg", bw_map)
        return bw_map

    # 计算小地图中蓝色箭头的角度
    def get_now_direc(self, loc_scr):
        blue = np.array([234, 191, 4])
        arrow = self.format_path("loc_arrow")
        arrow = cv.imread(arrow)
        loc_tp = deepcopy(loc_scr)
        loc_tp[np.sum(np.abs(loc_tp - blue), axis=-1) > 0] = [0, 0, 0]
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
        while not self.check("run", 0.9844, 0.7889, threshold=0.93):
            time.sleep(0.1)
            self.get_screen()
        time.sleep(1)
        self.press('m',0.2)
        time.sleep(2.5)
        self.get_screen()
        for i in range(12,0,-1):
            if self.check("floor/ff" + str(i + 1),0.0635,0.8917):
                self.floor=i
                log.info(f"当前层数：{i+1}")
                self.floor_init=1
                break
        self.press('m',0.2)
        time.sleep(1)

    def goodf(self):
        is_killed = (
            self.check("bonus", 0.3531,0.4250)
            or self.check("rescure", 0.3578,0.4333)
            or self.check("download", 0.3578,0.4333)
        )
        return self.check("f", 0.3891,0.4315) and not is_killed

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

    def move_to_interac(self, i=0):
        self.get_screen()
        threshold=0.84
        shape = (int(self.scx * 190), int(self.scx * 190))
        curloc = (118, 125)
        blue = np.array([234, 191, 4])
        local_screen = self.get_local(0.9333, 0.8657, shape)
        target = ((-1, -1), 0)
        nearest = (-1, -1)
        minicon = cv.imread(self.format_path("mini"+str(i+1)))
        sp = minicon.shape
        result = cv.matchTemplate(local_screen, minicon, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if (max_val > threshold):
            nearest = (max_loc[1] + sp[0] // 2, max_loc[0] + sp[1] // 2)
            target = (nearest, 2)
            log.info(
                f"交互点相似度{max_val}，位置{max_loc[1]},{max_loc[0]}"
            )
        else:#226 64 66
            minicon = cv.imread(self.format_path("mini"+str(i+2)))
            sp = minicon.shape
            result = cv.matchTemplate(local_screen, minicon, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if (max_val > threshold):
                nearest = (max_loc[1] + sp[0] // 2, max_loc[0] + sp[1] // 2)
                target = (nearest, 3)
                log.info(
                    f"黑塔相似度{max_val}，位置{max_loc[1]},{max_loc[0]}"
                )
        if max_val <= threshold:
            red = [60,60,226]
            rd = np.where(np.sum((local_screen-red)**2,axis=-1)<=512)
            if rd[0].shape[0]>0:
                nearest = (rd[0][0],rd[1][0])
                target = (nearest, 3)

        if (target[1] >= 1):
            local_screen[np.sum(np.abs(local_screen - blue), axis=-1) <= 150] = blue
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
            if self.stop_move:
                sub=0
            if i==0:
                if self.ang_off==0:
                    sub*=1.2
                else:
                    sub=0
            self.mouse_move(sub)
            return sub
        else:
            return 0
        
    def move_thread(self):
        me=0
        if self.mini_state>2:
            me=self.move_to_end()
        else:
            self.ang_off+=self.move_to_interac(2)
        self.ready=1
        now_time=time.time()
        if me==0:
            me=0.5
        while not self.stop_move and time.time()-now_time<3:
            if self.mini_state<=2:
                self.ang_off+=self.move_to_interac()
            else:
                me=max(self.move_to_end(me),me)

    def get_direc_only_minimap(self):
        if self.ang_off:
            self.ang_neg=self.ang_off<0
            self.mouse_move(-self.ang_off*1.2)
            time.sleep(0.7)
        self.ang_off=0
        self.stop_move=0
        self.ready=0
        self.get_screen()
        threading.Thread(target=self.move_thread).start()
        while not self.ready:
            time.sleep(0.1)
        pyautogui.keyDown("w")
        if self.mini_state==1:
            time.sleep(0.7)
        need_confirm=0
        init_time = time.time()
        while True:
            self.get_screen()
            if self._stop == 1:
                pyautogui.keyUp("w")
                self.stop_move=1
                break
            if self.goodf() and not (self.check("quit", 0.3552,0.4343) and time.time() - self.quit < 30): 
                pyautogui.keyUp("w")
                self.stop_move=1
                need_confirm = 1
                break
            if self.check("auto_2", 0.3760, 0.0370): 
                self.stop_move=1
                self.mini_state+=2
                break
            if self.check("z",0.5906,0.9537,mask="mask_z"):
                self.stop_move=1
                time.sleep(2.1)
                while self.check("z",0.5906,0.9537,mask="mask_z"):
                    pyautogui.click()
                    self.press("w",0.5)
                    self.get_screen()
                self.mini_state+=2
                break
            if time.time()-init_time>2.5:
                self.stop_move=1
                pyautogui.keyUp("w")
                self.mini_state+=2
                pyautogui.click()
                break
        self.stop_move=1
        if need_confirm:
            time.sleep(0.5)
            for i in "sasddwwaa":
                if self._stop:
                    return
                time.sleep(0.4)
                self.get_screen()
                if self.goodf() and not (self.check("quit", 0.3552,0.4343) and time.time() - self.quit < 30):
                    self.mini_state+=2
                    return
                else:
                    self.press(i, 0.25)

    # 寻路函数
    def get_direc(self):
        gray = np.array([55, 55, 55])
        blue = np.array([234, 191, 4])
        white = np.array([210, 210, 210])
        sred = np.array([49, 49, 140])
        yellow = np.array([145, 192, 220])
        black = np.array([0, 0, 0])
        shape = (int(self.scx * 190), int(self.scx * 190))
        local_screen = self.get_local(0.9333, 0.8657, shape)
        local_screen[np.sum(np.abs(local_screen - blue), axis=-1) <= 150] = blue
        bw_map = self.get_bw_map(gs=0)
        self.loc_off = 0
        self.get_loc(bw_map, 40 - self.find * 15)
        # 录图模式，将小地图覆盖到录制的大地图中
        if self.find == 0:
            self.write_map(bw_map)
            self.get_map()
        # 寻路模式
        else:
            self.ang = 360 - self.get_now_direc(local_screen) - 90
            bl = 0
            if self.his_loc[0] == 30:
                bl = 1
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
            if bl == 0:
                self.mouse_move(sub)
                self.ang = ang
            if type == 1:
                ps = 8
            elif type == 0:
                ps = 6
            else:
                ps = 6
            if self.speed == 2 and type == 0:
                ps += 4
            # 如果当前就在交互点上：直接返回
            if self.goodf() and not self.check("quit", 0.3552,0.4343):
                for j in deepcopy(self.target):
                    if j[1] == type:
                        self.last = j[0]
                        self.target.remove(j)
                return
            if self._stop == 0:
                pyautogui.keyDown("w")
            time.sleep(0.5)
            ltm = time.time()
            bw_map = self.get_bw_map(sbl=bl)
            self.get_loc(bw_map, rg=18)
            sloc = self.real_loc
            # 复杂的定位、寻路过程
            ds = self.get_dis(self.real_loc, loc)
            dls = [100000]
            dtm = [time.time()]
            sds = ds
            td = 0
            t = 2
            sft = 1
            if self.speed == 2 and type != 3:
                self.press("shift")
            for i in range(3000):
                if self._stop == 1:
                    pyautogui.keyUp("w")
                    return
                ctm = time.time()
                bw_map = self.get_bw_map(sbl=(i <= 4 and bl))
                self.get_loc(bw_map, fbw=1)
                if i <= 4 and bl:
                    fx = 0.4 / (ctm - ltm) * (self.real_loc[0] - sloc[0])
                    fy = 0.4 / (ctm - ltm) * (self.real_loc[1] - sloc[1])
                    self.offset = (int(fx), int(fy))
                    # print(self.offset,self.his_loc)
                if i > 4 or bl == 0:
                    self.real_loc = (
                        self.real_loc[0] + self.his_loc[0] + self.offset[0],
                        self.real_loc[1] + self.his_loc[1] + self.offset[1],
                    )
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
                if i > 4 or bl == 0:
                    self.mouse_move(sub)
                    self.ang = ang
                self.big_map[
                    self.real_loc[0] - 1 : self.real_loc[0] + 2,
                    self.real_loc[1] - 1 : self.real_loc[1] + 2,
                ] = 49
                # 轨迹图
                cv.imwrite("imgs/bigmap.jpg", self.big_map)
                nds = self.get_dis(self.real_loc, loc)
                if nds < 18 and self.speed == 2 and type == 2 and sft:
                    self.press('shift')
                    sft = 0
                # 1秒内没有离目标点更近：开始尝试绕过障碍
                if dls[0] <= nds:
                    ts = " da"
                    if t > 0:
                        pyautogui.keyUp("w")
                        self.press("s", 0.35)
                        self.press(ts[t], 0.4)
                        if self._stop == 0:
                            pyautogui.keyDown("w")
                        bw_map = self.get_bw_map()
                        local_screen = self.get_local(0.9333, 0.8657, shape)
                        local_screen[
                            np.sum(np.abs(local_screen - blue), axis=-1) <= 150
                        ] = blue
                        self.ang = 360 - self.get_now_direc(local_screen) - 90
                        self.get_loc(bw_map, rg=28, fbw=1)
                        self.real_loc = (
                            self.real_loc[0] + self.his_loc[0] + self.offset[0],
                            self.real_loc[1] + self.his_loc[1] + self.offset[1],
                        )
                        t -= 1
                        dls = [100000]
                        dtm = [time.time()]
                        if self._stop == 0 and self.speed == 2:
                            self.press("shift")
                    else:
                        pyautogui.keyUp("w")
                        break
                if (
                    nds <= ps
                    or self.goodf()
                    or self.check("run", 0.9844, 0.7889, threshold=0.93) == 0
                ):
                    if nds <= ps and type == 0:
                        dls = [100000]
                        dtm = [time.time()]
                        self.target.remove((loc, type))
                        self.lst_changed = time.time()
                        loc, type = self.get_tar()
                        ds = self.get_dis(self.real_loc, loc)
                        t = 2
                    else:
                        pyautogui.keyUp("w")
                        break
                ds = nds
                dls.append(ds)
                dtm.append(time.time())
                while dtm[0] < time.time() - 1.5:
                    dtm = dtm[1:]
                    dls = dls[1:]
            log.info("进入新地图或者进入战斗")
            if type == 0:
                self.lst_tm = time.time()
            if type == 1:
                if self._stop == 0:
                    pyautogui.click()
                time.sleep(1)
                if self._stop == 0:
                    pyautogui.click()
                time.sleep(1)
                if len(self.target) <= 2:
                    self.press("s")
                    pyautogui.click()
                    time.sleep(0.6)
                    self.press("s", 0.5)
                    pyautogui.click()
                    time.sleep(0.6)
                    self.press("w")
                    pyautogui.click()
            if type == 2 or type == 3:
                # 接近交互点/传送点但是没出现交互按钮：开始绕当前点乱走
                key_list = ["sasddwwwaw", "sdsaawwwdw"]
                key = key_list[random.randint(0, len(key_list) - 1)]
                for i in range(-1, len(key)):
                    if self._stop:
                        return
                    time.sleep(0.4)
                    self.get_screen()
                    if self.goodf():
                        for j in deepcopy(self.target):
                            if j[1] == type:
                                self.last = j[0]
                                self.target.remove(j)
                                self.lst_changed = time.time()
                        break
                    else:
                        if i == -1:
                            if self._stop == 0:
                                pyautogui.click()
                            time.sleep(1.6)
                        else:
                            self.press(key[i], 0.25)
                # 多次找不到交互点，放弃寻找（不能放弃传送点）
                if type == 2:
                    self.tries += 1
                    if self.tries == 3:
                        try:
                            self.target.remove((loc, type))
                            self.lst_changed = time.time()
                        except:
                            pass
            # 离目标点挺近了，准备找下一个目标点
            elif nds <= 10 + (self.speed == 2) * 4:
                try:
                    self.target.remove((loc, type))
                    self.lst_changed = time.time()
                except:
                    pass
            elif self.check("run", 0.9844, 0.7889, threshold=0.93) == 0:
                try:
                    self.target.remove((loc, type))
                    if type != 0 and ds > 15:
                        self.target.add((loc, 0))
                    self.lst_changed = time.time()
                except:
                    pass

    # 视角转动x度
    def mouse_move(self, x):
        if x > 30:
            y = 30
        elif x < -30:
            y = -30
        else:
            y = x
        dx = int(9800 * y * 1295 / self.real_width / 180 * self.multi)
        if self._stop == 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        time.sleep(0.05)
        if x != y:
            self.mouse_move(x - y)

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
    # fbw：（人物静止/移动时小地图会有个缩放的过程，fbw=1表示当前人物是静止状态，因此缩放到移动状态与大地图匹配）ps：大地图是移动状态录制的
    def get_loc(self, bw_map, rg=8, fbw=0):
        rg += self.loc_off // 3
        rge = 88 + rg
        loc_big = np.zeros((rge * 2, rge * 2), dtype=self.big_map.dtype)
        tpl = (self.now_loc[0], self.now_loc[1])
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
        if self.find and fbw == 0:
            tbw = cv.resize(bw_map, (176 + tt * 2, 176 + tt * 2))
            tbw[tbw > 150] = 255
            tbw[tbw <= 150] = 0
            tbw = tbw[tt : 176 + tt, tt : 176 + tt]
            bo_2 = tbw == 255
        bo_3 = loc_big >= 50
        # 枚举匹配，找到匹配点最多的坐标
        for i in range(rge * 2 - 176):
            for j in range(rge * 2 - 176):
                if (i - rge + 88) ** 2 + (j - rge + 88) ** 2 > rg**2:
                    continue
                p = np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_1)
                if p > max_val:
                    max_val = p
                    max_loc = (i, j)
                if self.find and fbw == 0:
                    p = np.count_nonzero(bo_3[i : i + 176, j : j + 176] & bo_2)
                    if p > max_val:
                        max_val = p
                        max_loc = (i, j)
        lst = self.now_loc
        if max_val != 0:
            self.now_loc = (
                max_loc[0] + 88 - rge + self.now_loc[0],
                max_loc[1] + 88 - rge + self.now_loc[1],
            )
        # 如果旧坐标和新坐标一致：增加匹配范围
        if lst == self.now_loc:
            self.loc_off = min(self.loc_off + 1, 18)
        else:
            self.loc_off = 0
        self.real_loc = (self.now_loc[0], self.now_loc[1])

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
        sim = -1
        ans = -1
        matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        for i, j in self.img_set:
            try:
                matches = matcher.match(key, j)
                similarity_score = len(matches) / max(len(key), len(j))
                if similarity_score > sim:
                    sim = similarity_score
                    ans = i
            except:
                pass
        # or ans in ['75337','23480','52451','38866','47312','42250','19787','78566']
        #if sim<0.42 and self.debug == 2:
        #    time.sleep(1000000)
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
