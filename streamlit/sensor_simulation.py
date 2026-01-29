import streamlit as st
import pandas as pd
import numpy as np
import time


# ==========================================
# 第一部分：定义“物理引擎” (Phase 2 新增内容)
# ==========================================

class VirtualSensor:
    """
    模拟真实的物理传感器：具有惯性（不会突变）和噪声。
    """

    def __init__(self, name, base_value, volatility):
        self.name = name
        self.current_value = base_value
        self.volatility = volatility  # 波动性

    def read_value(self):
        # 1. 随机游走 (Random Walk): 基于上一次的值进行微小漂移
        drift = np.random.normal(0, self.volatility)
        self.current_value += drift

        # 2. 添加测量白噪声 (电子元件的抖动)
        noise = np.random.normal(0, 0.02)
        final_value = self.current_value + noise

        # 3. 物理约束 (防止数据跑偏太远)
        if "pH" in self.name:
            # pH 被强行限制在 6.0 到 9.0 之间回弹
            if final_value > 9.0: self.current_value -= 0.1
            if final_value < 6.0: self.current_value += 0.1
            final_value = np.clip(final_value, 0, 14)
        elif "氨氮" in self.name:
            # 氨氮不能小于0
            final_value = max(0, final_value)

        return round(final_value, 2)


# ==========================================
# 第二部分：初始化系统记忆 (关键！)
# ==========================================
st.set_page_config(page_title="SNAPP 智慧水务终端", layout="wide")

# 如果系统里还没有传感器，就造两个新的存起来
if 'sensors' not in st.session_state:
    st.session_state['sensors'] = {
        'ph_sensor': VirtualSensor("pH传感器", base_value=7.0, volatility=0.05),
        'nh3_sensor': VirtualSensor("氨氮传感器", base_value=0.5, volatility=0.02)
    }

# 如果系统里还没有历史数据，就造一个空的列表
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = pd.DataFrame(columns=['Time', 'pH', 'Ammonia'])

# ==========================================
# 第三部分：页面布局与逻辑
# ==========================================

st.title("🌊 智慧水务实时监测系统 (Phase 2)")
st.markdown("集成物理仿真引擎：模拟真实传感器的**随机游走**与**噪声特性**。")

# 1. 侧边栏控制
st.sidebar.header("控制台")
update_btn = st.sidebar.button("采集一次数据 (模拟 MQTT 接收)")
auto_run = st.sidebar.checkbox("自动连续采集 (Auto Mode)")

# 2. 核心逻辑：读取传感器
# 只要点击了按钮，或者勾选了自动运行，就会执行下面的代码
if update_btn or auto_run:
    # 从“记忆”中取出传感器
    ph_sensor = st.session_state['sensors']['ph_sensor']
    nh3_sensor = st.session_state['sensors']['nh3_sensor']

    # 获取新的读数 (这一步就在运行你写的 read_value 算法)
    new_ph = ph_sensor.read_value()
    new_nh3 = nh3_sensor.read_value()
    current_time = time.strftime("%H:%M:%S")

    # 把新数据存入历史记录
    new_row = pd.DataFrame({
        'Time': [current_time],
        'pH': [new_ph],
        'Ammonia': [new_nh3]
    })

    # 拼接数据 (concat)
    st.session_state['history_data'] = pd.concat(
        [st.session_state['history_data'], new_row],
        ignore_index=True
    ).tail(30)  # 只保留最近30条数据，防止内存爆炸

    # 如果是自动模式，稍微休息一下，模拟采样间隔
    if auto_run:
        time.sleep(0.5)
        st.rerun()  # 关键：让页面重新刷新，显示新数据

# ==========================================
# 第四部分：数据可视化 (Dashboard)
# ==========================================

# 准备数据
df = st.session_state['history_data']

# 只要有数据，就开始画图
if not df.empty:
    # 顶栏指标卡 (KPI)
    kpi1, kpi2, kpi3 = st.columns(3)
    last_ph = df['pH'].iloc[-1]
    last_nh3 = df['Ammonia'].iloc[-1]

    kpi1.metric("实时 pH", last_ph, delta=round(last_ph - 7.0, 2))
    kpi2.metric("实时 氨氮 (mg/L)", last_nh3, delta=round(last_nh3 - 0.5, 2), delta_color="inverse")

    # 简单的异常判定逻辑 (Boolean Logic)
    status = "正常"
    if last_ph < 6 or last_ph > 9 or last_nh3 > 1.0:
        status = "⚠️ 异常报警"
    kpi3.metric("系统状态", status)

    # 绘制折线图
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("pH 变化趋势 (含物理惯性)")
        st.line_chart(df.set_index('Time')['pH'], color="#0000FF")  # 蓝色

    with col2:
        st.subheader("氨氮 变化趋势")
        st.line_chart(df.set_index('Time')['Ammonia'], color="#FF0000")  # 红色

else:
    st.info("👈 请点击侧边栏的按钮开始采集数据")