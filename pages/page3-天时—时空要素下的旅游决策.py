import os
import pandas as pd
import streamlit as st
import requests
from pyproj import Transformer
from math import sqrt
import math
# 构造数据文件的绝对路径
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
pardirname = os.path.dirname(dirname)

st.title('天时—时空要素下的旅游决策')
st.caption("""
### 使用说明
1. 该模块由用户输入出游月份以及精确时间和所在地，
系统根据气候舒适度以及距离远近分别做出推荐旅游城市供用户选择。
2. 注意：选择月份时如果任意选择月份则是服务于长期出行计划。
（系统调用监测站近十年的月份平均数据计算气候舒适度指数并做出前十的城市推荐，但由于长期出游，故下方两个选项可忽略）
3. 注意：如果是短期内（7天）出游，则选择当前月份和计划几天后出行，
系统将使用历史舒适度排名前十的城市调用天气查询API获取天气预报计算预测气候舒适度指数并排序。距离计算也使用这些城市。
""", unsafe_allow_html=True)

# 华氏度转为摄氏度
def huashidu_to_celsius(huashidu):
    return (huashidu - 32) * 5.0 / 9.0
# 计算THI指数
def calculate_THI(temp, dew_point):
    e_temp = 6.11 * 10 ** ((7.5 * temp) / (237.3 + temp))
    e_dew = 6.11 * 10 ** ((7.5 * dew_point) / (237.3 + dew_point))
    RH = 100 * (e_dew / e_temp)
    THI = (1.8 * temp + 32) - 0.55 * (1 - RH / 100) * (1.8 * temp - 26)
    return THI

folder_path = f"{pardirname}\\data\\输出数据\\全国站点分指标平均数据\\"
temp_file = folder_path + 'TEMP.xlsx'
dewp_file = folder_path + 'DEWP.xlsx'

temp_df = pd.read_excel(temp_file, sheet_name='Monthly_Averages')
dewp_df = pd.read_excel(dewp_file, sheet_name='Monthly_Averages')
st.divider()
with st.form("my form"):
    st.write('注：请填写出游相关信息(如果长期计划请忽略后两个选项）')
    month = st.slider("（一）选择计划出游月份", 1, 12, 1)
    month_column = str(month)
    days_later = st.number_input("（二）计划几天后出游", min_value=1, max_value=7, value=1)
    address = st.text_input("（三）请输入您所在位置：")
    submitted = st.form_submit_button('提交')
if submitted:
    temp_df_selected = temp_df[['站点名称', month, '纬度', '经度', 'province', 'city']].copy()
    dewp_df_selected = dewp_df[['站点名称', month]].copy()
    temp_df_selected[month] = temp_df_selected[month].apply(huashidu_to_celsius)
    dewp_df_selected[month] = dewp_df_selected[month].apply(huashidu_to_celsius)
    temp_df_selected.rename(columns={month: f'{month}_temp'}, inplace=True)
    dewp_df_selected.rename(columns={month: f'{month}_dewp'}, inplace=True)
    merged_df = pd.merge(temp_df_selected, dewp_df_selected, on='站点名称')
    merged_df['THI'] = merged_df.apply(lambda row: calculate_THI(row[f'{month}_temp'], row[f'{month}_dewp']), axis=1)
    
# THI分级
    def assign_THI_level(THI):
        if 60 <= THI <= 65:
            return 9
        elif 55 <= THI < 60 or 65 < THI <= 70:
            return 7
        elif 45 <= THI < 55 or 70 < THI <= 75:
            return 5
        elif 40 <= THI < 45 or 75 < THI <= 80:
            return 3
        else:
            return 1

    merged_df['THI_Level'] = merged_df['THI'].apply(assign_THI_level)
    top_10 = merged_df[merged_df['THI_Level'] == 9].head(10)
    # Print result to Streamlit
    #st.write("THI值为9的前十个站点信息:")
    #st.dataframe(top_10[['站点名称', 'THI', '纬度', '经度', 'province', 'city']])
    
