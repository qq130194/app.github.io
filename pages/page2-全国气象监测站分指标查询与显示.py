import matplotlib.pyplot as plt
import pandas as pd 
import streamlit as st
import os
import folium
import geopandas as gpd
from streamlit_folium import st_folium
from folium import FeatureGroup, Marker, LayerControl
import matplotlib.pyplot as plt
from folium.plugins import HeatMap, MousePosition
from folium.map import FeatureGroup, Marker, LayerControl
import geopandas as gpd
from pyproj import Transformer
from math import sqrt
from shapely.geometry import Point

# 构造数据文件的绝对路径
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
pardirname = os.path.dirname(dirname)

st.title('全国气象监测站分指标查询与显示')
st.caption("""
### 使用说明
1. 该模块提供全国气象监测站的位置查询功能以及部分气象指标的月均值年均值以及最值查询，用户可以选择一个需要查询的气象指标，选择一种查询方式，并且选择对应时间。后面的输出均按照
用户选择的结果呈现。
2. 地图显示：该指标在全国范围监测站的均值和最大值最小值以及出现的点位以及热力图显示。
3. 还包括下拉多选框可选择多个站点绘制折线图。条件判别式查询等功能
""", unsafe_allow_html=True)
st.divider()# 分割线
st.subheader('全国气象监测站信息查询与显示')
st.markdown("""注：该模块提供全国400个气象监测站的信息。可交互式查询。""", unsafe_allow_html=True)
# 创建地图控件，不加载底图
m = folium.Map(tiles=None)
# 缓存加载数据
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path,encoding = 'ANSI')
file_path = f"{pardirname}\\data\\输出数据\\站点数据_new.csv" 
df = load_data(file_path)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['经度'], df['纬度']))
# 监测站POI点图层
poi = FeatureGroup(name="监测站")
for _, row in gdf.iterrows():
    # 生成Popup内容
    html = f"""
    <div style="font-size: 8pt">
    <h4>{row['监测站']}</h4>
    <p>省份: {row['province']}</p>
    <p>城市: {row['city']}</p>
    <p>区县: {row['area']}</p>
    <p>地址: {row['address']}</p>
    """
    popup = folium.Popup(html, max_width=200)
    tooltip = row['监测站']
    icon = folium.Icon(icon="cloud", color="blue")  # 修改地图符号为蓝色云朵
    Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=popup,
        tooltip=tooltip,
        icon=icon
    ).add_to(poi)
# 所有的Marker对象都添加到POI点图层
poi.add_to(m)
# 创建3个地图切片
folium.TileLayer(tiles="CartoDB.Positron", name="carto地图").add_to(m)
folium.TileLayer(tiles="http://webrd02.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}", name="高德地图", attr="高德地图").add_to(m)
folium.TileLayer(tiles="Esri.WorldImagery", name="Esri全球影像").add_to(m)
# 获取数据边界
minx = min(gdf.geometry.x)
maxx = max(gdf.geometry.x)
miny = min(gdf.geometry.y)
maxy = max(gdf.geometry.y)
# 添加图层控制
LayerControl().add_to(m)
# 添加显示坐标控件
MousePosition().add_to(m)
m.fit_bounds([(miny, minx), (maxy, maxx)])
st_folium(m, width=700, height=500)

st.divider()
st.subheader("气象数据查询模块")
st.caption('注：请根据提示选择以下信息。（本界面的输出受到该参数控制）')
names = ['TEMP(平均温度)', 'DEWP(平均露点)', 'VISIB(平均能见度)', 'WDSP(平均风速)', 'PRCP(降水量)']
names_dict = {name.split('(')[0]: name for name in names}
months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
years = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
zhibiao = st.selectbox('1 请选择一个需要查询的气象指标', names)
way = st.radio('2 请选择一个查询方式', ['按年份', '按月份'])
if way == '按年份':
    selectime = st.select_slider('请选择一个需要查询的年份', options=years)
else:
    selectime = st.select_slider('请选择一个需要查询的月份', options=months)
# 计算距离
def projected_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    transformer = Transformer.from_crs(4326, 3857, always_xy=True)
    x1, y1 = transformer.transform(lon1, lat1)
    x2, y2 = transformer.transform(lon2, lat2)
    distance_meters = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    distance_kilometers = distance_meters / 1000
    return distance_kilometers

