import openpyxl
import datetime

# 1. 设置文件路径
path = r'/Users/mimihouse/Desktop/python/data/demo.xlsx'
path2 = r'/Users/mimihouse/Desktop/python/data/demooutput3.xlsx'

# 2. 定义起始日期
start_date = datetime.date(2026, 1, 20)

# --- 核心修改：使用 openpyxl 直接加载原文件 ---
print("正在加载 Excel 文件...")
wb = openpyxl.load_workbook(path)
ws = wb.active  # 获取当前活动的 Sheet

# 3. 确定修改范围
# 您之前的代码是 skiprow=3，意味着前3行是跳过的
# 所以通常：第1-3行是无关信息，第4行是表头，数据从【第5行】开始
# 之前的 usecols="C:F"，对应 Excel 的第 3, 4, 5, 6 列
# 对应关系假设：C列=ID, D列=Name, E列=Instore, F列=Date

# 循环每一行数据（从第5行开始，直到有数据的最后一行）
# enumerate 从 0 开始计数，方便我们计算 ID 和日期增量
for i, row in enumerate(ws.iter_rows(min_row=5, min_col=3, max_col=6)):
    # row[0] -> C列 (ID)
    # row[1] -> D列 (Name)
    # row[2] -> E列 (Instore)
    # row[3] -> F列 (Date)

    # ---------------- 业务逻辑开始 ----------------

    # 1. 修改 ID (从1开始)
    current_id = i + 1
    row[0].value = current_id

    # 2. 修改 Name
    row[1].value = f"Name_{current_id}"

    # 3. 计算并修改 Date
    current_date = start_date + datetime.timedelta(days=i)
    row[3].value = current_date

    # 4. 修改 Instore (根据 Date 判断)
    # weekday(): 0-4是周一到周五(yes), 5-6是周六日(no)
    if current_date.weekday() < 5:
        row[2].value = 'yes'
    else:
        row[2].value = 'no'

    # ---------------- 业务逻辑结束 ----------------

# 4. 另存为新文件 (保留了原文件的所有格式和行列)
print("正在保存...")
wb.save(path2)
print('finish!')