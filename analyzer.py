# coding=utf-8
from PIL import Image
import os
import argparse
import matplotlib.pyplot as plt
import math

STHRESHOLD = 0.2
VTHRESHOLD = 0.2
HueArray = []
HueMap = []
peakList = {}
threshold = 0
smallWall = 0
scanMap = None
Tmp = 0
score1 = score3_1 = score3_2 = score4 = totalScore = 0
def getDataName(folder):
    dirs = os.listdir(folder)
    for dir in dirs:
        if 'png' in dir:
            getData(folder + "/" + dir, dir)
            break
def getEffectData(folder):
    for parent, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            if ".png" in filename: 
                imgFileName = os.path.join(parent, filename)
                if '\\' in parent:
                    prefix = parent.split('\\')
                    prefix.append(filename)
                    getData(imgFileName, "_".join(prefix[1:]))
                else:
                    getData(imgFileName, filename)
def getMultiData(folder):
    dirs= os.listdir(folder)
    print(dirs)
    for dir in dirs:
        getData(folder + "/" + dir + '/' + 'animate0.png', dir)
def getData(imgFileName, dir):
    global HueArray
    global HueMap
    global smallWall, threshold
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
        HueMap[int(math.floor(h))] += 1
        HueArray.append(h)
    
    # countPeak()
    print(imgFileName)
    threshold = len(HueArray) * 0.02
    smallWall = threshold * 0.05
    creat_plt_for_role(dir)
#根据阈值的区间计算法


def countPeak(): 
    global threshold, smallWall
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
def isOverlap(i, ptr):
    global Tmp
    for a in peakList.keys():
        if a == i: continue
        elif peakList[a][1] == ptr or peakList[a][0] == ptr: 
            Tmp = a
            return True
    return False
#峰合并判断
def canMerge(leftPeak, rightPeak, axis):
    global smallWall, HueMap, peakList
    global score1, score3_1, score3_2, score4, totalScore
    # #条件1
    #计算能到的区域
    leftptr = axis
    leftcount = 0
    while leftcount < peakList[leftPeak][3] * 0.1:
        leftptr -= 1
        if leftptr < 0:
            leftptr = 360
        leftcount += 1
    rightptr = axis
    rightcount = 0
    while rightcount < peakList[rightPeak][3] * 0.1:
        rightptr += 1
        if rightptr >360:
            rightptr = 0
        rightcount += 1
    #对区域内的值执行加权求和
    leftTolerance = 1 / float(leftcount)
    rightTolerance = 1 / float(rightcount)
    rangeSum = HueMap[axis]
    for i in range(max(leftcount, rightcount)):
        if leftcount > 0:
            tmp = axis - i if axis - i >= 0 else 360 + (axis - i) 
            rangeSum += (HueMap[tmp] * (1 - leftTolerance*i) * 2)
            leftcount -= 1
        if rightcount > 0:
            tmp = axis + i if axis + i < 360 else axis + i - 360 
            rangeSum += (HueMap[tmp] * (1 - rightTolerance*i) * 2)
            rightcount -= 1
    score1 = rangeSum * 0.2 / (peakList[leftPeak][2] + peakList[rightPeak][2])
    condition1 = score1 > 0.2

    #条件2
    # leftptr = axis
    # count = 0
    # leftsum = HueMap[leftPeak - 5:leftPeak] if leftPeak >= 5 else HueMap[:leftPeak] + HueMap[leftPeak - 5:]
    # rightsum = HueMap[rightPeak: rightPeak + 5] if rightPeak <= 355 else HueMap[rightPeak:] + HueMap[:365 - rightPeak]
    # leftsum = sum(leftsum)
    # rightsum = sum(rightsum)
    # while HueMap[axis] < leftsum * 0.2 * 0.1:
    #     leftptr -= 1
    #     if leftptr < 0:
    #         leftptr = 360
    #     count += 1
    # rightptr = axis
    # while HueMap[axis] < rightsum * 0.2 * 0.1:
    #     rightptr += 1
    #     if rightptr >360:
    #         rightptr = 0
    #     count += 1
    # condition2 = count / float(peakList[leftPeak][3] + peakList[rightPeak][3]) < 0.1

    #条件3
    condition3 = False
    peaksums = peakList[leftPeak][2] + peakList[rightPeak][2]
    score3_1 = peaksums / float(len(HueArray))
    score3_2 = max(peakList[leftPeak][2], peakList[rightPeak][2]) / float(peaksums)
    if score3_1 < 0.8 or score3_2 > 0.8:
        condition3 = True

    # #条件4
    condition4 = False
    rangeSums = peakList[leftPeak][3] + peakList[rightPeak][3]
    score4 = rangeSums / 360.0
    if score4 < 0.5:
        condition4 = True


    # totalScore = score1 - score3_1 + score3_2 * 2 - score4
    # return totalScore > 0.2
    return condition3
    
