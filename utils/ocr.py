from ppocronnx.predict_system import TextSystem
import numpy as np
import cv2 as cv

# mode: bless1 bless2 strange

class My_TS:
    def __init__(self,lang='ch'):
        self.lang=lang
        self.ts = TextSystem(use_angle_cls=False)
        self.text=''

    def sim(self,text,img=None):
        if img is not None:
            self.input(img)
        if len(self.text)<len(text)-1:
            return False
        text+='  '
        f = [[0,0] for _ in range(len(self.text)+1)]
        f[0][1]=1
        for i in range(len(self.text)):
            try:
                if self.text[i]==text[f[i][0]]:
                    f[i+1][0]=f[i][0]+1
                if self.text[i]==text[f[i][1]]:
                    f[i+1][1]=f[i][1]+1
            except:
                print(text,self.text)
                if self.text[i]==text[f[i][0]]:
                    f[i+1][0]=f[i][0]+1
                if self.text[i]==text[f[i][1]]:
                    f[i+1][1]=f[i][1]+1
            f[i+1][0]=max(f[i][0],f[i+1][0])
            f[i+1][1]=max(f[i][1],f[i+1][1],f[i][0]+1)
        return f[-1][1]>=len(text)-2
    
    def input(self,img):
        self.text=self.ts.ocr_single_line(img)[0].lower()

    def sim_list(self,text_list,img=None):
        if img is not None:
            self.input(img)
        for t in text_list:
            if self.sim(t):
                return t
        return None
        
    def split_and_find(self,key_list,img,mode=None):
        white=[255,255,255]
        yellow=[126,162,180]
        binary_image = np.zeros_like(img[:, :, 0])
        enhance_image = np.zeros_like(img)
        if mode=='strange':
            binary_image[np.sum((img - yellow) ** 2, axis=-1) <= 512]=255
            enhance_image[np.sum((img - yellow) ** 2, axis=-1) <= 3200]=[255,255,255]
        else:
            binary_image[np.sum((img - white) ** 2, axis=-1) <= 1600]=255
            enhance_image[np.sum((img - white) ** 2, axis=-1) <= 3200]=[255,255,255]
        if mode=='bless':
            kerneld = np.zeros((7,3),np.uint8) + 1
            kernele = np.zeros((1,39),np.uint8) + 1
            kernele2 = np.zeros((7,1),np.uint8) + 1
            binary_image = cv.dilate(binary_image,kerneld,iterations=2)
            binary_image = cv.erode(binary_image,kernele,iterations=5)
            binary_image = cv.erode(binary_image,kernele2,iterations=2)
            enhance_image = img
        else:
            kernel = np.zeros((5,9),np.uint8) + 1
            for i in range(2):
                binary_image = cv.dilate(binary_image,kernel,iterations=3)
                binary_image = cv.erode(binary_image,kernel,iterations=2)
        contours, _ = cv.findContours(binary_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        prior = len(key_list)
        rcx,rcy,find=-1,-1,0
        res=''
        text_res=''
        for c,contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            if h==binary_image.shape[0] or w<55:
                continue
            roi = enhance_image[y:y+h, x:x+w]
            cx = x + w // 2
            cy = y + h // 2
            self.input(roi)
            #cv.imwrite('tmp'+str(c)+'.jpg',roi)
            res+='|'+self.text
            for i,text in enumerate(key_list):
                if (self.sim(text) and prior>i) or rcx==-1:
                    rcx,rcy,find=cx,cy,1+(self.sim(text) and prior>i)
                    if find==2:
                        prior=i
                        text_res=text
        print('识别结果：',res+'|',' 识别到：',text_res)
        return (rcx-img.shape[1]//2,rcy-img.shape[0]//2),find

class text_keys:
    def __init__(self,fate=4):
        self.fate=fate
        self.interacts = ['黑塔','区域','事件','退出','沉浸','紧锁','复活','下载','模拟']
        self.fates = ["存护", "记忆", "虚无", "丰饶", "巡猎", "毁灭", "欢愉"]
        self.prior_bless = ['火堆外的夜']
        self.strange = ['福灵胶','博士之袍','降维骰子','信仰债券','时空棱镜','朋克洛德','香涎干酪']
        self.blesses = [[] for _ in range(7)]
        self.blesses[0] = ['零维强化','均晶转变','宏观偏析','超静定场','谐振传递','四棱锥体','聚塑','哨戒','亚共晶体','切变结构','弥合','迸裂晶格']
        self.blesses[1] = ['体验的富翁','全面记忆','第二次初恋','浮黎','缄默','纯真','难言的羞耻','怅然若失','麻木不仁','不寒而栗','特立独行','头晕目眩','多愁善感','沦浃肌髓']
        self.blesses[2] = ['苦难与阳光','怀疑的四重根','局外人','为何一切尚未消失','感官追奉者的葬礼','被装在套子里的人','旷野的呼告','存在的黄昏','火堆外的夜','知觉迷墙','虚妄贡品','日出之前','无根据颂歌','自欺咖啡馆','他人即地狱','开端与终结']
        self.blesses[3] = ['诸行无常','诸法无我','一法界心','施诸愿印','延彼遐龄','厌离邪秽苦','天人不动众','宝光烛日月','明澈琉璃身','法雨','胜军','灭罪累生善']
        self.blesses[4] = ['柘弓危矢','射不主皮','帝星君临','白矢决射御','云镝逐步离','彤弓素矰','背孤击虚']
        self.blesses[5] = ['极端氦闪','激变变星','寰宇热寂特征数','反物质非逆方程','法雨','戒律性闪变','危害性余光','毁灭性吸积','原生黑洞','轨道红移','预兆性景深','递增性末日','灾难性共振','破坏性耀发','偏振受体','永坍缩体','不稳定带','哨戒卫星','回光效应']
        self.blesses[6] = ['末日狂欢','开盖有奖','茫茫白夜','众生安眠','阴风阵阵','被涂污的信天翁','十二猴子与怒汉','操行满分','基本有害','灰暗的火','第二十一条军规','流吧你的眼泪']
        self.prior_bless += self.blesses[fate]
        self.strange = [self.fates[self.fate]+'火漆'] + self.strange