import cv2 as cv
import numpy as np
import time
import random
import sys
import os

# 删除地图数据中没用的文件
for file in os.listdir("imgs/maps"):
    pth = "imgs/maps/" + file + "/target.jpg"
    if os.path.exists(pth):
        image = cv.imread(pth)
        print(image.shape)
        for map in os.listdir("imgs/maps/" + file):
            if map == "bwmap.jpg":
                os.remove("imgs/maps/" + file + "/" + map)
            elif map != "init.jpg" and map != "target.jpg":
                map_img = cv.imread("imgs/maps/" + file + "/" + map)
                if map_img.shape != image.shape:
                    os.remove("imgs/maps/" + file + "/" + map)
