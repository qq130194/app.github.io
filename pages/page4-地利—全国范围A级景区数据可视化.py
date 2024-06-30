import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from folium import Choropleth
from streamlit_folium import folium_static as st_folium
import matplotlib.pyplot as plt
import os
# 构造数据文件的绝对路径
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
pardirname = os.path.dirname(dirname)

file_path = f"{pardirname}\\data\\全国范围A级景点\\2024年A级景区数据.xlsx"  
data = pd.read_excel(file_path)
data = data.loc[:, ~data.columns.duplicated()]

st.title("地利—全国范围A级景区数据可视化")
st.markdown("注：该模块可视化了全国范围内不同等级景区数据，并统计了各省的不同等级的景区数量并且以地图可视化显示。")
st.divider()
st.caption("""
### 使用说明
1. 选择景区等级：从下拉框中选择你感兴趣的景区等级。
2. 查看地图：地图上会显示选定等级的景区位置和数量。
3. 查看统计：表格显示了各省不同等级景区的数量。
4. 选择颜色条：从下拉框中选择颜色条以更改地图上的颜色显示(推荐使用Reds)。
""")
st.divider()
st.header("A级景区数据预览")
st.dataframe(data.head())

# 统计各省级各等级景区的数量，只保留1A到5A的列
count_df = data.groupby(['NAME', '等级']).size().unstack(fill_value=0).reset_index()
count_df = count_df[['NAME', '1A', '2A', '3A', '4A', '5A']] 

# 重命名count_df的列名
count_df.columns = ['NAME', '1A', '2A', '3A', '4A', '5A']
st.divider()
st.header("各省各等级景区数量统计")
st.dataframe(count_df)
shp_file = f"{pardirname}\\data\\中国基础地理数据\\2. Province\\china_provinces.shp"  
gdf = gpd.read_file(shp_file)
gdf = gdf.rename(columns={'NAME': 'NAME'})
merged_gdf = gdf.merge(count_df, on='NAME', how='left')
st.divider()
level = st.selectbox("请选择需要查询的景区等级", ['1A', '2A', '3A', '4A', '5A'])
filtered_data = data[data['等级'] == level]
st.subheader(f"{level} 级景区位置")
map_data = filtered_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
st.map(map_data[['latitude', 'longitude']])
st.divider()
st.subheader(f"各省{level}级景区数量地图")
m = folium.Map(location=[35, 110], zoom_start=5)
folium.TileLayer('cartodbpositron').add_to(m)

# 颜色条选择
color_map = st.selectbox("选择颜色条", plt.colormaps(),index=plt.colormaps().index('Reds'))
# 创建 Choropleth 图层
Choropleth(
    geo_data=merged_gdf,
    data=merged_gdf,
    key_on='feature.properties.NAME',
    columns=['NAME', level],  # 使用选择的等级的景区数量
    fill_color=color_map,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=f'{level} 级景区数量').add_to(m)

st_folium(m, width=725)



