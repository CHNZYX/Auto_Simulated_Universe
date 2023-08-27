import os
from typing import List, Dict, Union
import yaml

class Config:
    def __init__(self):
        self.order_text = "1 2 3 4"
        self.angle = "1.0"
        self.difficult = "4"
        self.allow_difficult = [1, 2, 3, 4, 5]
        self.text = "info.yml"
        self.fate = "巡猎"
        self.map_sha = ""
        self.fates = ["存护", "记忆", "虚无", "丰饶", "巡猎", "毁灭", "欢愉"]
        self.show_map_mode = 0
        self.debug_mode = 0
        self.speed_mode = 0
        self.force_update = 0
        self.unlock = 0
        self.bonus = 0
        self.timezones = ['America', 'Asia','Europe','Default']
        self.timezone = 'Default'
        self.read()

    @property
    def multi(self) -> float:
        return float(self.angle)

    @property
    def order(self) -> List[int]:
        return [int(i) for i in self.order_text.strip(" ").split(" ")]

    @property
    def diffi(self) -> int:
        return int(self.difficult) if int(self.difficult) in self.allow_difficult else 1

    def read(self):
        if os.path.exists(self.text):
            with open(self.text, "r", encoding="utf-8",errors='ignore') as f:
                config: Dict[str,Union[int,float,str,List[int]]] = yaml.safe_load(f)['config']
                try:
                    self.order_text = " ".join(str(x) for x in config['order_text'])
                    self.angle = str(config['angle'])
                    self.difficult = config['difficulty']
                    self.fate = config['fate']
                    self.map_sha = config['map_sha']
                    self.show_map_mode = config['show_map_mode']
                    self.debug_mode = config['debug_mode']
                    self.speed_mode = config['speed_mode']
                    self.force_update = config['force_update']
                    self.timezone = config['timezone']
                except:
                    pass
        else:
            self.save()

    def save(self):
        try:
            with open(self.text, "r", encoding="utf-8",errors='ignore') as f:
                prior = yaml.safe_load(f)['prior']
        except:
            try:
                with open('info_example.yml', "r", encoding="utf-8",errors='ignore') as f:
                    prior = yaml.safe_load(f)['prior']
            except:
                prior = {'奇物': ['福灵胶', '博士之袍', '降维骰子', '信仰债券', '时空棱镜', '朋克洛德', '香涎干酪'], '事件': ['购买1个星祝福', '购买一个', '跳上右边的砖块', '丢下雕像', '和序列扑满玩', '信仰星神', '克里珀的恩赐', '哈克的藏品', '动作片', '感恩克里珀星神'], '存护': ['零维强化', '均晶转变', '共晶反应', '宏观偏析', '超静定场', '谐振传递', '四棱锥体', '聚塑', '哨戒', '亚共晶体', '切变结构', '弥合', '迸裂晶格'], '记忆': ['体验的富翁', '全面记忆', '第二次初恋', '浮黎', '缄默', '纯真', '难言的羞耻', '怅然若失', '麻木不仁', '不寒而栗', '特立独行', '头晕目眩', '多愁善感', '沦浃肌髓'], '虚无': ['局外人', '苦难与阳光', '怀疑的四重根', '为何一切尚未消失', '感官追奉者的葬礼', '被装在套子里的人', '旷野的呼告', '存在的黄昏', '火堆外的夜', '知觉迷墙', '虚妄贡品', '日出之前', '无根据颂歌', '自欺咖啡馆', '他人即地狱', '开端与终结'], '丰饶': ['诸行无常', '诸法无我', '一法界心', '施诸愿印', '延彼遐龄', '厌离邪秽苦', '天人不动众', '宝光烛日月', '明澈琉璃身', '法雨', '胜军', '灭罪累生善'], '巡猎': ['柘弓危矢', '射不主皮', '帝星君临', '白矢决射御', '云镝逐步离', '彤弓素矰', '背孤击虚'], '毁灭': ['激变变星', '极端氦闪', '事件视界', '寰宇热寂特征数', '反物质非逆方程', '戒律性闪变', '危害性余光', '毁灭性吸积', '原生黑洞', '轨道红移', '预兆性景深', '递增性末日', '灾难性共振', '破坏性耀发', '偏振受体', '永坍缩体', '不稳定带', '哨戒卫星', '回光效应'], '欢愉': ['末日狂欢', '开盖有奖', '茫茫白夜', '众生安眠', '阴风阵阵', '被涂污的信天翁', '十二猴子与怒汉', '操行满分', '基本有害', '灰暗的火', '第二十一条军规', '流吧你的眼泪']}
        with open(self.text, "w", encoding="utf-8") as f:
            yaml.safe_dump({
                "config":{
                    "order_text": list(map(lambda x:int(x),self.order_text.split(' '))),
                    "angle": float(self.angle),
                    "difficulty": self.diffi,
                    "fate": self.fate,
                    "map_sha": self.map_sha,
                    "show_map_mode": self.show_map_mode,
                    "debug_mode": self.debug_mode,
                    "speed_mode": self.speed_mode,
                    "force_update": self.force_update,
                    "timezone": self.timezone
                    },
                "prior": prior
            }, f, allow_unicode=True, sort_keys=False)


config = Config()