# 加载数据部分
def load_data(zhibiao, way):
    file_name =  f"{pardirname}\\data\\输出数据\\全国站点分指标平均数据\\{zhibiao.split('(')[0]}.xlsx"
    if way == '按年份':
        df = pd.read_excel(file_name, sheet_name=0)  # 第一个表格按年份
    else:
        df = pd.read_excel(file_name, sheet_name=1)  # 第二个表格按月份
    return df

# 生成热力图的函数
def create_heatmap(df, value, center=[35, 110], zoom_start=5):
    m = folium.Map(location=center, zoom_start=zoom_start)
    data = df[['纬度', '经度', int(value)]].values.tolist()
    HeatMap(data).add_to(m)
    return m

# 查询数据
df = load_data(zhibiao, way)
selected_column = df[int(selectime)]
mean_value = selected_column.mean()
max_value = selected_column.max()
min_value = selected_column.min()
max_row = df[df[int(selectime)] == max_value]
min_row = df[df[int(selectime)] == min_value]
st.divider()
# 显示全国均值、最高值、最低值
st.markdown(f"### 全国{zhibiao}的查询结果")
st.markdown(f"**全国均值**: {mean_value:.2f}")
st.markdown(f"**最高值**: {max_value:.2f}，出现在位于{max_row.iloc[0]['province']}{max_row.iloc[0]['city']}{max_row.iloc[0]['area']}的监测站：{max_row.iloc[0]['站点名称']}")
st.markdown(f"**最低值**: {min_value:.2f}，出现在位于{min_row.iloc[0]['province']}{min_row.iloc[0]['city']}{min_row.iloc[0]['area']}的监测站：{min_row.iloc[0]['站点名称']}")

# 创建地图控件，不加载底图
m = folium.Map(tiles=None)
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df['经度'], df['纬度']))
# POI点图层
poi = FeatureGroup(name="POI")
for _, row in gdf.iterrows():
    # 生成Popup内容
    html = f"""
    <div style="font-size: 8pt">
    <h4>{row['站点名称']}</h4>
    <p>{names_dict[zhibiao.split('(')[0]]}</p>
    <p>均值: {row[int(selectime)]:.2f}</p>
    </div>
    """
    popup = folium.Popup(html, max_width=200)
    tooltip = row['站点名称']
    if row[int(selectime)] == max_value:
        icon = folium.Icon(icon="cloud", color="red", icon_size=(25, 41))  
    elif row[int(selectime)] == min_value:
        icon = folium.Icon(icon="cloud", color="green", icon_size=(25, 41))  
    else:
        icon = folium.Icon(icon="cloud", color="blue") 
    Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=popup,
        tooltip=tooltip,
        icon=icon).add_to(poi)

poi.add_to(m)
# 仅保留高德地图，提高运行速度
folium.TileLayer(tiles="Esri.WorldImagery", name="Esri全球影像").add_to(m)
minx = min(gdf.geometry.x)
maxx = max(gdf.geometry.x)
miny = min(gdf.geometry.y)
maxy = max(gdf.geometry.y)
# 添加显示坐标控件
MousePosition().add_to(m)
m.fit_bounds([(miny, minx), (maxy, maxx)])
st_folium(m, width=700, height=500)
# 生成热力图
st.divider()
st.subheader('热力图显示')
map_obj = create_heatmap(df, selectime)
st_folium(map_obj, width=725)

# 添加下拉多选框以选择站点绘制折线图
st.divider()
df.columns = df.columns.map(str)
st.subheader('折线图显示')
stations = st.multiselect(' 请选择需要显示的站点', df['站点名称'].unique())
if stations:
    filtered_df = df[df['站点名称'].isin(stations)]
    filtered_df.columns = filtered_df.columns.map(str)
    for station in stations:
        station_info = filtered_df[filtered_df['站点名称'] == station].iloc[0]
        province = station_info['province']
        city = station_info['city']
        st.markdown(f"**您选择的是位于** [{province}](province) **{city}** 的 **{station}** 监测站。")
    fig, ax = plt.subplots(figsize=(10, 6))
    if way == '按年份':
        time_period = years
    else:
        time_period = months
    for station in stations:
        station_data = filtered_df[filtered_df['站点名称'] == station]
        ax.plot(time_period, station_data[time_period].values.flatten(), marker='o', label=station)
    ax.set_xlabel('时间')
    ax.set_ylabel(names_dict[zhibiao.split('(')[0]])
   # ax.set_title(f'{names_dict[zhibiao.split('(')[0]]} - 各站点折线图')
    ax.legend()
    st.pyplot(fig)
