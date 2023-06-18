from ppocronnx.predict_system import TextSystem
import cv2 as cv
import time
import utils.ocr as ocr

text_sys = ocr.My_TS()
img = cv.imread('imgs/mask.jpg')
res = text_sys.split_and_find(img)