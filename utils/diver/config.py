import os
from typing import List, Dict, Union
import yaml
import sys
import json

class Config:
    def __init__(self):
        self.abspath = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # 获取项目根目录../Auto_Simulated_Universe
        if getattr(sys, 'frozen', False):
            self.abspath = '.'
        self.angle = "1.0"
        self.difficult = "5"
        self.allow_difficult = [1, 2, 3, 4, 5]
        self.text = "info.yml"
        self.skill_char = ['符玄', '阮梅', '黄泉']

        # 推测定义的是远程角色
        self.long_range_list = ['丹恒饮月','克拉拉','青雀','波提欧','托帕账账','彦卿','符玄','砂金','三月七','娜塔莎','阮梅','知更鸟','布洛妮娅','艾丝妲','驭空','黑天鹅','瓦尔特杨','佩拉','大黑塔','忘归人','星期日','灵砂','缇宝']
        
        self.all_list = ['流萤','黄泉','波提欧','真理医生','丹恒饮月','瓦尔特杨','克拉拉','银枝','刃','希儿','景元','镜流','卡芙卡','托帕账账','黑天鹅','翡翠','云璃','砂金','椒丘','彦卿','姬子','杰帕德','藿藿','白露','阿兰','素裳','加拉赫','知更鸟','阮梅','布洛妮娅','花火','符玄','银狼','罗刹','寒鸦','卢卡','桂乃芬','虎克','艾丝妲','米沙','佩拉','黑塔','三月七','停云','桑博','雪衣','青雀','玲可','驭空','娜塔莎','希露瓦','大黑塔','忘归人','星期日','灵砂','缇宝']
        self.angles = [912,891,870,848,828,805,784,765,745,724,704,685,667,648,629,612,594,574,557,538,523,505,489,472,456,438,422,408,391,374,358,342,327,313,297,280,265,251,235,222,205,192,160,146,134,118,101,87,73,59,44,28,12,0,-14,-31,-45,-56,-76,-89,-99,-117,-131,-145,-152,-173,-196,-206,-221,-235,-255,-268,-284,-297,-311,-329,-339,-354,-375,-391,-407,-422,-440,-457,-473,-486,-506,-523,-540,-555,-576,-592,-613,-630,-649,-668,-687,-707,-725,-744,-765,-786,-807,-827,-849,-872,-893,-907,-918]
        self.angles = self.angles[::-1]
        self.long_press_sprint = 0
        self.debug_mode = 0
        self.speed_mode = 0
        self.weekly_mode = 0
        self.cpu_mode = 0
        self.save_cnt = 4
        self.accuracy = 1440
        self.enable_portal_prior = 0
        self.portal_prior = {'奖励':3, '事件':3, '战斗':2, '遭遇':2, '商店':1, '财富':1}
        self.team = '终结技'
        self.timezones = ['America', 'Asia', 'Europe', 'Default']
        self.timezone = 'Default'
        self.origin_key = ['f','m','shift','v','e','w','a','s','d','1','2','3','4']
        self.mapping = self.origin_key
        self.max_run = 34
        self.match = json.load(open('actions/character.json', 'r', encoding='utf-8'))
        self.read()

    @property
    def multi(self) -> float:
        x = float(self.angle)
        if x > 5:
            self.angle = '1.0'
            return 1.0
        elif x > 2:
            return x - 2
        else:
            return x

    @property
    def diffi(self) -> int:
        return int(self.difficult) if int(self.difficult) in self.allow_difficult else 5
    
    def clean_text(self, text, char=1):
        symbols = r"[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~—“”‘’«»„…·¿¡£¥€©®™°±÷×¶§‰]，。！？；：（）【】「」《》、￥"
        if char:
            symbols += r"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        translator = str.maketrans('', '', symbols)
        return text.translate(translator)
    
    def update_skill(self, skill: List[str]):
        self.skill_char = []
        for i in skill:
            i = self.clean_text(i, 0)

            # 匹配character.json中的数据,这里面是为了对策ocr无法准确识别导致的错别字么,但是还有很多别名?
            if i in self.match:
                i = self.match[i]

            # 匹配全部角色,是不是考虑配置为外部json更合适?
            if i in self.all_list:
                self.skill_char.append(i)

            elif i in ['1', '2', '3', '4']:
                self.skill_char.append(i)

        # 未导入log类,暂时用print应付调试
        print(f"秘技列表:{self.skill_char}")


    def read(self):
        if os.path.exists(os.path.join(self.abspath, self.text)):
            with open(os.path.join(self.abspath, self.text), "r", encoding="utf-8", errors='ignore') as f:
                config: Dict[str, Union[int, float, str, List[int]]] = yaml.safe_load(f)['config']
                try:
                    self.angle = str(config['angle'])
                    self.difficult = config['difficulty']
                    self.team = config['team']
                    self.speed_mode = config['speed_mode']
                    self.weekly_mode = config['weekly_mode']
                    self.cpu_mode = config['cpu_mode']
                    self.update_skill(config['skill'])
                    self.timezone = config['timezone']
                    self.max_run = config['max_run']
                    self.save_cnt = config['save']
                    self.accuracy = config['accuracy']
                    self.enable_portal_prior = config['enable_portal_prior']
                    self.portal_prior = config['portal_prior']
                except:
                    pass
            with open(os.path.join(self.abspath, self.text), "r", encoding="utf-8", errors='ignore') as f:
                try:
                    self.mapping = yaml.safe_load(f)['key_mapping']
                except:
                    pass
        else:
            self.save()

    def save(self):
        with open(os.path.join(self.abspath, self.text), "w", encoding="utf-8") as f:
            yaml.safe_dump({
                "config": {
                    "angle": float(self.angle),
                    "difficulty": self.diffi,
                    "team": self.team,
                    "speed_mode": self.speed_mode,
                    "weekly_mode": self.weekly_mode,
                    "cpu_mode": self.cpu_mode,
                    "skill": self.skill_char,
                    "save": self.save_cnt,
                    "timezone": self.timezone,
                    "max_run": self.max_run,
                    "accuracy": self.accuracy,
                    "enable_portal_prior": self.enable_portal_prior,
                    "portal_prior": self.portal_prior
                },
                "key_mapping": self.mapping
            }, f, allow_unicode=True, sort_keys=False)


config = Config()
