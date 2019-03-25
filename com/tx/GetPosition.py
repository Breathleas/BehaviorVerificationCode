# encoding=utf8
import cv2
import numpy as np
import random
from selenium.webdriver import ActionChains
import time
from selenium import webdriver
from PIL import Image
import os
import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC





def show(name):
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def getPostion(chunk, canves):
    otemp = chunk
    oblk = canves
    target = cv2.imread(otemp, 0)
    template = cv2.imread(oblk, 0)
    w, h = target.shape[::-1]
    temp = 'temp.jpg'
    targ = 'targ.jpg'
    cv2.imwrite(temp, template)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target = abs(255 - target)
    cv2.imwrite(targ, target)
    target = cv2.imread(targ)
    template = cv2.imread(temp)
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(), result.shape)
    return x, y
    # # 展示圈出来的区域
    # cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    # cv2.imwrite("yuantu.jpg", template)
    # show(template)


def get_track(distance):

    # 初速度
    v = 0
    # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
    t = 0.2
    # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
    tracks = []
    # 当前的位移
    current = 0
    # 到达mid值开始减速
    mid = distance * 7 / 8

    distance += 10  # 先滑过一点，最后再反着滑动回来
    # a = random.randint(1,3)
    while current < distance:
        if current < mid:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = random.randint(2, 4)  # 加速运动
        else:
            a = -random.randint(3, 5)  # 减速运动

        # 初速度
        v0 = v
        # 0.2秒时间内的位移
        s = v0 * t + 0.5 * a * (t ** 2)
        # 当前的位置
        current += s
        # 添加到轨迹列表
        tracks.append(round(s))

        # 速度已经达到v,该速度作为下次的初速度
        v = v0 + a * t

    # 反着滑动到大概准确位置
    for i in range(4):
        tracks.append(-random.randint(2, 3))
    for i in range(4):
        tracks.append(-random.randint(1, 3))
    return tracks


def urllib_download(imgUrl, imgSavePath):
    from urllib.request import urlretrieve
    urlretrieve(imgUrl, imgSavePath)


ssl._create_default_https_context = ssl._create_unverified_context
driver = webdriver.Chrome()
driver.get(
    "https://h5.kugou.com/apps/h5Verify/verify.html?thisurl=https%3A%2F%2Fcaptcha.guard.qcloud.com%2Ftemplate%2FTCapIframeApi.js%3Fappid%3D1253967378%26clientype%3D4%26lang%3D2052%26asig%3D3zTe0ZtlS_Vjq3cA_JQ1ZXhZy7f_B21po7cRaJZfhWCyHORe1c9usVnnn3NZwcNQc2v9WdLPq1qgdGKW5arV92iHgo8bl75s")
# time.sleep(5)
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID,'tcaptcha_iframe')))

driver.switch_to.frame(driver.find_element_by_xpath('//iframe[@id="tcaptcha_iframe"]'))
# time.sleep(1)
bkBlock = driver.find_element_by_xpath('//img[@id="bkBlock"]')
webImageWidth = bkBlock.size
webImageWidth = webImageWidth['width']
bkBlockX = bkBlock.location['x']
slideBlock = driver.find_element_by_xpath('//img[@id="slideBlock"]')
slideBlockX = slideBlock.location['x']
bkBlock = driver.find_element_by_xpath('//img[@id="bkBlock"]').get_attribute('src')
slideBlock = driver.find_element_by_xpath('//img[@id="slideBlock"]').get_attribute('src')
slidIng = driver.find_element_by_xpath('//div[@id="tcaptcha_drag_thumb"]')
os.makedirs('./image/', exist_ok=True)
urllib_download(bkBlock, './image/bkBlock.png')
urllib_download(slideBlock, './image/slideBlock.png')
imgBkBlock = Image.open('./image/bkBlock.png')
realWidth = (imgBkBlock.size)[0]
widthScale = float(realWidth) / float(webImageWidth)
position = getPostion('./image/bkBlock.png', './image/slideBlock.png')
realPosition = position[1] / widthScale
realPosition = realPosition - (slideBlockX - bkBlockX)
track_list = get_track(realPosition + 4)
ActionChains(driver).click_and_hold(on_element=slidIng).perform()  # 点击鼠标左键，按住不放
time.sleep(0.2)
# print('第二步,拖动元素')
for track in track_list:
    ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
    time.sleep(0.002)
ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()
time.sleep(1)
# print('第三步,释放鼠标')
ActionChains(driver).release(on_element=slidIng).perform()
time.sleep(3)

