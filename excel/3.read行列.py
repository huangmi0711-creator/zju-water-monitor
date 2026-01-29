import pandas as pd

d ={"x":100,"y":200,"z":300}



import pandas as pd

s1 = pd.Series([1,2,3,],index = ['a','b','c'],name='dataA')
s2 = pd.Series([10,20,30],index = ['a','b','c'],name='dataB')
s3 = pd.Series([100,200,300],index = ['a','b','c'],name='datC')

df = pd.DataFrame({s1.name:s1,s2.name:s2,s3.name:s3})
print(df)

# 使用列表创建 Series
data = [1, 2, 3, 4, 5]
s = pd.Series(data)
print(s)
# 使用字典创建 Series
dict_data = {'a': 1, 'b': 2, 'c': 3}
s = pd.Series(dict_data)
print(s)


# 使用 NumPy 数组创建 Series
import numpy as np
np_data = np.array([1, 2, 3, 4, 5])
s = pd.Series(np_data)
print(s)