#最新的方法
def Peakgrow():
    global smallWall, HueMap, peakList, Tmp
    peakList = {}
    #计算峰值
    for i in range(len(HueMap)):
        compareLeft = HueMap[i - 10:i] if i >= 10 else HueMap[:i] + HueMap[i - 10:]
        compareRight = HueMap[i: i + 10] if i <= 350 else HueMap[i:] + HueMap[:370 - i]
        if HueMap[i] > smallWall * 5 and HueMap[i] > max(compareLeft) and HueMap[i] == max(compareRight):
            peakList[i] = [i, i, HueMap[i], 1, True, True] #左边界，右边界，和，区间长度, 左边是否截止，右是否截止    
    line = 0
    for k in peakList.keys():
        line = max(HueMap[k], line)
    hasSpread = True
    while hasSpread:#and line > smallWall#:
        hasSpread = False
        direction = -1  #0:左 1：右
        i = 0
        line = -1
        #检查是否有可以生长的峰
        for k,v in peakList.items():
            if v[4] and HueMap[v[0]] > line:
                i = k
                line = HueMap[v[0]]
                direction = 0
                hasSpread = True
            if v[5] and HueMap[v[1]] > line:
                i = k
                line = HueMap[v[1]]
                direction = 1
                hasSpread = True        
        #往左
        if direction == 0:
            cur = peakList[i][0]
            leftPtr = cur - 1 if cur > 0 else 360
            meanVal = HueMap[leftPtr]
            tmp = leftPtr
            for _ in range(4):
                leftPtr = leftPtr - 1 if leftPtr > 0 else 360
                meanVal += HueMap[leftPtr]
            meanVal /= 5
            leftPtr = tmp
            if meanVal == 0:
                peakList[i][4] = False
                continue
            if isOverlap(i, leftPtr):
                if canMerge(Tmp, i, leftPtr):
                    if HueMap[i] > HueMap[Tmp]:
                        reserve = i
                        delete = Tmp
                    else:
                        reserve = Tmp
                        delete = i
                    peakList[reserve] = [peakList[Tmp][0], peakList[i][1], peakList[i][2] + peakList[Tmp][2], peakList[i][3] + peakList[Tmp][3], peakList[Tmp][4], peakList[i][5]]
                    peakList.pop(delete)
                else:
                    peakList[i][4] = False
                haha = None
            else:
                peakList[i][0] = leftPtr
                peakList[i][2] += HueMap[leftPtr]
                peakList[i][3] += 1
        #往右
        if direction == 1:
            cur = peakList[i][1]
            rightPtr = cur + 1 if cur < 360 else 0
            meanVal = HueMap[rightPtr]
            tmp = rightPtr
            for _ in range(4):
                rightPtr = rightPtr + 1 if rightPtr < 360 else 0
                meanVal += HueMap[rightPtr]
            meanVal /= 5.0
            rightPtr = tmp
            if meanVal == 0:
                peakList[i][5] = False
            Tmp = 0
            if isOverlap(i, rightPtr):
                if canMerge(i, Tmp, rightPtr):
                    if HueMap[i] > HueMap[Tmp]:
                        reserve = i
                        delete = Tmp
                    else:
                        reserve = Tmp
                        delete = i
                    peakList[reserve] = [peakList[i][0], peakList[Tmp][1], peakList[i][2] + peakList[Tmp][2], peakList[i][3] + peakList[Tmp][3], peakList[i][4], peakList[Tmp][5]]
                    peakList.pop(delete)
                else:
                    peakList[i][5] = False
                haha = None
            else:
                peakList[i][1] = rightPtr
                peakList[i][2] += HueMap[rightPtr]
                peakList[i][3] += 1
    #log
    print(peakList)        
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
    # plt.figure()
    #直接画直方图
    # plt.subplot(211)
    plt.cla()
    plt.title(dir)
    plt.xlabel("Hue")
    plt.ylabel("PixelCount")
    plt.hist(HueArray, rwidth=1, bins=360, histtype='stepfilled')
    # ax = plt.gca()
    # plt.axhline(max(HueMap) * 0.05)
    # plt.axhline(len(HueArray) * 0.005)
    # plt.axhline(len(HueArray) * 0.005 * 0.05)

    #画自己计算的色调-像素数量数组
    # plt.subplot(212)
    # plt.cla()
    # plt.plot(HueMap)
    # plt.show()

    #计算峰值
    # getPeak()
    # Scan()
    Peakgrow()
    # plt.show()
    # plt.savefig("./role_hist/%s" % dir)


if __name__ == '__main__':
    getMultiData('D:/clients/resource/assets/role')
    # getDataName('D:/clients/resource/assets/role/1014')
    # getEffectData('D:/clients/resource/assets/effect')
    
    