else:
    st.warning('请选择至少一个站点')

# 条件判别式筛选
st.divider()
st.subheader('条件判别式查询与显示')
condition = st.selectbox(' 请选择条件判别式', ['大于', '小于', '大于等于', '小于等于'])
threshold = st.text_input(' 请输入条件判别式的阈值')
if threshold:
    try:
        threshold = float(threshold)
        if way == '按年份':
            time_period = years
        else:
            time_period = months
        if condition == '大于':
            filtered_df = df[df[time_period].apply(lambda row: (row > threshold).any(), axis=1)]
        elif condition == '小于':
            filtered_df = df[df[time_period].apply(lambda row: (row < threshold).any(), axis=1)]
        elif condition == '大于等于':
            filtered_df = df[df[time_period].apply(lambda row: (row >= threshold).any(), axis=1)]
        elif condition == '小于等于':
            filtered_df = df[df[time_period].apply(lambda row: (row <= threshold).any(), axis=1)]
        # 显示符合条件的监测点信息
        st.markdown(f"共有 **{len(filtered_df)}** 个监测点符合筛选要求。")
        st.dataframe(filtered_df)
        # 地图显示
        map_df = filtered_df.copy()
        map_df.rename(columns={'纬度': 'latitude', '经度': 'longitude'}, inplace=True)
        # 在地图上显示符合条件的监测点位置
        st.subheader('符合条件的监测点位置')
        st.map(map_df[['latitude', 'longitude']])
        
    except ValueError:
        st.error('请输入一个有效的数字作为阈值。')
else:
    st.warning('请输入一个阈值进行筛选。')
