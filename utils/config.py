import os
from typing import List, Dict, Union
import yaml

class Config:
    def __init__(self):
        self.order_text = "1 2 3 4"
        self.angle = "1.0"
        self.difficult = "2"
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
                    }
            }, f, allow_unicode=True, sort_keys=False)


config = Config()
