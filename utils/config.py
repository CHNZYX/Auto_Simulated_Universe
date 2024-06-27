import os
from typing import List, Dict, Union
import yaml
import sys


class Config:
    def __init__(self):
        self.abspath = os.path.dirname(os.path.dirname(__file__))  # 获取项目根目录../Auto_Simulated_Universe
        if getattr(sys, 'frozen', False):
            self.abspath = '.'
        self.angle = "1.0"
        self.difficult = "5"
        self.allow_difficult = [1, 2, 3, 4, 5]
        self.text = "info.yml"
        self.skill_char = ['符玄', '黄泉']
        self.angles = [912,891,870,848,828,805,784,765,745,724,704,685,667,648,629,612,594,574,557,538,523,505,489,472,456,438,422,408,391,374,358,342,327,313,297,280,265,251,235,222,205,192,160,146,134,118,101,87,73,59,44,28,12,0,-14,-31,-45,-56,-76,-89,-99,-117,-131,-145,-152,-173,-196,-206,-221,-235,-255,-268,-284,-297,-311,-329,-339,-354,-375,-391,-407,-422,-440,-457,-473,-486,-506,-523,-540,-555,-576,-592,-613,-630,-649,-668,-687,-707,-725,-744,-765,-786,-807,-827,-849,-872,-893,-907,-918]
        self.angles = self.angles[::-1]
        self.long_press_sprint = 0
        self.debug_mode = 0
        self.speed_mode = 0
        self.cpu_mode = 0
        self.team = '终结技'
        self.timezones = ['America', 'Asia', 'Europe', 'Default']
        self.timezone = 'Default'
        self.origin_key = ['f','m','shift','v','e','w','a','s','d','1','2','3','4']
        self.mapping = self.origin_key
        self.max_run = 34
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
    def order(self) -> List[int]:
        return [int(i) for i in self.order_text.strip(" ").split(" ")]

    @property
    def diffi(self) -> int:
        return int(self.difficult) if int(self.difficult) in self.allow_difficult else 1

    def read(self):
        if os.path.exists(os.path.join(self.abspath, self.text)):
            with open(os.path.join(self.abspath, self.text), "r", encoding="utf-8", errors='ignore') as f:
                config: Dict[str, Union[int, float, str, List[int]]] = yaml.safe_load(f)['config']
                try:
                    self.angle = str(config['angle'])
                    self.difficult = config['difficulty']
                    self.team = config['team']
                    self.speed_mode = config['speed_mode']
                    self.cpu_mode = config['cpu_mode']
                    self.skill_char = config['skill']
                    self.timezone = config['timezone']
                    self.max_run = config['max_run']
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
                    "cpu_mode": self.cpu_mode,
                    "skill": self.skill_char,
                    "timezone": self.timezone,
                    "max_run": self.max_run
                },
                "key_mapping": self.mapping
            }, f, allow_unicode=True, sort_keys=False)


config = Config()
