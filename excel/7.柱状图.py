import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib import font_manager
import platform
import numpy as np # 引入numpy生成刻度序列

# 1. 设置文件路径
file_path = r'/Users/mimihouse/Desktop/python/data/pollution degradation.xlsx'
output_img_path = r'/Users/mimihouse/Desktop/python/data/degradation_bar_chart_v2.tiff'

# 2. 读取数据
try:
    df = pd.read_excel(file_path, sheet_name='comparison')
    df.sort_values(by='降解率', ascending=False, inplace=True)
except Exception as e:
    print(f"❌ 读取数据失败: {e}")
    exit()

# 3. --- 字体与颜色设置 ---
font_en = {'family': 'Arial', 'weight': 'normal'}

# 中文尝试用 微软雅黑 (Microsoft YaHei)，Mac回退到 Arial Unicode MS
system_name = platform.system()
if system_name == 'Darwin': # macOS
    font_names = [f.name for f in font_manager.fontManager.ttflist]
    if 'Microsoft YaHei' in font_names:
        chinese_font_name = 'Microsoft YaHei'
    else:
        chinese_font_name = 'Arial Unicode MS'
else:
    chinese_font_name = 'Microsoft YaHei'

# 字号设置 (加大 30%)
font_cn_label = font_manager.FontProperties(family=chinese_font_name, size=16)
font_title = font_manager.FontProperties(family=chinese_font_name, size=21)

# 莫兰迪色系
morandi_colors = [
    '#A0C1B8', '#7098DA', '#E0BBE4', '#FFDFD3',
    '#957DAD', '#D291BC', '#FEC8D8', '#FF9AA2'
]

# 4. 开始绘图
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

# 绘制柱状图 (宽度 0.54)
bars = ax.bar(df['污染物名称'], df['降解率'],
              color=morandi_colors[:len(df)],
              width=0.54,
              edgecolor=None)

# 5. 精细化设置字体

# (A) 标题
ax.set_title('污染物降解率对比', fontproperties=font_title, pad=25)

# (B) X轴和Y轴标签
ax.set_xlabel('污染物名称', fontproperties=font_cn_label, labelpad=10)
ax.set_ylabel('降解率', fontproperties=font_cn_label, labelpad=10)

# (C) X轴刻度标签 (这里修复了警告)
# -------------------------------------------------------
# 第一步：明确设置刻度的位置 (0, 1, 2, 3...)
ax.set_xticks(np.arange(len(df)))
# 第二步：再给这些位置贴上标签
ax.set_xticklabels(df['污染物名称'], fontdict=font_en, fontsize=14)
# -------------------------------------------------------

# (D) Y轴刻度标签
for label in ax.get_yticklabels():
    label.set_fontname('Arial')
    label.set_fontsize(13)

# 设置 Y 轴为百分比格式
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.set_ylim(0, 1.15)

# (E) 去掉边框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 6. 在柱子上方添加数值标签
for bar in bars:
    height = bar.get_height()
    if pd.notna(height):
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                 f'{height:.1%