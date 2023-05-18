from pickle import FALSE
import pyautogui
import cv2 as cv
import numpy as np
import time
import win32api
import win32gui
import win32print
import win32con
import json
from copy import deepcopy
import math

class Universe_Utils:
    def __init__(self):
        self.bx,self.by=1920,1080
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
                Text = win32gui.GetWindowText(hwnd)
                self.x0,self.y0,self.x1,self.y1 = win32gui.GetClientRect(hwnd)
                self.xx=self.x1-self.x0
                self.yy=self.y1-self.y0
                self.x0,self.y0,self.x1,self.y1 = win32gui.GetWindowRect(hwnd)
                self.x0=max(0,self.x1-self.xx)
                self.y0=max(0,self.y1-self.yy)
                self.scx=self.xx/self.bx
                self.scy=self.yy/self.by
                dc = win32gui.GetWindowDC(hwnd)
                dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
                dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
                win32gui.ReleaseDC(hwnd, dc)
                scale_x = dpi_x / 96
                scale_y = dpi_y / 96
                # 计算出真实分辨率
                self.real_width = int(self.xx * scale_x)
                #x01y01:窗口左上右下坐标
                #xx yy:窗口大小
                #scx scy:当前窗口和基准窗口（1920*1080）缩放大小比例
                if Text == '崩坏：星穹铁道':
                    break
                else:
                    time.sleep(0.3)
            except:
                time.sleep(0.3)
        with open('info.txt','r') as fh:
            s=fh.readlines()
            self.order=s[0].strip('\n').split(' ')
            self.order=[int(x) for x in self.order]
                
    def press(self,c,t=0):
        pyautogui.keyDown(c)
        time.sleep(t)
        pyautogui.keyUp(c)

    def get_point(self, x, y):
        #得到一个点的浮点表示
        x=self.x1-x
        y=self.y1-y
        print("{:.4f},{:.4f}".format(x/self.xx,y/self.yy))

    #没啥用
    def scan_screenshot(self, prepared):
        temp = pyautogui.screenshot()
        screenshot = np.array(temp)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
        result = cv.matchTemplate(screenshot, prepared, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        return {'screenshot': screenshot, 'min_val': min_val, 'max_val': max_val, 'min_loc': min_loc, 'max_loc': max_loc}

    #没啥用
    def calculated(self, result, shape):
        mat_top, mat_left = result['max_loc']
        prepared_height, prepared_width, prepared_channels = shape
        x = int((mat_top + mat_top + prepared_width) / 2)
        y = int((mat_left + mat_left + prepared_height) / 2)
        return x, y

    def click(self, points):
        #点击一个点
        x, y = points
        if type(x)!=type(0):
            x, y = self.x1-int(x*self.xx),self.y1-int(y*self.yy)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        time.sleep(0.3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.5)

    def click_target(self, target_path, threshold, flag=True):
        #点击与模板匹配的点，可能有用
        target = cv.imread(target_path)
        while True:
            result = self.scan_screenshot(target)
            if result['max_val'] > threshold:
                points = self.calculated(result, target.shape)
                self.get_point(*points)
                print(target.shape)
                self.click(points)
                return
            if flag == False:
                return
            
    def get_local(self,x,y,size):
        #在截图中裁剪需要匹配的部分
        sx,sy=size[0]+60,size[1]+60
        bx,by=self.xx-int(x*self.xx),self.yy-int(y*self.yy)
        return self.screen[max(0,by-sx//2):min(self.yy,by+sx//2),max(0,bx-sy//2):min(self.xx,bx+sy//2),:]

    def format_path(self, path):
        return f"./imgs/{path}.jpg"
            
    def check(self, path, x, y, mask=None, threshold=None):
        #path：匹配模板的路径，mask不用管
        if threshold is None:
            threshold = self.threshold
        path = self.format_path(path)
        target = cv.imread(path)
        #print(path,target.shape,self.scx,self.scy)
        target = cv.resize(target, dsize=(int(self.scx*target.shape[1]),int(self.scx*target.shape[0])))
        #print(target.shape)
        if mask is None:
            shape=target.shape
        else:
            mask_img = cv.imread(self.format_path(mask))
            shape=(int(self.scx*mask_img.shape[0]),int(self.scx*mask_img.shape[1]))
        local_screen=self.get_local(x,y,shape)
        if 1:#path=='./imgs/close_1.jpg':
            cv.imwrite('imgs/tmp.jpg',local_screen)
            cv.imwrite('imgs/tmp1.jpg',target)
        result = cv.matchTemplate(local_screen, target, cv.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        #print(max_loc,target.shape,max_val,local_screen.shape)
        self.tx=x-(max_loc[0]-0.5*local_screen.shape[1])/self.xx
        self.ty=y-(max_loc[1]-0.5*local_screen.shape[0])/self.yy
        self.tm=max_val
        if max_val>threshold:
            print(path,max_val,threshold)
        return max_val>threshold
    # 计算旋转变换矩阵
    def handle_rotate_val(self,x,y,rotate):
        cos_val = np.cos(np.deg2rad(rotate))
        sin_val = np.sin(np.deg2rad(rotate))
        return np.float32([
            [cos_val, sin_val, x * (1 - cos_val) - y * sin_val],
            [-sin_val, cos_val, x * sin_val + y * (1 - cos_val)]
            ])

    # 图像旋转（以任意点为中心旋转）
    def image_rotate(self,src, rotate=0):
        h,w,c = src.shape
        M = self.handle_rotate_val(w//2,h//2,rotate)
        img = cv.warpAffine(src, M, (w,h))
        return img

    def exist_minimap(self):
        #TODO 截图中存在小地图，开始寻路
        #TODO 使用local_screen
        shape=(int(self.scx*190),int(self.scx*190))
        local_screen=self.get_local(0.9333,0.8657,shape)
        arrow=self.format_path('loc_arrow')
        arrow=cv.imread(arrow)
        blue=np.array([234,191,4])
        local_screen[np.sum(np.abs(local_screen-blue),axis=-1)<=50]=blue
        #tot_blue=np.sum(local_screen[int(shape[0]*0.2):int(shape[0]*0.7),int(shape[1]*0.2):int(shape[1]*0.7)]==blue)
        self.loc_scr=local_screen
        return 1
    

    def get_screen(self):
        self.screen = pyautogui.screenshot()
        self.screen = np.array(self.screen)
        self.screen = self.screen[self.y0:self.y1,self.x0:self.x1,:]
        self.screen = cv.cvtColor(self.screen, cv.COLOR_BGR2RGB)

    def get_bw_map(self,gs=1,sbl=0):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 300)
        yellow=np.array([145,192,220])
        black=np.array([0,0,0])
        white=np.array([210,210,210])
        sblue=np.array([222,198,121])
        shape=(int(self.scx*190),int(self.scx*190))
        if gs:
            self.get_screen()
        local_screen=self.get_local(0.9333,0.8657,shape)
        bw_map=np.zeros(local_screen.shape[:2],dtype=np.uint8)
        bw_map[np.sum((local_screen-yellow)**2,axis=-1)<=800+self.find*1600]=200
        bw_map[np.sum((local_screen-white)**2,axis=-1)<=800+self.find*1600]=255
        if sbl:
            bw_map[np.sum((local_screen-sblue)**2,axis=-1)<=400]=150
        bw_map=bw_map[int(shape[0]*0.5)-68:int(shape[0]*0.5)+108,int(shape[1]*0.5)-48:int(shape[1]*0.5)+128]
        for i in range(bw_map.shape[0]):
            for j in range(bw_map.shape[1]):
                if ((i-88)**2+(j-88)**2)>85**2:
                    bw_map[i,j]=0
        if sbl:
            ii,jj=30,30
            cv.imwrite('imgs/sbl.jpg',bw_map)
            for i in range(-20,21):
                for j in range(-20,21):
                    if bw_map[88+i,88+j]==150 and i**2+j**2<ii**2+jj**2:
                        ii,jj=i,j
            bw_map[bw_map==150]=0
            print(ii,jj)
            if ii**2+jj**2<self.his_loc[0]**2+self.his_loc[1]**2:
                self.his_loc=(ii,jj)
        bw_map[bw_map==200]=255
        if self.find==0:
            cv.imwrite(self.map_file+'bwmap.jpg',bw_map)
        return bw_map
    
    def get_direc(self):
        gray=np.array([55,55,55])
        blue=np.array([234,191,4])
        white=np.array([210,210,210])
        blue=np.array([234,191,4])
        sred=np.array([49,49,140])
        yellow=np.array([145,192,220])
        black=np.array([0,0,0])
        arrow=self.format_path('loc_arrow')
        arrow=cv.imread(arrow)
        shape=(int(self.scx*190),int(self.scx*190))
        local_screen=self.get_local(0.9333,0.8657,shape)
        local_screen[np.sum(np.abs(local_screen-blue),axis=-1)<=150]=blue
        self.loc_scr=local_screen
        loc_tp=deepcopy(self.loc_scr)
        loc_tp[np.sum(np.abs(loc_tp-blue),axis=-1)>0]=[0,0,0]
        mx_acc=0
        mx_loc=(0,0)
        self.ang=0
        for i in range(360):
            rt=self.image_rotate(arrow,i)
            result = cv.matchTemplate(loc_tp, rt, cv.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            if max_val>mx_acc:
                mx_acc=max_val
                mx_loc=(max_loc[0]+12,max_loc[1]+12)
                self.ang=i
        self.ang=360-self.ang-90
        bw_map=self.get_bw_map(gs=0)
        cv.imwrite('imgs/tmp2.jpg',bw_map)
        self.get_loc(bw_map,35-self.find*10)
        if self.find==0:
            self.write_map(bw_map)
            self.get_map()
        else:
            mn_dis=100000
            loc=0
            type=-1
            bl=0
            if self.his_loc[0]==30:
                bl=1
            for i,j in self.target:
                if self.get_dis(i,self.real_loc)<mn_dis:
                    mn_dis=self.get_dis(i,self.real_loc)
                    loc=i
                    type=j
            ang=math.atan2(loc[0]-self.real_loc[0],loc[1]-self.real_loc[1])/math.pi*180
            sub=ang-self.ang
            while sub<-180:
                sub+=360
            while sub>180:
                sub-=360
            if bl==0:
                self.mouse_move(sub)
                self.ang=ang
            if type==1:
                ps=8
            elif type==0:
                ps=6
            else:
                ps=6
            print(self.real_loc,loc)
            pyautogui.keyDown('w')
            time.sleep(0.5)
            ltm=time.time()
            bw_map=self.get_bw_map(sbl=bl)
            self.get_loc(bw_map,rg=18)
            sloc=self.real_loc
            self.big_map[self.real_loc[0]-1:self.real_loc[0]+2,self.real_loc[1]-1:self.real_loc[1]+2]=49
            ds=self.get_dis(self.real_loc,loc)
            dls=[100000,100000,100000,ds]
            sds=ds
            td=0
            for i in range(1000):
                ctm=time.time()
                bw_map=self.get_bw_map(sbl=(i<=4 and bl))
                self.get_loc(bw_map,fbw=1)
                if i<=4 and bl:
                    fx=0.2/(ctm-ltm)*(self.real_loc[0]-sloc[0])
                    fy=0.2/(ctm-ltm)*(self.real_loc[1]-sloc[1])
                    print('off',fx,fy)
                    self.offset=(int(fx),int(fy))
                else:
                    self.real_loc=(self.real_loc[0]+self.his_loc[0]+self.offset[0],self.real_loc[1]+self.his_loc[1]+self.offset[1])
                ang=math.atan2(loc[0]-self.real_loc[0],loc[1]-self.real_loc[1])/math.pi*180
                sub=ang-self.ang
                while sub<-180:
                    sub+=360
                while sub>180:
                    sub-=360
                #if (abs(sub)<10 and ds>10 and i>2) or i==1:
                if i>4 or bl==0:
                    self.mouse_move(sub)
                    self.ang=ang
                self.big_map[self.real_loc[0]-1:self.real_loc[0]+2,self.real_loc[1]-1:self.real_loc[1]+2]=49
                cv.imwrite('imgs/bigmap.jpg',self.big_map)
                nds=self.get_dis(self.real_loc,loc)
                print('upd',ds,sds,nds,self.real_loc,loc,sub)
                if nds<=ps or dls[-4]==nds or self.check('f',0.3901,0.5093):
                    pyautogui.keyUp('w')
                    #if type==0:
                    #    self.mouse_move(180)
                    #    self.press('w',0.3)
                    break
                ds=nds
                dls.append(ds)
            print('done!')
            if type==0:
                self.lst_tm=time.time()
            if type==1:
                pyautogui.click()
                time.sleep(1)
                pyautogui.click()
                time.sleep(1)
            if type==2 or type==3:
                key='sasddww'
                for i in range(7):
                    if i==0:
                        time.sleep(0.3)
                    self.get_screen()
                    if self.check('f',0.3901,0.5093):
                        for j in deepcopy(self.target):
                            if j[1]==type:
                                self.target.remove(j)
                    else:
                        self.press(key[i],0.2-0.1*(i==0))
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 300)
            else:
                self.target.remove((loc,type))
            print('loc',loc,self.real_loc)
        
    def mouse_move(self, x):
        if x>40:
            y=40
        elif x<-40:
            y=-40
        else:
            y=x
        dx = int(9800 * y * 1295 / self.real_width/180)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, 0)  # 进行视角移动
        time.sleep(0.05)
        if x!=y:
            self.mouse_move(x-y)

    def write_map(self,bw_map):
        for i in range(bw_map.shape[0]):
            for j in range(bw_map.shape[1]):
                if ((i-88)**2+(j-88)**2)>80**2:
                    bw_map[i,j]=0
                if bw_map[i,j]==255:
                    if self.big_map[self.now_loc[0]-88+i,self.now_loc[1]-88+j]<250:
                        self.big_map[self.now_loc[0]-88+i,self.now_loc[1]-88+j]+=50
        #cv.imwrite('imgs/tmps/tmp'+str(self.now_loc[0])+'_'+str(self.now_loc[1])+'_.jpg',bw_map)

    def get_loc(self,bw_map,rg=12,fbw=0):
        rge=88+rg
        loc_big=np.zeros((rge*2,rge*2),dtype=self.big_map.dtype)
        tpl=(self.now_loc[0],self.now_loc[1])
        x0,y0=max(rge-tpl[0],0),max(rge-tpl[1],0)
        x1,y1=max(tpl[0]+rge-self.big_map.shape[0],0),max(tpl[1]+rge-self.big_map.shape[1],0)
        loc_big[x0:rge*2-x1,y0:rge*2-y1]=self.big_map[tpl[0]-rge+x0:tpl[0]+rge-x1,tpl[1]-rge+y0:tpl[1]+rge-y1]
        max_val, max_loc=-1, 0
        bo_1=(bw_map==255)
        tt=4
        if self.find and fbw==0:
            tbw=cv.resize(bw_map,(176+tt*2,176+tt*2))
            tbw[tbw>150]=255
            tbw[tbw<=150]=0
            tbw=tbw[tt:176+tt,tt:176+tt]
            bo_2=(tbw==255)
            cv.imwrite('imgs/tbw.jpg',tbw)
        bo_3=(loc_big>=50)
        for i in range(rge*2-176):
            for j in range(rge*2-176):
                if (i-rge+88)**2+(j-rge+88)**2>rg**2:
                    continue
                p=np.count_nonzero(bo_3[i:i+176,j:j+176]&bo_1)
                if p>max_val:
                    max_val=p
                    max_loc=(i,j)
                if self.find and fbw==0:
                    p=np.count_nonzero(bo_3[i:i+176,j:j+176]&bo_2)
                    if p>max_val:
                        max_val=p
                        max_loc=(i,j)
        cv.imwrite('imgs/bwmap.jpg',bw_map)
        tp=deepcopy(loc_big[max_loc[0]:max_loc[0]+176,max_loc[1]:max_loc[1]+176])
        tp[86:90,86:90]=100
        cv.imwrite('imgs/maxloc.jpg',tp)
        if max_val==0:
            return
        self.now_loc=(max_loc[0]+88-rge+self.now_loc[0],max_loc[1]+88-rge+self.now_loc[1])
        self.real_loc=(self.now_loc[0],self.now_loc[1])
        print(self.real_loc,max_val)

    def get_map(self):
        x1,x2,y1,y2=0,8191,0,8191
        #self.big_map[4090:4097+5,4090:4097+5]=255
        while x1<8192 and np.sum(self.big_map[x1,:])==0:
            x1+=1
        while y1<8192 and np.sum(self.big_map[:,y1])==0:
            y1+=1
        while x2>0 and np.sum(self.big_map[x2,:])==0:
            x2-=1
        while y2>0 and np.sum(self.big_map[:,y2])==0:
            y2-=1
        if x1>=x2 or y1>=y2:
            return
        tp=deepcopy(self.big_map[x1-1:x2+2,y1-1:y2+2])
        tp[tp>=100]=255
        bk=deepcopy(tp)
        for i in range(tp.shape[0]):
            for j in range(tp.shape[1]):
                f=0
                for ii in range(0,1):
                    for jj in range(0,1):
                        if i+ii>=0 and j+jj>=0 and i+ii<tp.shape[0] and j+jj<tp.shape[1]:
                            if bk[i+ii,j+jj]==255:
                                f=1
                                break
                if f:
                    tp[i,j]=255
        tp[tp<100]=0
        cv.imwrite(self.map_file+'map_'+str(x1-1)+'_'+str(y1-1)+'_.jpg',tp)
        cv.imwrite(self.map_file+'target.jpg',tp)

    def extract_features(self,img):
        orb = cv.ORB_create()
        # 检测关键点和计算描述符
        keypoints, descriptors = orb.detectAndCompute(img, None)
        return descriptors
    
    def match_scr(self,img):
        key=self.extract_features(img)
        sim=-1
        ans=-1
        for i,j in self.img_set:
            matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
            try:
                matches = matcher.match(key, j)
                similarity_score = len(matches) / max(len(key), len(j))
                if similarity_score>sim:
                    sim=similarity_score
                    ans=i
            except:
                pass
        print(sim,ans)
        return ans
    
    def get_dis(self,x,y):
        return ((x[0]-y[0])**2+(x[1]-y[1])**2)**0.5
    
    def check_sred(self,sred,loc_scr,i,j):
        for k in range(max(0,i-2),min(i+2,loc_scr.shape[0])):
            for t in range(max(0,j-2),min(j+2,loc_scr.shape[1])):
                if not (sred==loc_scr[k,t]).all():
                    return 0
        return 1
        