from ppocronnx.predict_system import TextSystem
import numpy as np
import cv2 as cv
from utils.log import log

# mode: bless1 bless2 strange

class My_TS:
    def __init__(self,lang='ch'):
        self.lang=lang
        self.ts = TextSystem(use_angle_cls=False)
        self.ts.text_recognizer.postprocess_op.character.append(' ')
        self.text=''
        self.res=[]
        self.forward_img = None

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
        length = len(text)
        res = 0
        stext = self.text+' '
        for i in range(len(stext)-length):
            res |= self.is_edit_distance_at_most_one(text,stext[i:i+length],stext[i+length])
        return res

    def input(self,img):
        try:
            self.text=self.ts.ocr_single_line(img)[0].lower()
        except:
            self.text=''

    def sim_list(self,text_list,img=None):
        if img is not None:
            self.input(img)
        for t in text_list:
            if self.sim(t):
                return t
        return None

    def forward(self, img):
        if self.forward_img is not None and np.sum(np.abs(self.forward_img-img))<1e-6:
            return
        self.forward_img = img
        self.res = self.ts.detect_and_ocr(img)
        for res in self.res:
            res.box = [int(np.min(res.box[:,0])),int(np.max(res.box[:,0])),int(np.min(res.box[:,1])),int(np.max(res.box[:,1]))]

    def find_with_text(self, text=[]):
        ans = []
        for txt in text:
            for res in self.res:
                self.text = res.ocr_text
                if self.sim(txt):
                    print("识别到文本：",txt,"匹配文本：",self.text)
                    ans.append({'raw_text':res.ocr_text, 'text':text, 'box':res.box, 'score':res.score})
        return sorted(ans, key=lambda x: x['score'], reverse=True)

    def box_contain(self, box_out, box_in, redundancy):
        if type(redundancy) in [tuple, list]:
            r = redundancy
        else:
            r = (redundancy, redundancy)
        return box_out[0]<=box_in[0]+r[0] and box_out[1]>=box_in[1]-r[0] and box_out[2]<=box_in[2]+r[1] and box_out[3]>=box_in[3]-r[1]

    def find_with_box(self, box=None, redundancy=10):
        ans = []
        for res in self.res:
            if box is None:
                print(res.ocr_text, res.box)
            else:
                if self.box_contain(box, res.box, redundancy=redundancy):
                    ans.append({'raw_text':res.ocr_text, 'box':res.box, 'score':res.score})
        return sorted(ans, key=lambda x: x['score'], reverse=True)

class text_keys:
    def __init__(self,fate=4):
        self.fate=fate
        self.interacts = ['造物调试台', '复活装置']
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
