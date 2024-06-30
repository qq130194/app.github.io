import os
import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from folium import Choropleth
from streamlit_folium import folium_static as st_folium

# 构造数据文件的绝对路径
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
pardirname = os.path.dirname(dirname)
#data_file_path = f"{pardirname}/data/my_data.csv"

# 读取景点评论文化自然倾向指数数据
visit_file =  f"{pardirname}\\data\\输出数据\\分析结果.xlsx"
visit_data = pd.read_excel(visit_file)
visit_data = visit_data.loc[:, ~visit_data.columns.duplicated()]

# 读取景点情感倾向指数数据.
sentiment_file = f"{pardirname}\\data\\输出数据\\province_sentiment_analysis.xlsx"
sentiment_data = pd.read_excel(sentiment_file)
sentiment_data = sentiment_data.loc[:, ~sentiment_data.columns.duplicated()]

# 读取shapefile
shp_file = f"{pardirname}\\data\\中国基础地理数据\\2. Province\\china_provinces.shp"
gdf = gpd.read_file(shp_file)


st.title("人和—景点评论情感倾向可视化")
st.divider()
# 第一部分：景点评论文化和自然倾向的指数数据
st.header("PART1:景点评论文化和自然倾向可视化")
st.markdown("""
注：该部分展示了中国各省份的景点评论中游客所呈现的 <span style='color:blue'>自然倾向</span> 或 <span style='color:blue'>文化倾向</span> 数据，并可视化在地图上。
""", unsafe_allow_html=True)
st.caption("""
### 使用说明
1. 选择景点评论中 <span style='color:blue'>文化</span> 和 <span style='color:blue'>自然</span> 倾向的指标名：从下拉框中选择你感兴趣的指标。（推荐选择“归一化指标”）
2. 地图显示：地图上会显示选定数据列名的数据分布。
""", unsafe_allow_html=True)
st.divider()
st.subheader("（一）景点评论文化和自然倾向数据预览")
st.dataframe(visit_data.head())
visit_columns = visit_data.columns.tolist()
visit_columns.remove('简称')
st.divider()
st.subheader("（二）各省份景点评论中文化和自然倾向数据地图")  
visit_column = st.selectbox("请选择景点评论文化和自然倾向指标", visit_columns)
# 合并
merged_gdf_visit = gdf.merge(visit_data[['简称', visit_column]], on='简称', how='left')
# 地图
m_visit = folium.Map(location=[35, 110], zoom_start=5)
folium.TileLayer('cartodbpositron').add_to(m_visit)
# 创建 Choropleth 图层
Choropleth(
    geo_data=merged_gdf_visit,
    data=merged_gdf_visit,
    key_on='feature.properties.简称',
    columns=['简称', visit_column],
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f'{visit_column}').add_to(m_visit)

st_folium(m_visit, width=725)

st.divider()
# 第二部分：景点情感倾向的指数数据
st.header("PART2:景点情感倾向可视化")
st.markdown("""注：该部分展示了中国各省景点游客评论所展现出的 <span style='color:blue'>情感倾向</span> 的数据，并可视化在地图上。""", unsafe_allow_html=True)
st.caption("""### 使用说明
1. 选择景点情感倾向的可视化指标：从下拉框中选择你感兴趣的指标名。（推荐选择 <span style='color:blue'>"负面/正面情感指数"</span> ）
2. 地图显示：地图上会显示选定数据列名的数据分布。""", unsafe_allow_html=True)
st.divider()
# 数据预览
st.subheader("（一）景点情感倾向数据预览")
st.dataframe(sentiment_data.head())
sentiment_columns = sentiment_data.columns.tolist()
sentiment_columns.remove('简称')
st.divider()  
st.subheader("（二）各省份景点评论中情感倾向数据可视化地图")
sentiment_column = st.selectbox("请选择景点情感倾向可视化指标", sentiment_columns)
# 合并
merged_gdf_sentiment = gdf.merge(sentiment_data[['简称', sentiment_column]], on='简称', how='left')
# 地图
m_sentiment = folium.Map(location=[35, 110], zoom_start=5)
folium.TileLayer('cartodbpositron').add_to(m_sentiment)
# 创建 Choropleth 图层
Choropleth(
    geo_data=merged_gdf_sentiment,
    data=merged_gdf_sentiment,
    key_on='feature.properties.简称',
    columns=['简称', sentiment_column],
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f'{sentiment_column}').add_to(m_sentiment)
st_folium(m_sentiment, width=725)


