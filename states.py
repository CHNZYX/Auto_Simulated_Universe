import threading
import traceback
import keyboard
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32gui
import random
import sys
from copy import deepcopy
from utils.log import log, set_debug
from utils.map_log import map_log
from utils.update_map import update_map
from utils.utils import UniverseUtils,set_forground
import os
 
version = "v4.2"

echos = {"火堆外的夜":"hdwdy"}
stranges = {"未收集奇物":"new","降维骰子":"jwtz","福灵胶":"flj","巡猎火漆":"xlhq","博士之袍":"bszp","香涎干酪":"xygl"}

class SimulatedUniverse(UniverseUtils):
    def __init__(self, find, debug, show_map, update=0):
        super().__init__()
        self.now_map = None
        self.now_map_sim = None
        self.real_loc = [0,0]
        self.debug_map = np.zeros((8192, 8192), dtype=np.uint8)
        self._stop = False
        self.img_set = []
        self.find = find
        self.debug = debug
        self._show_map = show_map
        set_debug(debug)
        if update:
            update_map()
        self.lst_changed = time.time()
        log.info("加载地图")
        for file in os.listdir('imgs/maps'):
            pth = 'imgs/maps/' + file + '/init.jpg'
            if os.path.exists(pth):
                image = cv.imread(pth)
                self.img_set.append((file, self.extract_features(image)))
        log.info("加载地图完成，共 %d 张" % len(self.img_set))

    def init_map(self):
        self.big_map = np.zeros((8192, 8192), dtype=np.uint8)
        self.big_map_c = 0
        self.lst_tm = 0
        self.tries = 0
        self.his_loc = (30, 30)
        self.offset = (30, 30)
        self.now_loc = (4096, 4096)
        self.map_file = 'imgs/maps/' + str(random.randint(0, 99999)) + '/'
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
            cnt=0
            while Text != '崩坏：星穹铁道':
                if self._stop:
                    raise KeyboardInterrupt
                if not warn_game:
                    warn_game = True
                    log.warning("等待游戏窗口")
                time.sleep(0.5)
                cnt+=1
                if cnt==1200:
                    set_forground()
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
            self.get_screen()
            # cv.imwrite('imgs/scr.jpg',self.screen) #0.8547,0.4963 0.7375,0.4898
            # self.click_target('imgs/c.jpg',0.9,True)#0.3375,0.9685 0.9417,0.9472 0.1167,0.5491  0.2938,0.4685  0.1167,0.3546
            res = self.normal()
            if res == 0:
                if self.threshold > 0.95:
                    self.threshold -= 0.015
                else:
                    self.click((0.5062, 0.1454))
                    self.threshold = 0.98
                time.sleep(1)
            else:
                self.threshold = 0.98
                if res == 1:
                    time.sleep(0.7)
        log.info("停止运行")

    def normal(self):
        bk_lst_changed = self.lst_changed
        self.lst_changed = time.time()
        if self.check('auto_2', 0.3760, 0.0370):
            if self.check('c', 0.9453,0.1296,threshold=0.99):
                self.click((0.0891, 0.9676))
            self.battle = time.time()
            return 1
        if self.check('choose_bless', 0.9266, 0.9491):
            self.battle = 0
            ok = 0
            for i in range(4):
                time.sleep(0.6)
                self.get_screen()
                # cv.imwrite('imgs/collect/'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+'.jpg',self.screen)
                # 特殊优先级buf
                flag = True
                for echo in echos.values():
                    img_path = "echos/" + echo
                    if self.check(img_path, 0.5047, 0.4130, mask='mask_echo',threshold=0.9):
                        self.click((self.tx, self.ty))
                        ok = 1
                        flag = False
                        break
                if self._stop:return 1
                if flag:
                    # 是否有巡猎buf
                    self.check('bless/'+str(self.my_fate), 0.5062, 0.3157, mask='mask')
                    if self.tm > 0.96:
                        time.sleep(0.2)
                        self.get_screen()
                        tx,ty=self.tx, self.ty
                        if self.opt and self.check('bless/'+str(self.my_fate)+'/echo1',0.5047,0.4130,mask='mask_echo'):
                            self.click((self.tx,self.ty))
                        elif self.opt and self.check('bless/'+str(self.my_fate)+'/echo2',0.5047,0.4130,mask='mask_echo'):
                            self.click((self.tx,self.ty))
                        else:
                            self.click((tx, ty))
                        ok = 1
                        break
                else:
                    break
            if ok == 0:
                self.click((0.2990, 0.1046))
                time.sleep(2.5)
                if self._stop:return 1
                self.get_screen()
                # cv.imwrite('imgs/collect/'+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+'.jpg',self.screen)
                # 特殊优先级buf
                flag = True
                for echo in echos.values():
                    img_path = "echos/" + echo
                    if self.check(img_path, 0.5047, 0.4130, mask='mask_echo',threshold=0.9):
                        self.click((self.tx, self.ty))
                        ok = 1
                        flag = False
                        break
                if flag:
                    self.check('bless/'+str(self.my_fate), 0.5062, 0.3157, mask='mask')
                    self.click((self.tx, self.ty))
            self.click((0.1203, 0.1093))
            time.sleep(1)
            return 1
        elif self.check('f', 0.3901, 0.5093):
            is_killed=0
            time.sleep(0.45)
            self.get_screen()
            if self.check('f', 0.3901, 0.5093):
                if self.check('quit', 0.3563, 0.5120):
                    if time.time() - self.quit > 30:
                        self.quit = time.time()
                        self.press('f')
                        self.battle = 0
                else:
                    if self.debug:
                        self.check('tele', 0.3719, 0.5083)
                        print(self.tm,end=' ')
                        self.check('exit', 0.3719, 0.5083)
                        print(self.tm)
                    if self.check('tele', 0.3719, 0.5083, threshold=0.965) or self.check('exit', 0.3719, 0.5083, threshold=0.965):
                        # self.get_map()
                        map_log.info(f'地图{self.now_map}已完成,相似度{self.now_map_sim}')
                        self.init_map()
                    is_killed=self.check('bonus',0.3578,0.5083) or self.check('rescure',0.3578,0.5083) or self.check('download',0.3578,0.5083)
                    if is_killed==0:
                        self.press('f')
                    self.battle = 0
                if is_killed==0:
                    return 1
        elif self.check('fail', 0.5073, 0.0676):
            self.click((0.5073, 0.0676))
            self.battle = 0
            return 1
        if self.check('run', 0.9844, 0.7889, threshold=0.93):
            self.lst_changed = bk_lst_changed
            self.battle = 0
            if self.big_map_c == 0:
                while 1:
                    men = np.mean(self.get_screen())
                    if men > 12: break
                    print(men)
                    time.sleep(0.1)
                    if self._stop:return 1
                time.sleep(2.2)
                if self._stop:return 1
                self.get_screen()
                self.exist_minimap()
                self.big_map_c = 1
                if self.find:
                    self.now_map,self.now_map_sim = self.match_scr(self.loc_scr)
                    if self.now_map_sim<0.3:
                        self.init_map()
                        return 0
                    self.now_pth = 'imgs/maps/' + self.now_map + '/'
                    files = self.find_latest_modified_file(self.now_pth)
                    print('地图文件：',files)
                    self.big_map = cv.imread(files, cv.IMREAD_GRAYSCALE)
                    self.debug_map = deepcopy(self.big_map)
                    xy = files.split('/')[-1].split('_')[1:3]
                    self.now_loc = (4096 - int(xy[0]), 4096 - int(xy[1]))
                    self.target = self.get_target(self.now_pth + 'target.jpg')
                    log.info("target %s" % self.target)
                    self.monster = (-1, -1)
                    # self.big_map[self.now_loc[0],self.now_loc[1]]=255
                    cv.imwrite('imgs/tmp4.jpg', self.big_map)
                else:
                    cv.imwrite(self.map_file + 'init.jpg', self.loc_scr)
            if time.time() - self.lst_tm > 5:
                if self.find == 0:
                    self.press('s', 0.5)
                    if self._stop==0:
                        pyautogui.keyDown('w')
                    time.sleep(0.5)
                    self.get_screen()
                else:
                    self.press('w',0.2)
                    self.get_screen()
            self.lst_tm = time.time()
            if time.time() - self.lst_changed >= 45 and self.find == 1:
                map_log.error(f'地图{self.now_map}未发现目标,相似度{self.now_map_sim}，尝试退出重进')
                self.press('esc')
                if self.debug == 1:
                    time.sleep(1000000)
                time.sleep(2)
                if random.randint(0,2)!=2:
                    self.click((0.2927, 0.2602))
                else:
                    self.click((0.2708, 0.1324))
            else:
                self.get_direc()
            return 2
        elif self.battle+15>time.time():
            return 1
        if self.check('yes', 0.3969, 0.3898):
            self.click((0.3969, 0.3898))
        elif self.check('close', 0.5016, 0.1259, mask='mask_close') or self.check('close_1', 0.5016, 0.1259,
                                                                                  mask='mask_close'):
            self.click((0.2062, 0.2054))
        elif self.check('init', 0.9276, 0.6731):
            self.click((0.3448, 0.4926))
            self.init_map()
        elif self.check('begin', 0.3339, 0.7741):
            self.click((0.9375,0.8565-0.1*(self.diffi-1)))
            self.click((0.1083, 0.1009))
        elif self.check('start', 0.6594, 0.8389):
            dx = 0.9266 - 0.8552
            dy = 0.8194 - 0.6741
            for i in self.order:
                self.click((0.9266 - dx * ((i - 1) % 3), 0.8194 - dy * ((i - 1) // 3)))
                time.sleep(0.3)
            self.click((0.1635, 0.1056))
        elif self.check('fate_2', 0.1797, 0.1009):
            self.click((0.1797, 0.1009))
        elif self.check('fate', 0.9458, 0.9481):#0.8547,0.4963 0.7375,0.4898
            self.click((0.8547-self.my_fate*(0.8547-0.7375),0.4963))
        elif self.check('fate_3', 0.9422,0.9472):
            self.click((0.5047, 0.4917))
            self.click((0.5062, 0.1065))
        elif self.check('arrow', 0.1828, 0.5000, mask='mask_event'):
            self.click((self.tx, self.ty))
        elif self.check('arrow_1', 0.1828, 0.5000, mask='mask_event'):
            self.click((self.tx, self.ty))
        elif self.check('star', 0.1828, 0.5000, mask='mask_event', threshold=0.965):
            self.click((self.tx, self.ty))
            self.click((0.1167, self.ty - 0.4685 + 0.3546))
            time.sleep(1.5)
        elif self.check('event', 0.9479, 0.9565):
            self.click((0.9479, 0.9565))
        # 选取奇物
        elif self.check('strange', 0.9417, 0.9481):
            self.get_screen()
            # cv.imwrite('imgs/collect/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.jpg', self.screen)
            flag = True
            # 优先选择stranges中的奇物
            for strange in stranges.values():
                img_path = "stranges/" + strange
                if self.check(img_path, 0.5000, 0.7333,'mask_strange',threshold=0.9):
                    self.click((self.tx, self.ty))
                    flag = False
                    break
            # 如果没有stranges中的奇物，则随机选择一个奇物
            if flag:
                self.click((0.5 + random.randint(0, 2) * 0.1, 0.5))
            self.click((0.1365, 0.1093))
        elif self.check('drop',0.9406,0.9491):
            self.click((0.4714,0.5500))
            self.click((0.1339,0.1028))
        # elif self.check('run',0.9844,0.7889,threshold=0.95):
        #    return 2
        else:
            log.info("匹配不到任何图标")
            return 0
        return 1

    def find_latest_modified_file(self, folder_path):
        files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.split('/')[-1][0] == 'm']
        nx,ny=4096,4096
        file=''
        for i in files:
            try:
                x,y=i.split('_')[-3:-1]
                x,y=int(x),int(y)
                if x<nx or y<ny:
                    nx,ny=x,y
                    file=i
            except:
                pass
        return file

    def get_target(self, pth):
        img = cv.imread(pth)
        res = set()
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                # 路径点 蓝
                if img[i, j, 2] < 85 and img[i, j, 1] < 85 and img[i, j, 0] > 180:
                    res.add((self.get_center(img, i, j), 0))
                    img[max(i - 7, 0):i + 7, max(j - 7, 0):j + 7] = [0, 0, 0]
                # 怪 红
                if img[i, j, 2] > 180 and img[i, j, 1] < 70 and img[i, j, 0] < 70:
                    res.add((self.get_center(img, i, j), 1))
                    img[max(i - 7, 0):i + 7, max(j - 7, 0):j + 7] = [0, 0, 0]
                # 交互点 绿
                if img[i, j, 2] < 90 and img[i, j, 1] > 150 and img[i, j, 0] < 90:
                    res.add((self.get_center(img, i, j), 2))
                    img[max(i - 7, 0):i + 7, max(j - 7, 0):j + 7] = [0, 0, 0]
                # 终点 黄
                if img[i, j, 2] > 180 and img[i, j, 1] > 180 and img[i, j, 0] < 70:
                    res.add((self.get_center(img, i, j), 3))
                    img[max(i - 7, 0):i + 7, max(j - 7, 0):j + 7] = [0, 0, 0]
                    self.last=(i,j)
        return res

    def get_center(self, img, i, j):
        rx, ry, rt = 0, 0, 0
        for x in range(-7, 7):
            for y in range(-7, 7):
                if i + x >= 0 and j + y >= 0 and i + x < img.shape[0] and j + y < img.shape[1]:
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
        cv.namedWindow("Map",cv.WINDOW_AUTOSIZE)

        # Update the image every second
        while not self._stop:
            if self.debug_map.shape[0] == 8192:
                continue
            # Load the updated image
            updated_image = self.debug_map.copy()

            # 灰度图转RGB
            updated_image = cv.cvtColor(updated_image, cv.COLOR_GRAY2RGB)
            updated_image[self.real_loc[0] - 2:self.real_loc[0] + 3, self.real_loc[1] - 2:self.real_loc[1] + 3] = [49, 49, 140]

            # 将图片放大两倍
            updated_image = cv.resize(updated_image, None, fx=2, fy=2, interpolation=cv.INTER_LINEAR)

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
    su = SimulatedUniverse(find, debug, show_map, update)
    try:
        su.start()
    except Exception:
        traceback.print_exc()
    finally:
        su.stop()


if __name__ == '__main__':
    find = 1
    debug = 0
    show_map = 0
    update = 0
    for i in sys.argv[1:]:
        exec(i.split('-')[-1])
    main()
