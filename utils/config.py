import os
from typing import List


class Config:
    def __init__(self):
        self.order_text = "1 2 3 4"
        self.angle = "1.0"
        self.difficult = "2"
        self.allow_difficult = [1, 2, 3, 4, 5]
        self.text = "info.txt"
        self.fate = "巡猎"
        self.map_sha = ""
        self.fates = ["存护", "记忆", "虚无", "丰饶", "巡猎", "毁灭", "欢愉"]
        self.show_map_mode = False
        self.debug_mode = False
        self.speed_mode = False
        self.force_update = False
        self.read()

    @property
    def multi(self) -> float:
        return float(self.angle)

    @property
    def order(self) -> List[int]:
        return [int(i) for i in self.order_text.strip(' ').split(" ")]

    @property
    def diffi(self) -> int:
        return int(self.difficult) if int(self.difficult) in self.allow_difficult else 1

    def read(self):
        if os.path.exists(self.text):
            with open(self.text, "r", encoding="utf-8") as f:
                self.order_text = f.readline().strip()
                self.angle = f.readline().strip()
                try:
                    self.difficult = str(int(f.readline().strip()))
                    self.fate = f.readline().strip()
                    self.map_sha = f.readline().strip()
                except:
                    pass
        else:
            self.save()

    def save(self):
        with open(self.text, "w", encoding="utf-8") as f:
            f.write(
                f"{self.order_text}\n{self.angle}\n{self.diffi}\n{self.fate}\n{self.map_sha}"
            )


config = Config()
