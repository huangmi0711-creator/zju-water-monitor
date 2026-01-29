import pandas as pd

path = r'/Users/mimihouse/Desktop/python/data/demo.xlsx'
path2 = r'/Users/mimihouse/Desktop/python/data/demooutput2.xlsx'

# --- 修改重点 ---
# header=None 表示：不要把第一行当标题，所有行都是数据
# names=["numbers", "names"] 表示：直接在读取时就给这几列加上新名字
df = pd.read_excel(path, header=None, names=["numbers", "names"])

# 打印一下前几行，看看第一行原来的内容是不是回来了（变成了第0行数据）
print("--- 预览数据 ---")
print(df.head())

# 设置索引
df.set_index("numbers", inplace=True)

# 保存
df.to_excel(path2)
print('finish!')