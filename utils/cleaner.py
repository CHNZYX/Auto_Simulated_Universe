import cv2 as cv
import numpy as np
import time
import random
import sys
import os

def get_center(img, i, j):
    rx, ry, rt = 0, 0, 0
    for x in range(-7, 7):
        for y in range(-7, 7):
            if (
                i + x >= 0
                and j + y >= 0
                and i + x < img.shape[0]
                and j + y < img.shape[1]
            ):
                s = np.sum(img[i + x, j + y])
                if s > 30 and s < 255 * 3 - 30:
                    rt += 1
                    rx += x
                    ry += y
    return (i + rx / rt, j + ry / rt)

def get_target(pth):
    img = cv.imread(pth)
    res = set()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            # 终点 黄
            if img[i, j, 2] > 180 and img[i, j, 1] > 180 and img[i, j, 0] < 70:
                res.add((get_center(img, i, j), 3))
                img[max(i - 7, 0) : i + 7, max(j - 7, 0) : j + 7] = [0, 0, 0]
    if len(res)==0:
        print('No end point:',pth)

# 删除地图数据中没用的文件
for file in os.listdir("imgs/maps"):
    pth = "imgs/maps/" + file + "/target.jpg"
    if os.path.exists(pth):
        get_target(pth)
        image = cv.imread(pth)
        #print(image.shape)
        for map in os.listdir("imgs/maps/" + file):
            if map == "bwmap.jpg":
                os.remove("imgs/maps/" + file + "/" + map)
            elif map != "init.jpg" and map != "target.jpg":
                map_img = cv.imread("imgs/maps/" + file + "/" + map)
                if map_img.shape != image.shape:
                    os.remove("imgs/maps/" + file + "/" + map)
