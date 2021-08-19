输入：hueMap色调像素直方图数组
1.选择峰值：
for i in range(hueMap):
    计算左边坐标
    计算右边坐标
    if 当前值值比阈值大，比左右值大：
        peakMap[当前值] = [开始坐标，结束坐标，范围内值总和, 左边界高度，右边界高度]
2.开始扩散：
def 合并判断(a, b, 触发合并坐标axis):
    条件1：sum(hueMap[axis - peakMap[a]边界范围 * 0.1 : axis + peakMap[a]边界范围] * 0.1) / (peakMap[a][总和] + peakMap[b][总和]) > 0.2
    条件2：[达到a峰10%高度的右坐标，达到b峰10%高度的左坐标] / (peakMap[a]边界范围 + peakMap[b]边界范围) < 0.5

line：水平线，初始为最高峰,用于同步探索
rangeMap:记录所有峰边界的Map，方便合并的判断
hasSpread:中止条件，单次循环中是否有扩散或者合并操作，初始True
while hasSpread：
    hasSpread = False
    for i in peakMap.keys():
        while peakMap[i][左边界] >= line:
            往左探索：
                计算出带循环的左边坐标
                对坐标带循环左方向取长度为5的窗口，计算窗口均值（带权其实感觉差不多）
                if 均值 > 阈值：
                    if 该步坐标 in rangeMap[其他峰] and 合并判断 == True：
                        在peakMap中删除合并操作中的小峰，更新peakMap[大峰]（总和增加，边界扩张，边界高度修改）
                    else：
                        将该步坐标对应参数加入peakMap[i]
            hasSpread = True
        while peakMap[i][右边界] >= line:
            往右探索，同左
            hasSpread = True
    #更新line为最低的一个边界
    for i in peakMap.keys():
        line = min(peakMap[i][左边界高度], peakMap[i][右边界高度], line)
3.从peakMap输出，可以按照像素和、色调范围排序然后输出


