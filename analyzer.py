from PIL import Image
import os
import argparse
import matplotlib.pyplot as plt
import math

STHRESHOLD = 0.2
VTHRESHOLD = 0.2
HueArray = []
HueMap = [0] * 361
threshold = 0
smallWall = 0
scanMap = None

def getDataName(folder):
    dirs = os.listdir(folder)
    for dir in dirs:
        if 'png' in dir:
            getData(folder + "/" + dir, dir)
            break
def getMultiDataName(folder):
    dirs= os.listdir(folder)
    print(dirs)
    for dir in dirs:
        getData(folder + "/" + dir + '/' + 'animate0.png', dir)
def getData(imgFileName, dir):
    global HueArray
    global HueMap
    HueMap = [0] * 361
    HueArray = []
    img = Image.open(imgFileName)
    for pixel in img.getdata():
        if pixel[3] != 255:
            continue
        r = float(pixel[0] / 255.0)
        g = float(pixel[1] / 255.0)
        b = float(pixel[2] / 255.0)
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        h = 0
        if cmax < VTHRESHOLD:
                continue
        if delta == 0 or delta / cmax < STHRESHOLD:
            continue
        if cmax == r:
            if g > b:
                h = ((g - b) / delta) * 60.0
            else:
                h = ((g - b) / delta) * 60.0 + 360
        elif cmax == g:
            h = ((b - r) / delta) * 60.0 + 120.0
        elif cmax == b:
            h = ((r - g) / delta) * 60 + 240.0
        HueMap[int(round(h))] += 1
        HueArray.append(h)
    
    countPeak()
    print(imgFileName)

    creat_plt_for_role(dir)
#根据阈值的区间计算法
def countPeak(): 
    global threshold, smallWall
    threshold = len(HueArray) * 0.02
    smallWall = threshold * 0.05
    peakArray = []
    state = 0
    begin, end = 0, 0
    for i in range(len(HueMap)):
        if i + 5 < len(HueMap):
            window = HueMap[i:i + 5]  
        else:
            tail = HueMap[i:-1]
            tail.extend(HueMap[:5 - (len(HueMap) - 1 - i)])
        windowValue = sum(window) / 5
        if state == 0 and windowValue > smallWall:
            begin = i
            state = 1
        if state == 1 and windowValue < smallWall:
            end = i
            state = 0
            if max(HueMap[begin:end + 1]) > threshold and end - begin > 10:
            # print(max(HueMap[begin:end + 1]))
                hue = (end + begin) // 2
                hueRange = end - hue
                peakArray.append((hue, hueRange))
    # print(peakArray)
#根据峰值区间生长的区间计算法
def getPeak():
    global smallWall
    #计算峰值
    peaks = []
    for i in range(len(HueMap)):
        left = i - 1 if i > 0 else len(HueMap) - 1
        right = i + 1 if i < len(HueMap) - 1 else 0
        if HueMap[i] > smallWall * 5 and HueMap[i] > HueMap[left] and HueMap[i] > HueMap[right]:
            peaks.append(i)
    print(peaks)
    #峰值区间生长
    visited = [False] * len(HueMap)
    ranges = []
    for i in range(len(peaks)):
        if visited[peaks[i]]:
            continue
        leftptr = rightptr = peaks[i]
        lowlasting = 0
        while leftptr > 0 and lowlasting < 5:
            if HueMap[leftptr] < smallWall:
                lowlasting += 1
            else:
                lowlasting = 0
            leftptr -= 1
            if leftptr in peaks:
                visited[leftptr] = True
        lowlasting = 0
        while rightptr < len(HueMap) - 1 and lowlasting < 5:
            if HueMap[rightptr] < smallWall:
                lowlasting += 1
            else:
                lowlasting = 0
            rightptr += 1
            if rightptr in peaks:
                visited[rightptr] = True
        ranges.append((leftptr, rightptr))
    #合并重叠区间
    res = []
    for start, end in ranges:
        if len(res) == 0 or res[-1][1] < start:
            res.append([start, end])
        else:
            res[-1][1] = max(res[-1][1], end)
    print(res)
    hueSelect = []
    #合并360 和 0
    if res[0][0] < 5 and res[-1][1] > 355:
        rangeHue = (res[0][1] + (360 - res[-1][0])) // 2
        selectedHue = res[-1][0] + rangeHue if res[-1][0] + rangeHue <= 360 else res[-1][0] + rangeHue - 360
        hueSelect.append([selectedHue, rangeHue])
        res.pop(0)
        res.pop(-1)
    #计算色调值和范围
    for i in res:
        tmpRange = (i[1] - i[0]) // 2
        tmpHue = i[0] + tmpRange
        hueSelect.append([tmpHue, tmpRange])
    print(hueSelect)
