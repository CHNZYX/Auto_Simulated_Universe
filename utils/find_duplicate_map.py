import cv2 as cv
import os


def extract_features(img):
    orb = cv.ORB_create()
    # 检测关键点和计算描述符
    keypoints, descriptors = orb.detectAndCompute(img, None)
    return descriptors


# 加载图片集
def load_images(path):
    img_set = []
    for file in os.listdir(path):
        pth = path + "/" + file + "/init.jpg"
        if os.path.exists(pth):
            image = cv.imread(pth)
            img_set.append((file, extract_features(image)))
    return img_set


def filter_similar_images(img_set, threshold):
    similar_images = []
    for i in range(len(img_set)):
        current_img = img_set[i][1]
        sim = -1
        similar_img_index = -1
        for j in range(i + 1, len(img_set)):
            matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
            try:
                matches = matcher.match(current_img, img_set[j][1])
                similarity_score = len(matches) / max(
                    len(current_img), len(img_set[j][1])
                )
                if similarity_score > sim:
                    sim = similarity_score
                    similar_img_index = j
            except:
                pass
        if sim >= threshold:
            similar_images.append((img_set[i][0], img_set[similar_img_index][0], sim))
    return similar_images


path = "../imgs/maps"
print(filter_similar_images(load_images(path), 0.5))
