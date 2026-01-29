import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib import font_manager
import platform
import openpyxl

# 1. 设置文件路径
file_path = r'/Users/mimihouse/Desktop/python/data/pollution degradation.xlsx'
output_path_cn = r'/Users/mimihouse/Desktop/python/data/CBZ_kinetics_CN_v3.tiff'
output_path_en = r'/Users/mimihouse/Desktop/python/data/CBZ_kinetics_EN_v3.tiff'


# ==========================================
# 核心读取函数 (保持不变)
# ==========================================
def get_cbz_data(excel_path, sheet_name):
    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        if sheet_name not in wb.sheetnames: return None
        data = list(wb[sheet_name].values)
        df = pd.DataFrame(data)
    except:
        return None

    col_index = None
    for c in range(df.shape[1]):
        if str(df.iloc[0, c]).strip() == "CBZ":
            col_index = c
            break
    if col_index is None: return None

    time_col, conc_col = None, None
    for i in range(6):
        if col_index + i >= df.shape[1]: break
        val = str(df.iloc[1, col_index + i]).strip().lower()
        if "时间" in val or "time" in val or "min" in val: time_col = col_index + i
        if "浓度" in val or "conc" in val or "um" in val: conc_col = col_index + i

    if time_col is None or conc_col is None: return None

    clean_df = pd.DataFrame({
        'time': pd.to_numeric(df.iloc[2:, time_col], errors='coerce'),
        'conc': pd.to_numeric(df.iloc[2:, conc_col], errors='coerce')
    })
    clean_df.dropna(inplace=True)
    return clean_df if len(clean_df) > 0 else None


# ==========================================
# 数据处理
# ==========================================
print("🚀 正在读取数据...")
final_data = get_cbz_data(file_path, 'result')
if final_data is None: final_data = get_cbz_data(file_path, 'Sheet1')

if final_data is None:
    print("❌ 错误: 无法读取有效数据。")
    exit()

data = final_data.copy()
min_time_idx = data['time'].idxmin()
C0 = data.loc[min_time_idx, 'conc']

data = data[data['conc'] > 0]
data['y_log'] = np.log(data['conc'] / C0)
data_fit = data[data['time'] > 0].copy()

slope, intercept, r_value, p_value, std_err = stats.linregress(data_fit['time'], data_fit['y_log'])
r_squared = r_value ** 2

line_x = np.array([data_fit['time'].min(), data_fit['time'].max()])
line_y = slope * line_x + intercept

print(f"回归方程: y = {slope:.4f}x {intercept:+.4f}")
print(f"R2: {r_squared:.4f}")


# ==========================================
# 绘图函数 (视觉优化版)
# ==========================================
def plot_chart(lang='cn', save_path=''):
    # --- 语言配置 ---
    if lang == 'cn':
        title_text = '卡马西平降解动力学'
        xlabel_text = '反应时间 (min)'
        ylabel_text = 'ln($C_t/C_0$)'
        legend_data = '实验数据'
        legend_fit = '线性拟合'
        font_title_prop = font_manager.FontProperties(family=chinese_font_name, size=18)
        font_label_prop = font_manager.FontProperties(family=chinese_font_name, size=15)
        font_legend_prop = font_manager.FontProperties(family=chinese_font_name, size=13)
    else:
        title_text = 'Degradation Kinetics of Carbamazepine'
        xlabel_text = 'Time (min)'
        ylabel_text = 'ln($C_t/C_0$)'
        legend_data = 'Experimental Data'
        legend_fit = 'Linear Fit'
        font_title_prop = font_manager.FontProperties(family='Arial', size=18, weight='bold')
        font_label_prop = font_manager.FontProperties(family='Arial', size=15)
        font_legend_prop = font_manager.FontProperties(family='Arial', size=13)

    plt.figure(figsize=(8, 6), dpi=300)

    # -------------------------------------------------------
    # 🎨 核心修改区域：大小、透明度、配色
    # -------------------------------------------------------

    # 1. 散点 (Sage Green 鼠尾草绿)
    # s=320: 增大3-4倍 (原80)
    # alpha=0.6: 降低透明度 (原0.9)
    plt.scatter(data_fit['time'], data_fit['y_log'],
                color='#8FBC8F',  # 新颜色: 莫兰迪绿
                s=320,  # 新大小: 320
                alpha=0.6,  # 新透明度: 0.6
                label=legend_data,
                edgecolors='white',  # 白边增加层次感
                linewidth=1.5,
                zorder=5)

    # 2. 拟合线 (Dusty Rose 干枯玫瑰)
    plt.plot(line_x, line_y,
             color='#BC8F8F',  # 新颜色: 莫兰迪粉棕
             linewidth=3,  # 线条稍微加粗一点点配合大点
             linestyle='--',
             label=legend_fit,
             zorder=4)

    # -------------------------------------------------------

    # 公式标注
    formula_text = f"y = {slope:.4f}x {intercept:+.4f}\n$R^2$ = {r_squared:.4f}"
    plt.text(0.95, 0.95, formula_text, transform=plt.gca().transAxes,
             fontsize=13, fontdict={'family': 'Arial'},
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='none'))

    # 装饰
    plt.title(title_text, fontproperties=font_title_prop, pad=20)
    plt.xlabel(xlabel_text, fontproperties=font_label_prop)
    plt.ylabel(ylabel_text, fontproperties=font_label_prop)

    plt.xticks(fontname='Arial', fontsize=13)
    plt.yticks(fontname='Arial', fontsize=13)

    plt.grid(False)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)

    plt.legend(prop=font_legend_prop, frameon=False, loc='lower left')

    plt.tight_layout()
    plt.savefig(save_path, format='tiff', dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    print(f"✅ [{lang.upper()}] 图片已保存: {save_path}")
    plt.close()


# 执行
system_name = platform.system()
chinese_font_name = 'Microsoft YaHei' if system_name == 'Windows' else 'Arial Unicode MS'

plot_chart(lang='cn', save_path=output_path_cn)
plot_chart(lang='en', save_path=output_path_en)