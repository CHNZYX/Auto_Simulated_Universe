from pickle import FALSE
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api
import win32gui
import win32con
import json
import random
import sys
from utils.utils import Universe_Utils
import os


class Simulated_Universe(Universe_Utils):
    def __init__(self,find):
        super().__init__()
        self.img_set=[]
        self.find=find
        for file in os.listdir('imgs/maps'):
            pth='imgs/maps/'+file+'/init.jpg'
            if os.path.exists(pth):
                image = cv.imread(pth)
                self.img_set.append((file,self.extract_features(image)))

    def init_map(self):
        self.big_map=np.zeros((8192,8192),dtype=np.uint8)
        self.big_map_c=0
        self.lst_tm=0
        self.his_loc=(30,30)
        self.offset=(30,30)
        self.now_loc=(4096,4096)
        self.map_file='imgs/maps/'+str(random.randint(0,99999))+'/'
        if self.find==0 and not os.path.exists(self.map_file):
            os.mkdir(self.map_file)

    def route(self):
        self.threshold=0.98
        self.battle=0
        self.quit=0
        self.init_map()
        while True:
            hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
            Text = win32gui.GetWindowText(hwnd)
            while Text != '崩坏：星穹铁道':
                time.sleep(0.5)
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
            self.get_screen()
            #cv.imwrite('imgs/scr.jpg',self.screen)
            #self.click_target('imgs/fail.jpg',0.9,False)#0.1167,0.5491  0.2938,0.4685  0.1167,0.3546
            res=self.normal()
            if res==0:
                if self.threshold>0.95:
                    self.threshold-=0.015
                else:
                    self.click((0.5062,0.1454))
                    self.threshold=0.98
                time.sleep(1)
            else:
                self.threshold=0.98
                if res==1:
                    time.sleep(0.7)

    def normal(self):
        self.check('auto_1',0.0891,0.9676)
        if self.tm<0.95 and self.check('auto_2',0.3760,0.0370) and self.battle==0:
            self.click((0.0891,0.9676))
            self.battle=1
            return 1
        if self.check('choose_bless',0.9266,0.9491):
            self.battle=0
            ok=0
            for i in range(4):
                time.sleep(0.6)
                self.get_screen()
                self.check('bless',0.5062,0.3157,mask='mask')
                if self.tm>0.96:
                    self.click((self.tx,self.ty))
                    ok=1
                    break
            if ok==0:
                self.click((0.2990,0.1046))
                time.sleep(2.5)
                self.get_screen()
                self.check('bless',0.5062,0.3157,mask='mask')
                self.click((self.tx,self.ty))
            self.click((0.1203,0.1093))
            time.sleep(1)
            return 1
        elif self.check('f',0.3901,0.5093):
            if self.check('quit',0.3563,0.5120):
                if time.time()-self.quit>30:
                    self.quit=time.time()
                    self.press('f')
                    self.battle=0
            else:
                if self.check('tele',0.3719,0.5083) or self.check('exit',0.3719,0.5083):
                    #self.get_map()
                    self.init_map()
                self.press('f')
                self.battle=0
            return 1
        elif self.check('fail',0.5073,0.0676):
            self.click((0.5073,0.0676))
            self.battle=0
        elif self.check('run',0.9844,0.7889,threshold=0.93):
            self.battle=0
            if self.big_map_c==0:
                self.big_map_c=1
                time.sleep(2)
                self.get_screen()
                self.exist_minimap()
                if self.find:
                    self.now_map=self.match_scr(self.loc_scr)
                    self.now_pth='imgs/maps/'+self.now_map+'/'
                    files=self.find_latest_modified_file(self.now_pth)
                    self.big_map=cv.imread(files,cv.IMREAD_GRAYSCALE)
                    xy=files.split('/')[-1].split('_')[1:3]
                    self.now_loc=(4096-int(xy[0]),4096-int(xy[1]))
                    self.target=self.get_target(self.now_pth+'target.jpg')
                    print(self.target)
                    self.monster=(-1,-1)
                    #self.big_map[self.now_loc[0],self.now_loc[1]]=255
                    cv.imwrite('imgs/tmp4.jpg',self.big_map)
                else:
                    cv.imwrite(self.map_file+'init.jpg',self.loc_scr)
            if time.time()-self.lst_tm>5:
                if self.find==0:
                    self.press('s',0.5)
                    pyautogui.keyDown('w')
                    time.sleep(0.5)
                    self.get_screen()
                else:
                    pyautogui.keyDown('w')
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 3000)
                    time.sleep(0.2)
                    pyautogui.keyUp('w')
                    self.get_screen()
            self.lst_tm=time.time()
            self.get_direc()
            return 2
        elif self.battle:
            return 1
        if self.check('yes',0.3969,0.3898):
            self.click((0.3969,0.3898))
        elif self.check('close',0.5016,0.1259,mask='mask_close') or self.check('close_1',0.5016,0.1259,mask='mask_close'):
            self.click((0.2062,0.2054))
        elif self.check('init',0.9724,0.6630):
            self.click((0.3448,0.4926))
        elif self.check('begin',0.3339,0.7741):
            self.click((0.1083,0.1009))
        elif self.check('start',0.6594,0.8389):
            dx=0.9266-0.8552
            dy=0.8194-0.6741
            for i in self.order:
                self.click((0.9266-dx*((i-1)%3),0.8194-dy*((i-1)//3)))
                time.sleep(0.3)
            self.click((0.1635,0.1056))
        elif self.check('fate_1',0.3885,0.4972):
            self.click((0.3885,0.4972))
        elif self.check('fate_2',0.1797,0.1009):
            self.click((0.1797,0.1009))
            time.sleep(7)
            self.click((0.5047,0.4917))
            self.click((0.5062,0.1065))
        elif self.check('arrow',0.1828,0.5000,mask='mask_event'):
            self.click((self.tx,self.ty))
        elif self.check('arrow_1',0.1828,0.5000,mask='mask_event'):
            self.click((self.tx,self.ty))
        elif self.check('star',0.1828,0.5000,mask='mask_event'):
            self.click((self.tx,self.ty))
            self.click((0.1167,self.ty-0.4685+0.3546))
            time.sleep(1.5)
        elif self.check('event',0.9479,0.9565):
            self.click((0.9479,0.9565))
        elif self.check('strange',0.9417,0.9481):
            self.click((0.5+random.randint(0,2)*0.1,0.5))
            self.click((0.1365,0.1093))
        #elif self.check('run',0.9844,0.7889,threshold=0.95):
        #    return 2
        else:
            print('no')
            return 0
        return 1
    
    def find_latest_modified_file(self,folder_path):
        files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.split('/')[-1][0]=='m']
        sorted_files = sorted(files, key=lambda file: os.path.getmtime(file), reverse=True)
        return sorted_files[0]
    
    def get_target(self,pth):
        img=cv.imread(pth)
        res=set()
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                #路径点 蓝
                if img[i,j,2]<85 and img[i,j,1]<85 and img[i,j,0]>180:
                    res.add((self.get_center(img,i,j),0))
                    img[max(i-7,0):i+7,max(j-7,0):j+7]=[0,0,0]
                #怪 红
                if img[i,j,2]>180 and img[i,j,1]<70 and img[i,j,0]<70:
                    res.add((self.get_center(img,i,j),1))
                    img[max(i-7,0):i+7,max(j-7,0):j+7]=[0,0,0]
                #交互点 绿
                if img[i,j,2]<90 and img[i,j,1]>150 and img[i,j,0]<90:
                    res.add((self.get_center(img,i,j),2))
                    img[max(i-7,0):i+7,max(j-7,0):j+7]=[0,0,0]
                #终点 黄
                if img[i,j,2]>180 and img[i,j,1]>180 and img[i,j,0]<70:
                    res.add((self.get_center(img,i,j),3))
                    img[max(i-7,0):i+7,max(j-7,0):j+7]=[0,0,0]
        return res
    
    def get_center(self,img,i,j):
        rx,ry,rt=0,0,0
        for x in range(-7,7):
            for y in range(-7,7):
                if i+x>=0 and j+y>=0 and i+x<img.shape[0] and j+y<img.shape[1]:
                    s=np.sum(img[i+x,j+y])
                    if s>30 and s<255*3-30:
                        rt+=1
                        rx+=x
                        ry+=y
        return (i+rx/rt,j+ry/rt)
            
find=1
if len(sys.argv)>1:
    find=int(sys.argv[1].split('=')[1])
su = Simulated_Universe(find)
su.route()