# 和风天气API
# 调用QWeather API并获取城市ID
    def get_city_id(city_name, api_key):
        url = f"https://geoapi.qweather.com/v2/city/lookup?location={city_name}&key={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200' and 'location' in data:
                    location_info = data['location'][0]
                    city_id = location_info['id']
                    return city_id
                else:
                    print("失败")
            else:
                print("失败")
        except:
            print("失败")
    
        return None

    merged_df['THI_Level'] = merged_df['THI'].apply(assign_THI_level)
    top_10 = merged_df[merged_df['THI_Level'] == 9].head(10)
    top_10['City_ID'] = ''
    
    # 循环处理每行数据，调用API获取城市ID并存储
    for index, row in top_10.iterrows():
        city_name = row['city']
        city_id = get_city_id(city_name, '34802390cfa647d08c5e66b01ff5081c')  
        if city_id:
            top_10.at[index, 'City_ID'] = city_id
    st.divider()
    st.write(f"如果您选择在{month_column}月出游，全国范围内最舒适的城市（THI值为9的前十个监测站所在城市）:")
    st.dataframe(top_10[['province', 'city', 'THI', '纬度', '经度', 'City_ID']])
    
# 和风天气预报API
    def get_weather_forecast(city_id, api_key):
        url = f"https://devapi.qweather.com/v7/weather/7d?location={city_id}&key={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '200' and 'daily' in data:
                    return data['daily']
                else:
                    print("失败")
            else:
                print("失败")
        except:
            print("失败")
        return None
    
    def calculate_THI(temp, humidity):
        temp = float(temp)
        humidity = float(humidity)
        return (1.8 * temp + 32) - 0.55 * (1 - humidity / 100) * (1.8 * temp - 26)
# THI详细分级
    def assign_THI_info(THI):
        if THI < 40:
            return 1, '极冷， 极不舒适', '羽绒或毛皮衣'
        elif 40 <= THI < 45:
            return 3, '寒冷， 不舒适', '便服加坚实外套'
        elif 45 <= THI < 55:
            return 5, '偏冷， 较不舒适', '冬季常用服装'
        elif 55 <= THI < 60:
            return 7, '清凉， 舒适', '春秋季常用便服'
        elif 60 <= THI < 65:
            return 9, '凉， 非常舒适', '衬衫和常用便服'
        elif 65 <= THI < 70:
            return 7, '暖， 舒适', '轻便的夏装'
        elif 70 <= THI < 75:
            return 5, '偏热， 较舒适', '短袖开领衫'
        elif 75 <= THI < 80:
            return 3, '闷热， 不舒适', '热带单衣'
        else:
                return 1, '极闷热， 极不舒适', '超短裙'
    travel_day_index = days_later - 1
    api_key = '34802390cfa647d08c5e66b01ff5081c'
    top_10['Weather_Forecast'] = top_10['City_ID'].apply(lambda x: get_weather_forecast(x, api_key))
    top_10['tempMax'] = top_10['Weather_Forecast'].apply(lambda x: x[travel_day_index]['tempMax'] if x else None)
    top_10['humidity'] = top_10['Weather_Forecast'].apply(lambda x: x[travel_day_index]['humidity'] if x else None)
    top_10['THI'] = top_10.apply(lambda row: calculate_THI(row['tempMax'], row['humidity']) if pd.notnull(row['tempMax']) and pd.notnull(row['humidity']) else None, axis=1)
    top_10[['THI_Level', '人体感受', '适宜着衣']] = top_10['THI'].apply(lambda x: pd.Series(assign_THI_info(x)) if pd.notnull(x) else pd.Series([None, None, None]))
    sorted_stations = top_10.sort_values(by='THI_Level', ascending=False)
    st.divider()
    st.subheader('舒适优先')
    st.write("上述舒适城市在选择出行的当天最高气温、相对湿度、THI值及相关信息如下:")
    st.dataframe(sorted_stations[['city', 'tempMax', 'humidity', 'THI', 'THI_Level', '人体感受', '适宜着衣']])

