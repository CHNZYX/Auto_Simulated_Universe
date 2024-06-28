import cv2 as cv
import numpy as np
import time
import random
import sys
import os
from shutil import copy


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
    f_set = [
        lambda p: p[2] < 85 and p[1] < 85 and p[0] > 180,  # 路径点 蓝
        lambda p: p[2] > 180 and p[1] < 70 and p[0] < 70,  # 怪 红
        lambda p: p[2] < 90 and p[1] > 150 and p[0] < 90,  # 交互点 绿
        lambda p: p[2] > 180 and p[1] > 180 and p[0] < 70,  # 终点 黄
    ]
    p_cnt = [0,0,0,0]
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(4):
                if f_set[k](img[i, j]):
                    p = get_center(img, i, j)
                    res.add((p, k))
                    img[max(i - 7, 0) : i + 7, max(j - 7, 0) : j + 7] = [0, 0, 0]
                    p_cnt[k]+=1
    if p_cnt[3]==0:
        print(pth,'no end point')
    if p_cnt[1]!=0 and p_cnt[2]!=0:
        print(pth,'wrong interactive point')

'''
big_minimap = [10538,11115,12345,12346,12872,13197,18769,19787,22212,23480,30797,31289,38866,40978,42250,43642,45516,45735,46900,4805,51202,52451,53073,56417,63533,65515,65576,67673,68145,70941,73927,74959,75973,78566,81866,85880,86757,89054,89201,89358,9011,96641,97964,9908,99257,99570]

for file in os.listdir("imgs/maps"):
    if len(file)<=5 and int(file) not in big_minimap:
        for map in os.listdir("imgs/maps/" + file):
            os.remove("imgs/maps/" + file + "/" + map)
        os.removedirs("imgs/maps/"+file)
for file in os.listdir('tmp'):
    print(file.split('.')[0],end=',')
exit()
'''
# 删除地图数据中没用的文件
for file in os.listdir("imgs/maps"):
    pth = "imgs/maps/" + file + "/target.jpg"
    if os.path.exists(pth):
        get_target(pth)
        copy(os.getcwd()+'\\'+"imgs/maps/" + file + "/target.jpg",os.getcwd()+'\\'+'targ')
        os.rename('targ/target.jpg','targ/'+str(file)+'.jpg')
        #image = cv.imread(pth)
        # for map in os.listdir("imgs/maps/" + file):
        #     if map == "bwmap.jpg":
        #         os.remove("imgs/maps/" + file + "/" + map)
        #     elif map != "init.jpg" and map != "target.jpg":
        #         map_img = cv.imread("imgs/maps/" + file + "/" + map)
        #         if map_img.shape != image.shape:
        #             os.remove("imgs/maps/" + file + "/" + map)
