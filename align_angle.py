import time

import numpy as np
import pywintypes
import win32api
import win32con
import win32gui
import pyuac
from utils.log import log


def get_angle(su, safe):
    import cv2
    su.press("w")
    time.sleep(0.5)
    su.get_screen()
    shape = (int(su.scx * 190), int(su.scx * 190))
    local_screen = su.get_local(0.9333, 0.8657, shape)  # 裁剪后得到的小地图
    return su.get_now_direc(local_screen)


# 不同电脑鼠标移动速度、放缩比、分辨率等不同，因此需要校准
# 基本逻辑：每次转60度，然后计算实际转了几度，计算出误差比
def main(cnt=10, safe=0, ang=[1,1,3], su=None):
    if su is None or 'Diver' in su.__class__.__name__:
        from utils.diver.config import config
    else:
        from utils.simul.config import config
    if float(config.angle)>2 and len(ang)<3 and su is not None:
        su.multi = config.multi
        return
    log.info("开始校准")
    if su is None:
        from utils.simul.utils import UniverseUtils
        su = UniverseUtils()
    su.multi = 1
    init_ang = get_angle(su, safe)
    lst_ang = init_ang
    for i in ang:
        if lst_ang != init_ang and i==1:
            continue
        ang_list = []
        for j in range(i):
            su.mouse_move(60, fine=3 // i)
            time.sleep(0.2)
            now_ang = get_angle(su, safe)
            sub = lst_ang - now_ang
            while sub < 0:
                sub += 360
            ang_list.append(sub)
            lst_ang = now_ang
        ang_list = np.array(ang_list)
        # 十/3次转身的角度
        print(ang_list)
        ax = 0
        ay = 0
        for j in ang_list:
            if abs(j - np.median(ang_list)) <= 3:
                ax += 60
                ay += j
        su.multi *= ax / ay
    su.multi += 1e-9
    try:
        if not abs(su.multi) <= 2:
            su.multi = 1
    except:
        su.multi = 1
    config.angle = str(su.multi+len(ang)-1)
    config.save()
    if su is None:
        from utils.simul.config import config
        config.angle = str(su.multi+len(ang)-1)
        config.save()
    log.info("校准完成")
    return 1


if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()