# 地理编码
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626
    a = 6378245.0
    ee = 0.00669342162296594323
    
    class GaodeGeo:
        def __init__(self):
            self.key = '288e7e8b6a912b2be87ed0110b899e76'
        def requestApi(self, url):
            re = requests.get(url).json()
            return re
        def getGeoCode(self, address):
            url = f'https://restapi.amap.com/v3/geocode/geo?parameters&key={self.key}&address={address}'
            json_data = self.requestApi(url)
            if json_data['status'] == '1':
                location = json_data['geocodes'][0]['location']
                return location
            else:
                return '获取失败'
        def correctCoordinates(self, location):
            url = f'https://restapi.amap.com/v3/assistant/coordinate/convert?locations={location}&coordsys=gps&key={self.key}'
            json_data = self.requestApi(url)
            if json_data['status'] == '1':
                corrected_location = json_data['locations']
                return corrected_location
            else:
                return '纠偏失败'
# 坐标纠偏公式（坐标转换）
    def gcj02towgs84(lng, lat):
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]
    
    def transformlat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
            0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret
    
    def transformlng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
            0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * pi) + 40.0 *
                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return ret
    
# 距离计算(先投影)     
    def projected_distance(coord1, coord2):
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        transformer = Transformer.from_crs(4326, 3857, always_xy=True)
        x1, y1 = transformer.transform(lon1, lat1)
        x2, y2 = transformer.transform(lon2, lat2)
        distance_meters = sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distance_kilometers = distance_meters / 1000
        return distance_kilometers
    st.divider()
    st.subheader("就近原则")
    geo = GaodeGeo()
    if address:
        location = geo.getGeoCode(address)
        if location == '获取失败':
            st.write("获取地理编码失败")
        else:
            lon, lat = map(float, location.split(','))
            local_corrected = gcj02towgs84(lon, lat)
            # 使用高德API进行纠偏
            api_corrected_location = geo.correctCoordinates(location)
            if api_corrected_location != '纠偏失败':
                api_corrected_lon, api_corrected_lat = map(float, api_corrected_location.split(','))
            # 显示纠偏后的用户位置
            st.write(f"您所在地的坐标: ({lon}, {lat})")
            st.write(f"本地计算纠偏后坐标: ({local_corrected[0]}, {local_corrected[1]})")
            if api_corrected_location != '纠偏失败':
                st.write(f"高德API纠偏后坐标: ({api_corrected_lon}, {api_corrected_lat})")
            #st.dataframe(top_10[['province', 'city', 'THI', '纬度', '经度', 'City_ID']])
            # 计算与用户位置的距离（本地纠偏后的坐标）
            user_location_local = (local_corrected[1], local_corrected[0]) 
            distances_local = []
            for i, row in top_10.iterrows():
                city_location = (row['纬度'], row['经度'])
                distance = projected_distance(user_location_local, city_location)
                distances_local.append((row['province'], row['city'], distance, row['人体感受'], row['适宜着衣']))
            # 排序并输出结果
            distances_local.sort(key=lambda x: x[2]) 
            distances_local_df = pd.DataFrame(distances_local, columns=['province', 'City', 'Distance', '人体感受', '适宜着衣'])
            st.write("将上述舒适城市从近到远排列：")
            st.dataframe(distances_local_df)
            # 输出前三行的信息
            top_three = distances_local_df.head(3)
            
            st.write("距离最近的前三个城市信息：")
            for index, row in top_three.iterrows():
                st.write(f"{index + 1}. {row['province']}{row['City']}, 距离: {row['Distance']:.2f} 公里, 人体感受: {row['人体感受']}, 适宜着衣: {row['适宜着衣']}")
                        







