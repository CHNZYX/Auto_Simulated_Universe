from utils.onnxocr.onnx_paddleocr import ONNXPaddleOcr
import numpy as np
import cv2 as cv
from utils.log import log

# mode: bless1 bless2 strange

class My_TS:
    def __init__(self,lang='ch'):
        self.lang=lang
        self.ts = ONNXPaddleOcr(use_angle_cls=False)
        self.text=''

    def is_edit_distance_at_most_one(self, str1, str2, ch):
        length = len(str1)
        diff_count = sum(1 for i in range(length) if str1[i] != str2[i])
        if diff_count <= 1:
            return 1
        i = 0
        j = 0
        diff_count = 0
        str2 += ch
        while i < length and j < length + 1:
            if str1[i] != str2[j]:
                diff_count += 1
                j += 1
            else:
                i += 1
                j += 1

        return diff_count <= 1

    def sim(self,text,img=None):
        if img is not None:
            self.input(img)
        self.text = self.text.strip()
        if text.strip() in ['胜军','脊刺','佩拉']:
            return text.strip() in self.text
        length = len(text)
        res = 0
        stext = self.text+' '
        for i in range(len(stext)-length):
            res |= self.is_edit_distance_at_most_one(text,stext[i:i+length],stext[i+length])
        return res

    def ocr_one_row(self, img):
        return self.ts.text_recognizer([img])[0][0]

    def input(self,img):
        try:
            self.text=self.ocr_one_row(img).lower()
        except:
            self.text=''

    def sim_list(self,text_list,img=None):
        if img is not None:
            self.input(img)
        for t in text_list:
            if self.sim(t):
                return t
        return None

    def split_and_find(self,key_list,img,mode=None,bless_skip=1):
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
        rcx,rcy,find,black=-1,-1,0,0
        res=''
        text_res='.'
        for c,contour in enumerate(contours):
            x, y, w, h = cv.boundingRect(contour)
            if h==binary_image.shape[0] or w<55:
                continue
            roi = enhance_image[y:y+h, x:x+w]
            cx = x + w // 2
            cy = y + h // 2
            self.input(roi)
            if len(self.text.strip())<=1:
                continue
            if find == 0:
                rcx,rcy,find,text_res = cx,cy,1,self.text+';'
            res+='|'+self.text
            if (self.sim('回归不等式') and bless_skip) or self.sim_list(['银河大乐透','普通八卦','愚者面具','机械齿轮']) is not None:
                black = 1
                res+='x'
                continue
            if find == 1:
                rcx,rcy,text_res=cx,cy,self.text+'?'
            for i,text in enumerate(key_list):
                if i==prior:
                    break
                if self.sim(text):
                    rcx,rcy,find=cx,cy,2
                    text_res=text+'!'
                    prior=i
        print('识别结果：',res+'|',' 识别到：',text_res)
        if black and find==1:
            find=3
        return (rcx-img.shape[1]//2,rcy-img.shape[0]//2),find+black
    
    def find_text(self, img, text, env=None):
        self.nothing = 1
        results = self.ts.ocr(img)
        for txt in text:
            for res in results:
                res = {'raw_text': res[1][0], 'box': np.array(res[0]), 'score': res[1][1]}
                self.text = res['raw_text']
                if len(self.text.strip())>1 and 'UID' not in self.text:
                    self.nothing = 0
                if self.sim(txt):
                    print("识别到文本：",txt,"匹配文本：",self.text)
                    return res['box']
        return None

class text_keys:
    def __init__(self,fate=4):
        self.fate=fate
        self.interacts = ['黑塔', '区域', '事件', '退出', '沉浸', '紧锁', '复活', '下载', '模拟']
        self.fates = ["存护", "记忆", "虚无", "丰饶", "巡猎", "毁灭", "欢愉", "繁育", "智识"]
        self.prior_bless = ['火堆外的夜']
        self.strange = []
        self.blesses = [[] for _ in range(9)]
        self.strange = ['福灵胶', '博士之袍', '陨石球', '降维骰子', '信仰债券', '时空棱镜', '朋克洛德', '香涎干酪',
                        '龋齿星系']
        self.blesses[0] = ['零维强化', '均晶转变', '共晶反应', '宏观偏析', '超静定场', '谐振传递', '四棱锥体', '聚塑',
                           '哨戒', '亚共晶体', '切变结构', '弥合', '迸裂晶格']
        self.blesses[1] = ['体验的富翁', '全面记忆', '第二次初恋', '浮黎', '缄默', '纯真', '难言的羞耻', '怅然若失',
                           '麻木不仁', '不寒而栗', '特立独行', '头晕目眩', '多愁善感', '沦浃肌髓']
        self.blesses[2] = ['苦难与阳光', '怀疑的四重根', '局外人', '为何一切尚未消失', '感官追奉者的葬礼',
                           '被装在套子里的人', '旷野的呼告', '存在的黄昏', '火堆外的夜', '知觉迷墙', '虚妄贡品',
                           '日出之前', '无根据颂歌', '自欺咖啡馆', '他人即地狱', '开端与终结']
        self.blesses[3] = ['诸行无常', '诸法无我', '一法界心', '施诸愿印', '延彼遐龄', '厌离邪秽苦', '天人不动众',
                           '宝光烛日月', '明澈琉璃身', '法雨', '胜军', '灭罪累生善']
        self.blesses[4] = ['柘弓危矢', '射不主皮', '帝星君临', '白矢决射御', '云镝逐步离', '彤弓素矰', '背孤击虚']
        self.blesses[5] = ['激变变星', '极端氦闪', '事件视界', '寰宇热寂特征数', '反物质非逆方程', '戒律性闪变',
                           '危害性余光', '毁灭性吸积', '原生黑洞', '轨道红移', '预兆性景深', '递增性末日', '灾难性共振',
                           '破坏性耀发', '偏振受体', '永坍缩体', '不稳定带', '哨戒卫星', '回光效应']
        self.blesses[6] = ['末日狂欢', '开盖有奖', '茫茫白夜', '众生安眠', '阴风阵阵', '被涂污的信天翁',
                           '十二猴子与怒汉', '操行满分', '基本有害', '灰暗的火', '第二十一条军规', '流吧你的眼泪']
        self.blesses[7] = ['刺吸口器', '结晶鳌刺', '酚类物质', '子囊释放', '菌种脓疤', '镰刀肢足', '腐殖疮', '裂解酶',
                           '代谢腔', '裸脑质', '代谢腔', '催化剂', '节间膜', '孢夹', '骨刃', '鳞翅', '脊刺', '槽针',
                           '液囊']
        self.blesses[8] = ['34型灰质', '2型杏仁核', '18型枕叶', '前庭系统', '递质合成', '外显记忆', '触觉通路',
                           '阈下知觉', '纹状皮层', '跳跃传导', '齿轮啮合的王座', '导线弯绕的指环', '能量变距的权杖',
                           '偏时引燃的炬火', '延迟衍射的烛光', '金属斑驳的华盖', '线圈编制的罗琦', '管道交错的桂冠']
        self.secondary = ['巡猎', '毁灭', '丰饶']
        try:
            import yaml
            with open('info.yml', "r", encoding="utf-8",errors='ignore') as f:
                config = yaml.safe_load(f)['prior']
            with open('info.yml', "r", encoding="utf-8",errors='ignore') as f:
                try:
                    self.secondary = yaml.safe_load(f)['config']['secondary_fate']
                except:
                    pass
            for i,j in enumerate(config):
                if i>1:
                    self.blesses[i-2] = config[j]
                elif i==0:
                    self.strange = config[j]
        except:
            pass
        self.prior_bless += self.blesses[fate]
        self.skip = 1
        for s in self.prior_bless:
            if '回归不等式' in s:
                self.skip = 0
        self.strange = [self.fates[self.fate]+'火漆'] + self.strange
        self.secondary = [self.fates[self.fate]] + self.secondary
