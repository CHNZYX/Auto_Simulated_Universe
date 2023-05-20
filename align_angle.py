import time

import numpy as np
import pywintypes
import win32api
import win32con
import win32gui

from utils.config import config
from utils.utils import Universe_Utils


def get_angle(su):
    su.press('w', 0.2)
    su.get_screen()
    blue = np.array([234, 191, 4])
    shape = (int(su.scx * 190), int(su.scx * 190))
    local_screen = su.get_local(0.9333, 0.8657, shape)
    local_screen[np.sum(np.abs(local_screen - blue), axis=-1) <= 150] = blue
    return su.get_now_direc(local_screen)


def main():
    print("开始校准")
    su = Universe_Utils()
    su.multi = 1
    init_ang = get_angle(su)
    lst_ang = init_ang
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 3000)
    ang_list = []
    for i in range(10):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 300)
        su.mouse_move(60)
        now_ang = get_angle(su)
        sub = lst_ang - now_ang
        while sub < 0:
            sub += 360
        ang_list.append(sub)
        lst_ang = now_ang
    ang_list = np.array(ang_list)
    ax = 0
    ay = 0
    for i in ang_list:
        if abs(i - np.median(ang_list)) <= 5:
            ax += 60
            ay += i
    config.angle = str(ax / ay)
    config.save()
    try:
        win32gui.SetForegroundWindow(su.my_nd)
    except pywintypes.error:
        pass
    print('校准完成')


if __name__ == '__main__':
    main()