#扫描线计算法
def Scan():
    # scanMap = [[False] * max(HueMap) for _ in range(361)]
    # for i in range(len(scanMap)):
    #     scanMap[i][:HueMap[i]] = [True] * HueMap[i]

    # print(scanMap[222][:100])

    line = max(HueMap)
    peakList = {}
    while line > 100:
        isGrowing = False
        start = 0
        end = 0
        accumulateSum = 0
        peak = 0
        firstEnd = 0
        for i in range(len(HueMap)):
            if not isGrowing and HueMap[i] > line: #未在生长且大于线则开始生长
                start = i
                isGrowing = True
                accumulateSum = HueMap[i]
                peak = HueMap[i]
            elif isGrowing and (HueMap[i] < line or i == len(HueMap) - 1): #小于线或者到边界停止生长
                end = i
                isGrowing = False
                #处理边界
                # if start < 3:
                #     firstEnd = end
                # if i == len(HueMap) - 1:
                #     end = firstEnd
                #更新
                if peak in peakList:
                    if peakList[peak][2] / float(len(HueArray)) < 0.5: 
                        peakList[peak] = [start, end, accumulateSum, line]
                else:
                    peakList[peak] = [start, end, accumulateSum, line]
                accumulateSum = 0
                peak = 0
            elif isGrowing: #生长时更新峰和总和
                accumulateSum += HueMap[i]
                peak = max(peak, HueMap[i])
        print(line, peakList)
        line -= 5
    
    #处理占比过小的峰
    for key in peakList.keys():
        # print(peakList[key][2])
        if peakList[key][2] / float(len(HueArray)) < 0.05:
            peakList.pop(key)
    # print(peakList)
    #处理是否需要分割的双峰
    count = -1
    for key in peakList.keys():
        for subs in peakList.keys():
            if key == subs or key not in peakList or subs not in peakList:
                continue
            if peakList[subs][1] <= peakList[key][1] and peakList[subs][0] >= peakList[key][0]:
                # print(peakList[key], peakList[subs])
                if peakList[key][2] / float(len(HueArray)) > 0.8:
                    # print("small")
                    #选两个小的
                    if peakList[subs][0] - peakList[key][0] > peakList[key][1] - peakList[subs][1]:
                        peakList[count] = [peakList[key][0], peakList[subs][0] - 1, peakList[key][2] - peakList[subs][2], 0]
                    else:
                        peakList[count] = [peakList[subs][1] + 1, peakList[key][1], peakList[key][2] - peakList[subs][2], 0]
                    peakList.pop(key)
                else:
                    #选大的
                    peakList.pop(subs) 
    # print(peakList)
    #处理360 和0
    for key in peakList.keys():
        if key not in peakList.keys(): continue
        if peakList[key][0] < 3:
            for tail in peakList.keys():
                if tail not in peakList.keys() or key not in peakList.keys(): continue
                if peakList[tail][1] > 356:
                    larger = max(tail, key)
                    smaller = min(tail, key)
                    print(smaller, larger)
                    peakList[larger] = [peakList[tail][0], peakList[key][1], peakList[key][2] + peakList[tail][2], 0]
                    peakList.pop(smaller)
    print(peakList)

def creat_plt_for_role(dir):
    global HueArray
    plt.figure()
    #直接画直方图
    plt.subplot(211)
    plt.cla()
    plt.title(dir)
    plt.xlabel("Hue")
    plt.ylabel("PixelCount")
    plt.hist(HueArray, rwidth=1, bins=360, histtype='stepfilled')
    # plt.axhline(max(HueMap) * 0.05)
    # plt.axhline(len(HueArray) * 0.005)
    # plt.axhline(len(HueArray) * 0.005 * 0.05)

    #画自己计算的色调-像素数量数组
    plt.subplot(212)
    plt.plot(HueMap)

    #计算峰值
    # getPeak()
    Scan()

    plt.show()
    # plt.savefig("./role_hist/%s.png" % dir)


if __name__ == '__main__':
    # getMultiDataName('D:/clients/resource/assets/role')
    getDataName('D:/clients/resource/assets/role/1014')
    
    