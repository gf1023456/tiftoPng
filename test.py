import numpy as np

# 原始的 clevs 和 cdict
clevs_original = [1.80, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83, 1.835, 1.84, 1.845, 1.85, 1.855, 1.86, 1.865, 1.87,
                      1.89]
cdict_original =[
                [16, 40, 104], [19, 86, 129], [26, 121, 139], [30, 154, 135], [25, 170, 115], [14, 195, 66],
                [1, 218, 5], [79, 224, 3], [164, 240, 7], [250, 251, 5], [242, 214, 6], [238, 187, 13],
                [236, 160, 20], [221, 125, 34], [203, 100, 46], [190, 87, 58]
            ]

# 生成新的 clevs，范围是 5 到 2500
clevs_new = np.linspace(0.5, 1.3, len(clevs_original))

# 假设我们想将原始的 cdict 映射到新的 clevs 上
# 下面是通过线性插值的方式重新生成 cdict

# 转换原始 cdict 为 numpy 数组，方便插值
cdict_array = np.array(cdict_original) / 255  # 归一化到 [0, 1] 范围

# 线性插值 cdict 对应的颜色
cdict_new = []
for i in range(3):  # 3 个颜色通道
    cdict_new.append(np.interp(np.linspace(0, len(cdict_original)-1, len(clevs_new)),
                               np.arange(len(cdict_original)), cdict_array[:, i]))

# 转换回 [0, 255] 范围
cdict_new = np.array(cdict_new).T * 255

# 输出新的 clevs 和 cdict
print("New clevs:", clevs_new)
print("New cdict:", cdict_new)
