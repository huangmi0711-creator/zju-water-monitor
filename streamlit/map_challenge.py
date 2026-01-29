import pydeck as pdk
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SNAPP 机器鱼追踪系统", layout="wide")

st.title("🗺️ 水下机器人实时位置追踪 (GIS)")
st.markdown("模拟 SNAPP 机器鱼在目标水域（学校人工湖/实验水槽）的巡航轨迹与采样点分布。")

# --- 🔴 关键修改区：把你学校的坐标填在这里 ---
# 举例：这里填的是北京某高校的坐标，请替换成你的！
MY_SCHOOL_LAT = 30.31  # 纬度 (Latitude)
MY_SCHOOL_LON = 120.09 # 经度 (Longitude)
# ----------------------------------------

# --- 1. 侧边栏控制 ---
st.sidebar.header("🕹️ 机器人控制台")
robot_count = st.sidebar.slider("投放机器人数量", 10, 100, 50)
hour_selected = st.sidebar.slider("查看时间段 (24h)", 0, 23, 10)

# --- 2. 模拟 GIS 数据 (生成以你学校为中心的随机点) ---
# 这一步是为了模拟机器鱼传回来的 GPS 信号
@st.cache_data
def generate_gps_data(lat, lon, n):
    data = pd.DataFrame({
        # 在你学校坐标的基础上，加一点点随机偏移，模拟移动
        'lat': np.random.randn(n) / 500 + lat,
        'lon': np.random.randn(n) / 500 + lon,
        'time': np.random.randint(0, 24, n) # 随机分配时间
    })
    return data

# 生成数据
gps_data = generate_gps_data(MY_SCHOOL_LAT, MY_SCHOOL_LON, 500)

# --- 3. 数据筛选 (根据侧边栏的时间) ---
filtered_data = gps_data[gps_data['time'] == hour_selected]

# --- 4. 核心功能：地图可视化 (st.map) ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"📍 {hour_selected}:00 - 机器鱼分布图")

    # --- Pydeck 高级地图配置 ---
    # 1. 定义初始视图 (地图中心和缩放级别)
    view_state = pdk.ViewState(
        latitude=MY_SCHOOL_LAT,
        longitude=MY_SCHOOL_LON,
        zoom=15,  # 默认缩放级别
        pitch=0,  # 俯视角度 (0是垂直俯视)
    )

    # 2. 定义图层 (ScatterplotLayer = 散点图)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_data.iloc[:robot_count],
        get_position='[lon, lat]',
        get_color='[255, 0, 0, 200]',  # [红, 绿, 蓝, 透明度] -> 红色
        get_radius=10,  # 基础半径
        # ⬇️ 关键设置：锁定屏幕像素大小 ⬇️
        pickable=True,  # 允许鼠标悬停
        radius_scale=1,
        radius_min_pixels=5,  # 最小显示 5 像素 (防止缩太小看不见)
        radius_max_pixels=10,  # 最大显示 10 像素 (防止放太大挡住地图)
    )

    # 3. 渲染地图
    st.write(f"当前筛选出的数据条数: {len(filtered_data)}")
    st.write(filtered_data.head())  # 打印前5行看看
    st.pydeck_chart(pdk.Deck(
        # 使用 'light' 或 'dark'，这是 Streamlit 内置的快捷方式，不需要 Token
        map_style='light',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "机器鱼 ID: {index}\n经度: {lon}\n纬度: {lat}"}
    ))


with col2:
    st.subheader("📊 状态统计")
    st.write(f"当前活跃机器人: **{len(filtered_data.iloc[:robot_count])}** 台")
    st.write(f"中心纬度: {MY_SCHOOL_LAT}")
    st.write(f"中心经度: {MY_SCHOOL_LON}")
    st.info("绿色点位代表机器鱼当前上报的 GPS 位置。")

# --- 5. 原始数据折叠栏 ---
with st.expander("查看原始 GPS 遥测数据"):
    st.dataframe(filtered_data)