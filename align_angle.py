import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api
import win32gui
import win32con
import random
import sys
from utils.utils import Universe_Utils
import os

def get_angle():
    su.press('w',0.2)
    su.get_screen()
    blue=np.array([234,191,4])
    shape=(int(su.scx*190),int(su.scx*190))
    local_screen=su.get_local(0.9333,0.8657,shape)
    local_screen[np.sum(np.abs(local_screen-blue),axis=-1)<=150]=blue
    return su.get_now_direc(local_screen)

su = Universe_Utils()
su.multi=1
init_ang=get_angle()
lst_ang=init_ang
win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 3000)
ang_list=[]
for i in range(10):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 300)
    su.mouse_move(60)
    now_ang=get_angle()
    sub=lst_ang-now_ang
    ang_list.append(sub)
    lst_ang=now_ang
    while sub<0:
        sub+=360
ang_list=np.array(ang_list)
ax=0
ay=0
for i in ang_list:
    if abs(i-np.median(ang_list))<=5:
        ax+=60
        ay+=i
with open('info.txt','r') as fh:
    s=fh.readlines()[:2]
    while len(s)<2:
        s.append('')
    s[1]=str(ax/ay)
with open('info.txt','w') as fh:
    fh.write(s[0])
    fh.write(s[1])
try:
    win32gui.SetForegroundWindow(su.my_nd)
except:
    pass
print('success')