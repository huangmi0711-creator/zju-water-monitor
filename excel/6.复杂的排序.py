import pandas as pd

# 1. 设置文件路径
file_path = r'/Users/mimihouse/Desktop/python/data/pollution degradation.xlsx'

# 2. 读取数据 (使用 header=None 读取所有内容)
print("正在读取 Excel 文件...")
df = pd.read_excel(file_path, header=None)
print("读取成功，开始处理...")

# 3. 准备容器存放计算结果
summary_list = []
num_cols = df.shape[1]

# 4. 循环提取每一组数据
# 规律：从索引 1 开始 (ATL)，每隔 5 列是下一个污染物
for i in range(1, num_cols, 5):
    # 防止越界
    if i + 3 >= num_cols:
        break

    # 获取污染物名称 (在第0行)
    name = df.iloc[0, i]
    # 如果名字为空，说明读到了无效列，跳过
    if pd.isna(name):
        continue

    print(f"--> 正在处理污染物: {name}")

    # 提取“时间”列和“浓度”列的数据 (从第2行开始是数据)
    # i+1 是时间列, i+3 是浓度列
    # copy() 很重要，防止警告
    block_df = df.iloc[2:, [i + 1, i + 3]].copy()
    block_df.columns = ['time', 'conc']

    # === 关键修正：强制转换为数字 ===
    # errors='coerce' 表示如果遇到无法转换的非数字（比如空格、文字），直接变成 NaN (空值)
    block_df['time'] = pd.to_numeric(block_df['time'], errors='coerce')
    block_df['conc'] = pd.to_numeric(block_df['conc'], errors='coerce')

    # 去除时间或浓度为空的行 (清洗数据)
    block_df.dropna(subset=['time', 'conc'], inplace=True)

    # --- 查找时间点 ---
    # 使用浮点数比较，或者使用 isin 容错
    row_0 = block_df[block_df['time'] == 0]
    row_140 = block_df[block_df['time'] == 140]

    # 初始化变量
    c0 = None
    c140 = None
    rate = None
    note = "正常"

    # 获取 C0
    if not row_0.empty:
        c0 = row_0.iloc[0]['conc']
    else:
        note = "缺0min数据"
        print(f"   警告: {name} 找不到 0min 的数据")

    # 获取 C140
    if not row_140.empty:
        c140 = row_140.iloc[0]['conc']
    else:
        note = "缺140min数据" if note == "正常" else note + ", 缺140min"
        print(f"   警告: {name} 找不到 140min 的数据")

    # 计算降解率
    if c0 is not None and c140 is not None:
        if c0 != 0:
            # 公式: 1 - (140min浓度 / 0min浓度)
            rate = 1 - (c140 / c0)
        else:
            note = "初始浓度为0"
            rate = 0  # 避免除以0错误

    # 存入结果列表
    summary_list.append({
        '污染物名称': name,
        '初始浓度(0min)': c0,
        '最终浓度(140min)': c140,
        '降解率': rate,
        '备注': note
    })

# 5. 创建结果表格
if summary_list:
    result_df = pd.DataFrame(summary_list)

    # 按降解率从高到低排序 (把 None 的排在最后)
    result_df.sort_values(by='降解率', ascending=False, inplace=True)

    print("\n--- 计算结果预览 ---")
    print(result_df[['污染物名称', '降解率', '备注']].head())

    # 6. 保存到 Excel
    # 使用 openpyxl 引擎追加模式
    try:
        with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            result_df.to_excel(writer, sheet_name='comparison', index=False)
        print(f"\n✅ 成功！结果已保存到 sheet: comparison")
    except Exception as e:
        print(f"\n❌ 保存失败 (可能是文件被打开了): {e}")
else:
    print("\n❌ 未找到任何有效数据，请检查 Excel 格式是否变化。")