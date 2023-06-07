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

# 版本号
version = "v4.6"

# 优先祝福
echos = {"火堆外的夜": "hdwdy"}
# 优先奇物
stranges = {
    "未收集奇物": "new",
    "降维骰子": "jwtz",
    "福灵胶": "flj",
    "巡猎火漆": "xlhq",
    "博士之袍": "bszp",
    "香涎干酪": "xygl",
}
# 优先事件
events = len(os.listdir("imgs/events"))


class SimulatedUniverse(UniverseUtils):
    def __init__(self, find, debug, show_map, speed, update=0):
        super().__init__()
        self.now_map = None
        self.now_map_sim = None
        self.real_loc = [0, 0]
        self.debug_map = np.zeros((8192, 8192), dtype=np.uint8)
        self._stop = False
        self.img_set = []
        self.find = find
        self.debug = debug
        self.speed = speed
        self._show_map = show_map & find
        self.floor = 0
        self.count = 0
        self.count_tm = time.time()
        self.re_align = 0
        self.update_count()
        notif('开始运行',f'初始计数：{self.count}')
        set_debug(debug > 0)
        if update and find:
            update_map()
        self.lst_changed = time.time()
        log.info("加载地图")
        for file in os.listdir("imgs/maps"):
            pth = "imgs/maps/" + file + "/init.jpg"
            if os.path.exists(pth):
                image = cv.imread(pth)
                self.img_set.append((file, self.extract_features(image)))
        log.info("加载地图完成，共 %d 张" % len(self.img_set))
        if os.stat('imgs/mon'+self.ts).st_size!=141882:
            self._stop = 1

    # 初始化地图，刚进图时调用
    def init_map(self):
        self.big_map = np.zeros((8192, 8192), dtype=np.uint8)
        self.big_map_c = 0
        self.lst_tm = 0
        self.tries = 0
        self.his_loc = (30, 30)
        self.offset = (30, 30)
        self.now_loc = (4096, 4096)
        self.map_file = "imgs/maps/my_" + str(random.randint(0, 99999)) + "/"
        if self.find == 0 and not os.path.exists(self.map_file):
            os.mkdir(self.map_file)

    def route(self):
        self.threshold = 0.98
        self.battle = 0
        self.quit = 0
        self.init_map()
        while True:
            if self._stop:
                break
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
            warn_game = False
            cnt = 0
            while Text != "崩坏：星穹铁道":
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
            self.get_screen()
            #self.click_target('imgs/quit.jpg',0.9,True) # 如果需要输出某张图片在游戏窗口中的坐标，可以用这个
            res = self.normal()
            # 未匹配到图片，降低匹配阈值，若一直无法匹配则乱点
            if res == 0:
                if self.threshold > 0.95:
                    self.threshold -= 0.015
                else:
                    self.click((0.5062, 0.1454))
                    self.threshold = 0.98
                time.sleep(1)
            # 匹配到图片 res=1时等待一段时间
            else:
                self.threshold = 0.98
                if res == 1:
                    time.sleep(0.7)
        log.info("停止运行")

    def end_of_uni(self):
        self.update_count(0)
        notif("已完成",f"计数:{self.count}",cnt=str(self.count))
        self.floor = 0

    def normal(self):
        # self.lst_changed：最后一次交互时间，长时间无交互则暂离
        bk_lst_changed = self.lst_changed
        self.lst_changed = time.time()
        # 战斗界面
        if self.check("auto_2", 0.3760, 0.0370):
            # 需要打开自动战斗
            if self.check("c", 0.9453, 0.1296, threshold=0.99):
                self.click((0.0891, 0.9676))
            # self.battle：最后一次处于战斗状态的时间，0表示处于非战斗状态
            self.battle = time.time()
            return 1
        # 祝福界面/回响界面 （放在一起处理了）
        if self.check("choose_bless", 0.9266, 0.9491):
            self.battle = 0
            ok = 0
            for i in range(4):
                if self.speed and self.debug == 2:
                    break
                time.sleep(0.6)
                self.get_screen()
                flag = True
                # 特殊祝福优先级
                for echo in echos.values():
                    img_path = "echos/" + echo
                    if self.check(
                        img_path, 0.5047, 0.4130, mask="mask_echo", threshold=0.9
                    ):
                        self.click((self.tx, self.ty))
                        ok = 1
                        flag = False
                        break
                if self._stop:
                    return 1
                # 未匹配到优先祝福，尝试巡猎回响构音/巡猎祝福
                if flag:
                    self.check(
                        "bless/" + str(self.my_fate), 0.5062, 0.3157, mask="mask"
                    )
                    if self.tm > 0.96:
                        time.sleep(0.2)
                        self.get_screen()
                        tx, ty = self.tx, self.ty
                        if self.opt and self.check(
                            "bless/" + str(self.my_fate) + "/echo1",
                            0.5047,
                            0.4130,
                            mask="mask_echo",
                        ):
                            self.click((self.tx, self.ty))
                        elif self.opt and self.check(
                            "bless/" + str(self.my_fate) + "/echo2",
                            0.5047,
                            0.4130,
                            mask="mask_echo",
                        ):
                            self.click((self.tx, self.ty))
                        else:
                            self.click((tx, ty))
                        ok = 1
                        break
                else:
                    break
            # 未匹配到优先祝福，刷新祝福并再次匹配
            if ok == 0:
                if self.speed == 0 or self.debug != 2:
                    self.click((0.2990, 0.1046))
                    time.sleep(2.5)
                else:
                    time.sleep(2)
                if self._stop:
                    return 1
                self.get_screen()
                flag = True
                # 特殊祝福优先级
                for echo in echos.values():
                    img_path = "echos/" + echo
                    if self.check(
                        img_path, 0.5047, 0.4130, mask="mask_echo", threshold=0.9
                    ):
                        self.click((self.tx, self.ty))
                        ok = 1
                        flag = False
                        break
                if flag:
                    flag_fate = True
                    for fate in [self.my_fate, 4, 5, 3]:
                        if self.check("bless/" + str(fate), 0.5062, 0.3157, mask="mask"):
                            self.click((self.tx, self.ty))
                            flag_fate = False
                            break
                    if flag_fate:
                        self.click((self.tx, self.ty))
            self.click((0.1203, 0.1093))
            time.sleep(1)
            return 1
        # F交互界面
        elif self.check("f", 0.3891,0.4315):
            # is_killed：是否是禁用交互（沉浸奖励、复活装置、下载装置）
            is_killed = 0
            time.sleep(0.55)
            self.get_screen()
            if self.check("f", 0.3891,0.4315):
                # 黑塔
                if self.check("quit", 0.3552,0.4343):
                    # 与黑塔交互后30秒内禁止再次交互（防止死循环）
                    if time.time() - self.quit > 30:
                        self.quit = time.time()
                        self.press("f")
                        self.battle = 0
                else:
                    if self.debug:
                        self.check("tele", 0.3708,0.4306)
                        print(self.tm, end=" ")
                        self.check("exit", 0.3708,0.4306)
                        print(self.tm)
                    # tele：区域-xx  exit：离开模拟宇宙
                    if self.check(
                        "tele", 0.3708,0.4306, threshold=0.965
                    ) or self.check("exit", 0.3708,0.4306, threshold=0.965):
                        # self.get_map()
                        self.init_map()
                        self.floor += 1
                        map_log.info(
                            f"地图{self.now_map}已完成,相似度{self.now_map_sim},进入{self.floor+1}层"
                        )
                        if self.check("exit", 0.3708,0.4306, threshold=0.965):
                            self.end_of_uni()
                    elif self.re_align == 1:
                        align_angle(10, 1)
                        self.multi = config.multi
                        self.re_align += 1
                    is_killed = (
                        self.check("bonus", 0.3578,0.4333)
                        or self.check("rescure", 0.3578,0.4333)
                        or self.check("download", 0.3578,0.4333)
                    )
                    if is_killed == 0:
                        self.press("f")
                    self.battle = 0
                if is_killed == 0:
                    return 1
        # 战斗失败
        elif self.check("fail", 0.5073, 0.0676):
            self.click((0.5073, 0.0676))
            self.battle = 0
            return 1
        # 跑图状态
        if self.check("run", 0.9844, 0.7889, threshold=0.93):
            self.lst_changed = bk_lst_changed
            self.battle = 0
            # 刚进图，初始化一些数据
            if self.big_map_c == 0:
                # 黑屏检测
                while 1:
                    men = np.mean(self.get_screen())
                    if men > 12:
                        break
                    print(men)
                    time.sleep(0.1)
                    if self._stop:
                        return 1
                if self._stop:
                    return 1
                self.big_map_c = 1
                # 寻路模式，匹配最接近的地图
                if self.find:
                    now_time = time.time()
                    self.now_map_sim = 0
                    while True:
                        self.exist_minimap()
                        now_map, now_map_sim = self.match_scr(self.loc_scr)
                        if self.now_map_sim < now_map_sim:
                            self.now_map, self.now_map_sim = now_map, now_map_sim
                        if (
                            self.now_map_sim > 0.7
                            or time.time() - now_time > 2.6
                            or self._stop
                        ):
                            break
                    log.info(f"地图编号：{self.now_map}  相似度：{self.now_map_sim}")
                    if self.now_map_sim<0.42 and self.debug==2:
                        notif('相似度过低','DEBUG')
                        self._stop=1
                    if self._stop:return 1
                    self.press('1')
                    # 地图相似度过低，判定为黑塔空间站或非跑图状态
                    # if self.now_map_sim < 0.3:
                    #    self.init_map()
                    #    return 0
                    self.now_pth = "imgs/maps/" + self.now_map + "/"
                    files = self.find_latest_modified_file(self.now_pth)
                    print("地图文件：", files)
                    self.big_map = cv.imread(files, cv.IMREAD_GRAYSCALE)
                    self.debug_map = deepcopy(self.big_map)
                    xy = files.split("/")[-1].split("_")[1:3]
                    self.now_loc = (4096 - int(xy[0]), 4096 - int(xy[1]))
                    self.target = self.get_target(self.now_pth + "target.jpg")
                    log.info("target %s" % self.target)
                # 录制模式，保存初始小地图
                else:
                    time.sleep(3)
                    self.exist_minimap()
                    cv.imwrite(self.map_file + "init.jpg", self.loc_scr)
            if time.time() - self.lst_tm > 5:
                if self.find == 0:
                    self.press("s", 0.5)
                    if self._stop == 0:
                        pyautogui.keyDown("w")
                    time.sleep(0.5)
                    self.get_screen()
                else:
                    self.press("w", 0.2)
                    self.get_screen()
            self.lst_tm = time.time()
            # 长时间未交互/战斗，暂离或重开
            if (time.time() - self.lst_changed >= 35 - 7 * self.debug) and self.find == 1:
                self.press("esc")
                time.sleep(2)
                self.init_map()
                if self.debug == 2:
                    map_log.error(
                        f"地图{self.now_map}未发现目标,相似度{self.now_map_sim}，尝试退出重进"
                    )
                    notif(f"地图{self.now_map}出现问题","DEBUG")
                    self._stop = 1
                    time.sleep(1)
                    self.floor = 0
                    self.click((0.2708, 0.1324))
                elif random.randint(0, 2) != 3:
                    self.click((0.2927, 0.2602))
                    notif("暂离",f"地图{self.now_map}，当前层数:{self.floor+1}")
                    map_log.error(
                        f"地图{self.now_map}未发现目标,相似度{self.now_map_sim}，尝试暂离"
                    )
                else:
                    if self.debug == 0:
                        notif("中途结算",f"地图{self.now_map}，当前层数:{self.floor+1}")
                        self.floor = 0
                        self.click((0.2708, 0.1324))
                        map_log.error(
                            f"地图{self.now_map}未发现目标,相似度{self.now_map_sim}，尝试退出重进"
                        )
                    else:
                        self.click((0.2927, 0.2602))
                self.re_align += 1
            # 寻路
            else:
                self.get_direc()
            return 2
        # 超过15秒没有刷新战斗状态时间，而且也没有处于非战斗状态：出现月卡界面
        elif self.battle + 15 > time.time():
            return 1
        if self.check("yes", 0.3969, 0.3898):
            self.click((0.3969, 0.3898))
        elif self.check("close", 0.5016, 0.1259, mask="mask_close") or self.check(
            "close_1", 0.5016, 0.1259, mask="mask_close"
        ):
            self.click((0.2062, 0.2054))
        elif self.check("init", 0.9276, 0.6731):
            self.click((0.3448, 0.4926))
            self.init_map()
        elif self.check("begin", 0.3328,0.8148):
            self.click((0.9375, 0.8565 - 0.1 * (self.diffi - 1)))
            self.click((0.1083, 0.1009))
        elif self.check("start", 0.6594, 0.8389):
            dx = 0.9266 - 0.8552
            dy = 0.8194 - 0.6741
            for i in self.order:
                self.click((0.9266 - dx * ((i - 1) % 3), 0.8194 - dy * ((i - 1) // 3)))
                time.sleep(0.3)
            self.click((0.1635, 0.1056))
        elif self.check("fate_2", 0.1797, 0.1009):
            self.click((0.1797, 0.1009))
        elif self.check("fate", 0.9458, 0.9481):
            self.click((0.8547 - self.my_fate * (0.8547 - 0.7375), 0.4963))
        elif self.check("fate_3", 0.9422, 0.9472):
            self.click((0.5047, 0.4917))
            self.click((0.5062, 0.1065))
        # 事件界面
        elif self.check("event", 0.9479, 0.9565):
            # 事件界面：选择
            if self.check("arrow", 0.1828, 0.5000, mask="mask_event"):
                self.click((self.tx, self.ty))
            # 事件界面：退出
            elif self.check("arrow_1", 0.1828, 0.5000, mask="mask_event"):
                self.click((self.tx, self.ty))
            # 事件选择界面
            elif self.check("star", 0.1828, 0.5000, mask="mask_event", threshold=0.965):
                tx, ty = self.tx, self.ty
                for i in range(events):
                    if self.check(
                        "events/" + str(i),
                        0.1828,
                        0.5000,
                        mask="mask_event",
                        threshold=0.965,
                    ):
                        tx, ty = self.tx, self.ty
                        break
                self.click((tx, ty))
                self.click((0.1167, ty - 0.4685 + 0.3546))
                time.sleep(1.5)
            else:
                self.click((0.9479, 0.9565))
        # 选取奇物
        elif self.check("strange", 0.9417, 0.9481):
            self.get_screen()
            flag = True
            # 优先选择stranges中的奇物
            for strange in stranges.values():
                img_path = "stranges/" + strange
                if self.check(img_path, 0.5000, 0.7333, "mask_strange", threshold=0.9):
                    self.click((self.tx, self.ty))
                    flag = False
                    break
            # 如果没有stranges中的奇物，则随机选择一个奇物
            if flag:
                self.click((0.5 + random.randint(0, 2) * 0.1, 0.5))
            self.click((0.1365, 0.1093))
        # 丢弃奇物
        elif self.check("drop", 0.9406, 0.9491):
            self.click((0.4714, 0.5500))
            self.click((0.1339, 0.1028))
        elif self.check("drop_bless", 0.9417, 0.9481, threshold=0.95):
            self.click((0.4714, 0.5500))
            time.sleep(0.5)
            self.click((0.1203, 0.1093))
        else:
            log.info("匹配不到任何图标")
            return 0
        return 1

    def find_latest_modified_file(self, folder_path):
        files = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.split("/")[-1][0] == "m"
        ]
        nx, ny = 4096, 4096
        file = ""
        for i in files:
            try:
                x, y = i.split("_")[-3:-1]
                x, y = int(x), int(y)
                if x < nx or y < ny:
                    nx, ny = x, y
                    file = i
            except:
                pass
        return file

    def update_count(self,read=True):
        file_name = 'logs/notif.txt'
        if read:
            time_cnt = os.path.getmtime(file_name)
            if os.path.exists(file_name):
                with open(file_name,'r') as fh:
                    s=fh.readlines()
                    new_cnt = int(s[0].strip('\n'))
                    try:
                        time_cnt = float(s[3].strip('\n'))
                    except:
                        pass
            else:
                new_cnt = 0
                os.makedirs('logs',exist_ok=1)
                with open(file_name, 'w') as file:
                    file.write("0")
                    file.close()
                #win32api.SetFileAttributes(file_name, win32con.FILE_ATTRIBUTE_HIDDEN)
        else:
            new_cnt = self.count + 1
            time_cnt = self.count_tm
        dt = datetime.datetime.fromtimestamp(time.time())
        current_weekday = dt.weekday()
        monday = dt + datetime.timedelta(days=-current_weekday)
        target_datetime = datetime.datetime(monday.year, monday.month, monday.day, 4, 0, 0)
        monday_ts = target_datetime.timestamp()
        if dt.timestamp()>=monday_ts and time_cnt<monday_ts:
            self.count=not read
        else:
            self.count=new_cnt
        self.count_tm = time.time()

    def del_pt(self, img, A, S, f):
        if (
            (img[A] == [0, 0, 0]).all()
            or (not f(img[A]) and self.get_dis(A, S) > 5)
            or A[0] < 0
            or A[1] < 0
            or A[0] >= img.shape[0]
            or A[1] >= img.shape[1]
            or self.get_dis(A, S) > 10
        ):
            return
        else:
            img[A] = [0, 0, 0]
        for dx, dy in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            self.del_pt(img, (A[0] + dx, A[1] + dy), S, f)

    def get_target(self, pth):
        img = cv.imread(pth)
        res = set()
        f_set = [
            lambda p: p[2] < 85 and p[1] < 85 and p[0] > 180,  # 路径点 蓝
            lambda p: p[2] > 180 and p[1] < 70 and p[0] < 70,  # 怪 红
            lambda p: p[2] < 90 and p[1] > 150 and p[0] < 90,  # 交互点 绿
            lambda p: p[2] > 180 and p[1] > 180 and p[0] < 70,  # 终点 黄
        ]
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for k in range(4):
                    if f_set[k](img[i, j]):
                        p = self.get_center(img, i, j)
                        res.add((p, k))
                        p = (int(p[0]), int(p[1]))
                        self.del_pt(img, p, p, f_set[k])
                        if k == 3:
                            self.last = p
        cv.imwrite("imgs/tmp1.jpg", img)
        if self.speed:
            dis = 1000000
            pt = None
            for i in res:
                if i[1] == 1 and self.get_dis(i[0], self.last) < dis:
                    dis = self.get_dis(i[0], self.last)
                    pt = i
            for i in deepcopy(res):
                if i[1] == 1 and pt != i:
                    res.remove(i)
                    res.add((i[0], 0))
        if self.floor == 11:
            res = set()
            res.add((self.last,3))
        if len(res) == 1:
            pyautogui.click()
        return res

    def get_center(self, img, i, j):
        rx, ry, rt = 0, 0, 0
        for x in range(-7, 7):
            for y in range(-7, 7):
                if (
                    i + x >= 0
                    and j + y >= 0
                    and i + x < img.shape[0]
                    and j + y < img.shape[1]
                ):
                    s = np.sum(img[i + x, j + y])
                    if s > 30 and s < 255 * 3 - 30:
                        rt += 1
                        rx += x
                        ry += y
        return (i + rx / rt, j + ry / rt)

    def stop(self, *_, **__):
        log.info("尝试停止运行")
        self._stop = True

    def on_key_press(self, event):
        global stop_flag
        if event.name == "f8":
            print("F8 已被按下，尝试停止运行")
            self.stop()

    def show_map(self):
        # Create a window to display the image
        cv.namedWindow("Map", cv.WINDOW_AUTOSIZE)

        # Update the image every second
        while not self._stop:
            if self.debug_map.shape[0] == 8192:
                continue
            # Load the updated image
            updated_image = self.debug_map.copy()

            # 灰度图转RGB
            updated_image = cv.cvtColor(updated_image, cv.COLOR_GRAY2RGB)
            updated_image[
                self.real_loc[0] - 2 : self.real_loc[0] + 3,
                self.real_loc[1] - 2 : self.real_loc[1] + 3,
            ] = [49, 49, 140]

            # 将图片放大两倍
            updated_image = cv.resize(
                updated_image, None, fx=2, fy=2, interpolation=cv.INTER_LINEAR
            )

            # Update the displayed image
            cv.imshow("Map", updated_image)

            # Wait for one second
            cv.waitKey(1000)

        # Destroy the window
        cv.destroyAllWindows()

    def start(self):
        self._stop = False
        keyboard.on_press(self.on_key_press)
        if self._show_map:
            t_map = threading.Thread(target=self.show_map)
            t_map.start()
        try:
            self.route()
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            if not self._stop:
                self.stop()


def main():
    log.info(f"find: {find}, debug: {debug}, show_map: {show_map}")
    su = SimulatedUniverse(find, debug, show_map, speed, update)
    try:
        su.start()
    except Exception:
        traceback.print_exc()
    finally:
        su.stop()


if __name__ == "__main__":
    find = 1
    debug = 0
    show_map = 0
    update = 0
    speed = 0
    for i in sys.argv[1:]:
        exec(i.split("-")[-1])
    main()
