import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px  # 👈 引入 Plotly 绘图库
from shapely.geometry import Point, shape
import json
import time

import streamlit as st
# ... 其他 import ...

# 1. 设置浏览器标签页图标 (电脑上看)
st.set_page_config(
    page_title="ZJU Water Monitor",
    layout="wide",
    page_icon="🌊" # 这里也可以填图片文件名，比如 "app_icon.png"
)

# ==========================================
# 🍎 核心魔法：设置 iPhone 主屏幕图标 (Web Clip Icon)
# ==========================================
def set_apple_icon(image_url):
    """
    向网页头部注入 HTML 代码，告诉 iOS 添加到主屏幕时使用哪张图。
    """
    apple_icon_code = f"""
    <head>
        <link rel="apple-touch-icon" sizes="180x180" href="{image_url}">
        <link rel="icon" type="image/png" sizes="32x32" href="{image_url}">
    </head>
    """
    st.markdown(apple_icon_code, unsafe_allow_html=True)

# ⚠️ 把下面这个链接换成你刚才在 GitHub 复制的 "Raw" 链接！
ICON_URL = "https://github.com/huangmi0711-creator/zju-water-monitor/blob/e8cdaa0b4702f4abda567d588365cfc44b040f06/app_icon.png.jpg"

# 执行注入
set_apple_icon(ICON_URL)

# ... 下面接你原来的代码 ...

st.set_page_config(page_title="ZJU Water Monitor Pro", layout="wide")


# ==========================================
# 1. 地图加载 (保持不变)
# ==========================================
@st.cache_data
def load_lake_boundary():
    try:
        with open('qizhen_lake.geojson', 'r', encoding='utf-8') as f:
            data = json.load(f)
        max_area = 0
        lake_polygon = None
        for feature in data['features']:
            geom = shape(feature['geometry'])
            if geom.area > max_area:
                max_area = geom.area
                lake_polygon = geom
        return lake_polygon
    except:
        st.error("❌ 找不到 qizhen_lake.geojson")
        st.stop()


LAKE_POLYGON = load_lake_boundary()

if LAKE_POLYGON.geom_type == 'Polygon':
    x, y = LAKE_POLYGON.exterior.coords.xy
    LAKE_COORDS_FOR_MAP = [[lon, lat] for lon, lat in zip(x, y)]
else:
    x, y = max(LAKE_POLYGON.geoms, key=lambda a: a.area).exterior.coords.xy
    LAKE_COORDS_FOR_MAP = [[lon, lat] for lon, lat in zip(x, y)]


# ==========================================
# 2. 机器人逻辑 (保持不变)
# ==========================================
class CampusBot:
    def __init__(self):
        safe_pt = LAKE_POLYGON.representative_point()
        self.lat = safe_pt.y
        self.lon = safe_pt.x
        self.ph = 7.1
        self.do = 6.5

    def move(self):
        for _ in range(15):
            d_lat = np.random.normal(0, 0.0003)
            d_lon = np.random.normal(0, 0.0003)
            temp_lat = self.lat + d_lat
            temp_lon = self.lon + d_lon

            if LAKE_POLYGON.contains(Point(temp_lon, temp_lat)):
                self.lat = temp_lat
                self.lon = temp_lon
                self.ph += np.random.normal(0, 0.1)
                self.ph = np.clip(self.ph, 5.0, 9.0)
                self.do += np.random.normal(0, 0.2)
                self.do = np.clip(self.do, 0.5, 12.0)
                break

        return {
            'Time': time.strftime("%H:%M:%S"),
            'Lat': self.lat,
            'Lon': self.lon,
            'pH': round(self.ph, 2),
            'DO': round(self.do, 2)
        }


def generate_report(df):
    if df.empty: return "暂无数据"
    avg_do = df['DO'].mean()
    status = "🟢 水质优良" if avg_do >= 5.0 else "🟡 轻度缺氧" if avg_do >= 3.0 else "🔴 严重缺氧"
    return f"**状态**: {status}\n\n平均DO: `{avg_do:.2f}` | 平均pH: `{df['pH'].mean():.2f}`"


# ==========================================
# 3. 页面布局
# ==========================================
if 'bot' not in st.session_state:
    st.session_state.bot = CampusBot()
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Lat', 'Lon', 'pH', 'DO'])

st.title("🎓 浙大紫金港·智慧水务控制台")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("🕹️ 控制面板")
    if st.button("🚀 启动巡航 (10点)", type="primary"):
        progress = st.progress(0)
        temp_data = []
        for i in range(10):
            pt = st.session_state.bot.move()
            temp_data.append(pt)
            progress.progress((i + 1) / 10)
            time.sleep(0.05)
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame(temp_data)], ignore_index=True)
        st.success("已更新")

    if st.button("🗑️ 清空数据"):
        st.session_state.history = pd.DataFrame(columns=['Time', 'Lat', 'Lon', 'pH', 'DO'])
        st.rerun()

    st.divider()
    st.info(generate_report(st.session_state.history))

with col_right:
    df = st.session_state.history
    st.subheader("📍 实时轨迹追踪")

    # 地图部分
    layers = [
        pdk.Layer("PolygonLayer", data=[{"path": LAKE_COORDS_FOR_MAP}], get_polygon="path",
                  get_fill_color=[0, 100, 255, 40], get_line_color=[0, 100, 255, 150], line_width_min_pixels=1,
                  pickable=False)
    ]
    if not df.empty:
        layers.append(pdk.Layer("ScatterplotLayer", data=df, get_position='[Lon, Lat]', get_color='[255, 69, 0, 200]',
                                get_radius=5, radius_min_pixels=3, pickable=True))

    st.pydeck_chart(pdk.Deck(
        map_style='light',
        initial_view_state=pdk.ViewState(latitude=LAKE_POLYGON.centroid.y, longitude=LAKE_POLYGON.centroid.x, zoom=16),
        layers=layers,
        tooltip={"text": "DO: {DO}"}
    ))

    # --- 🔥 重点修改：使用 Plotly 绘制高颜值图表 ---
    if not df.empty:
        st.divider()
        chart_c1, chart_c2 = st.columns(2)

        with chart_c1:
            # 绘制 pH 面积图
            fig_ph = px.area(df, x='Time', y='pH', title="pH 趋势", markers=True)
            fig_ph.update_traces(line_color='#3498db', fillcolor='rgba(52, 152, 219, 0.2)')  # 蓝色
            fig_ph.update_layout(
                xaxis=dict(showgrid=False, nticks=5),  # 👈 关键：强制只显示5个刻度
                yaxis=dict(showgrid=True, gridcolor='#eee'),
                height=250,
                margin=dict(l=20, r=20, t=30, b=20),  # 去掉多余边距
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_ph, use_container_width=True)

        with chart_c2:
            # 绘制 DO 面积图
            fig_do = px.area(df, x='Time', y='DO', title="溶解氧 (DO) 趋势", markers=True)
            fig_do.update_traces(line_color='#2ecc71', fillcolor='rgba(46, 204, 113, 0.2)')  # 绿色
            fig_do.update_layout(
                xaxis=dict(showgrid=False, nticks=5),  # 👈 关键：强制只显示5个刻度
                yaxis=dict(showgrid=True, gridcolor='#eee'),
                height=250,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_do, use_container_width=True)

if not df.empty:
    with st.expander("查看原始数据"):
        st.dataframe(df.sort_values("Time", ascending=False), use_container_width=True)