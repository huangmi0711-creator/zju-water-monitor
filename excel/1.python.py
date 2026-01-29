import pandas as pd

# 路径定义
path = r'/Users/mimihouse/Desktop/python/data/demo.xlsx'
path2 = r'/Users/mimihouse/Desktop/python/data/demooutput.xlsx'

# --- 修正了缩进 ---
# 读取数据
df = pd.read_excel(path)

# 打印一下原始形状，确认列数是否为 2
print("原始数据形状:", df.shape)

# 重命名列 (前提：你的Excel必须正好有两列)
# 建议：如果列数不确定，最好不要用这种强制赋值的方法
df.columns = ["numbers", "names"]

# 设置索引
df.set_index("numbers", inplace=True)

# 打印剩余的列名 (因为 numbers 变成了索引，这里应该只打印出 names)
print("当前的列名:", df.columns)

# 保存文件
df.to_excel(path2)
print('finish!')