# =============================================================================
# # 逐日热力图folium（不知道为什么在streamlit里加载不了，Notebook可以）
# def generate_heatmap(indicator, year, month, folder_path):
#     filepath = os.path.join(folder_path, f'{indicator}_{year}.xlsx')
#     df = pd.read_excel(filepath)
#     df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S')
#     df_filtered = df[(df['DATE'].dt.year == year) & (df['DATE'].dt.month == month)]
#     st.write("Filtered Data:", df_filtered.head())
#     # 按日期分组，生成热力图数据
#     heatmap_data = []
#     time_index = []
#     for date, group in df_filtered.groupby(df_filtered['DATE'].dt.date):
#         data = group[['LATITUDE', 'LONGITUDE', indicator]].values.tolist()
#         # 增加权重值
#         for entry in data:
#             entry[2] = abs(entry[2])  
#         #st.write(f"Date: {date}, Data: {data}")
#         heatmap_data.append(data)
#         time_index.append(date.strftime("%Y-%m-%d"))
#     # 创建热力图
#     m = folium.Map([35.0, 103.0], zoom_start=5)
#     if heatmap_data:
#         hm = folium.plugins.HeatMapWithTime(heatmap_data, index=time_index, auto_play=True, max_opacity=0.3)
#         hm.add_to(m)
#     else:
#         folium.Marker([35.0, 103.0], popup='No data available for the selected period').add_to(m)
#     return m
# st.title('Heatmap')
# indicator = st.selectbox('Select Indicator', ['TEMP', 'DEWP', 'VISIB', 'WDSP', 'PRCP'])
# year = st.selectbox('Select Year', list(range(2014, 2024)))
# month = st.selectbox('Select Month', list(range(1, 13)))
# 
# folder_path =  f"{pardirname}\\data\\输出数据\\全国站点按年份分指标逐日数据"
# heatmap = generate_heatmap(indicator, year, month, folder_path)
# st_data = st_folium(heatmap, width=725)
# =============================================================================
# =============================================================================
# #逐日热力图pydeck（也不太行
# import os
# import pandas as pd
# import streamlit as st
# import pydeck as pdk
# from sklearn.preprocessing import MinMaxScaler
# def load_data(indicator, year, month, folder_path):
#     filepath = os.path.join(folder_path, f'{indicator}_{year}.xlsx')
#     df = pd.read_excel(filepath)
#     df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S')
#     df_filtered = df[(df['DATE'].dt.year == year) & (df['DATE'].dt.month == month)]
#     return df_filtered
# 
# def normalize_data(df, column):
#     scaler = MinMaxScaler()
#     df[column] = scaler.fit_transform(df[[column]])
#     return df
# 
# def create_heatmap(df, indicator):
#     df['date_str'] = df['DATE'].dt.strftime('%Y-%m-%d')
#     df = normalize_data(df, indicator)
#     df['WEIGHT'] = df[indicator]
#     unique_dates = df['date_str'].unique()
#     frames = []
#     for date in unique_dates:
#         filtered_df = df[df['date_str'] == date]
#         frame = {
#             'date': date,
#             'data': filtered_df[['LONGITUDE', 'LATITUDE', 'WEIGHT']].values.tolist()
#         }
#         frames.append(frame)
#     
#     initial_view_state = pdk.ViewState(
#         latitude=35.0,
#         longitude=103.0,
#         zoom=5,
#         pitch=0,)
# 
#     heatmap_layers = [
#         pdk.Layer(
#             "HeatmapLayer",
#             data=frame['data'],
#             get_position="[0, 1]",
#             get_weight="[2]",
#             radius_pixels=50,
#         ) for frame in frames]
# 
#     r = pdk.Deck(
#         layers=heatmap_layers,
#         initial_view_state=initial_view_state,
#         tooltip={"text": "Date: {date}\nValue: {2}"})
#     
#     return r
# st.title('Heatmap')
# indicator = st.selectbox('Select Indicator', ['TEMP', 'DEWP', 'VISIB', 'WDSP', 'PRCP'])
# year = st.selectbox('Select Year', list(range(2014, 2024)))
# month = st.selectbox('Select Month', list(range(1, 13)))
# 
# folder_path =  f"{pardirname}\\data\\输出数据\\全国站点按年份分指标逐日数据"
# df_filtered = load_data(indicator, year, month, folder_path)
# heatmap = create_heatmap(df_filtered, indicator)
# heatmap
# st.pydeck_chart(heatmap)
# 
# =============================================================================
# =============================================================================
# 
# 插值
# df = df.rename(columns={'纬度': 'latitude', '经度': 'longitude', int(selectime): 'value'})
# def reproject_shapefile(shapefile_path):
#     gdf = gpd.read_file(shapefile_path)
#     gdf = gdf.to_crs(epsg=4326) 
#     return gdf
# china_shp =  f"{pardirname}\\data\\中国基础地理数据\\2. Province\\china_provinces.shp"
# gdf = reproject_shapefile(china_shp)
# methods = ['linear', 'nearest', 'cubic']
# def mask_grid_with_shapefile(grid_lat, grid_lon, grid_value, gdf):
#     points = [Point(x, y) for x, y in zip(grid_lon.flatten(), grid_lat.flatten())]
#     grid_gdf = gpd.GeoDataFrame(geometry=points, crs='EPSG:4326')
#     grid_gdf['value'] = grid_value.flatten()
#     clipped = gpd.clip(grid_gdf, gdf)
#     clipped_grid = np.full(grid_lat.shape, np.nan)
#     for idx, row in clipped.iterrows():
#         lon_idx = np.abs(grid_lon[0] - row.geometry.x).argmin()
#         lat_idx = np.abs(grid_lat[:, 0] - row.geometry.y).argmin()
#         clipped_grid[lat_idx, lon_idx] = row['value']
#     clipped_grid[np.isnan(clipped_grid) | np.isinf(clipped_grid)] = np.nan
#     return clipped_grid
# def plot_interpolation(grid_lat, grid_lon, grid_value, method, gdf):
#     plt.figure(figsize=(8, 6))
#     levels = np.linspace(np.nanmin(grid_value), np.nanmax(grid_value), 20)
#     plt.contourf(grid_lon, grid_lat, grid_value, cmap='viridis', levels=levels)
#     plt.colorbar()
#     plt.xlabel('经度')
#     plt.ylabel('纬度')
#     plt.title(f'{method} 插值结果')
#     gdf.boundary.plot(ax=plt.gca(), edgecolor="black")
#     st.pyplot(plt)
# 
# china_bounds = [73, 135, 18, 53]
# lat = np.linspace(china_bounds[2], china_bounds[3], 300)
# lon = np.linspace(china_bounds[0], china_bounds[1], 300)
# grid_lat, grid_lon = np.meshgrid(lat, lon)
# 
# for method in methods:
#     grid_value = griddata(df[['latitude', 'longitude']].values, df['value'].values, (grid_lat, grid_lon), method=method)
#     clipped_grid_value = mask_grid_with_shapefile(grid_lat, grid_lon, grid_value, gdf)
#     st.header(f"{method} 插值")
#     plot_interpolation(grid_lat, grid_lon, clipped_grid_value, method, gdf)
# =============================================================================
