# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:54:57 2024

@author: 米斯德韩
"""
import pandas as pd 
import streamlit as st
st.markdown("""
# 天时、地利、人和
# ——出游决策的引领者 \U0001F5FB \U0001F30A
""", unsafe_allow_html=True)
st.divider()
st.markdown("""背景：随着社会进步和生活水平提高，越来越多的人通过旅行丰富精神生活，但传统跟团游的固定行程和自行规划游的繁琐步骤都存在不足。出行者在决策时主要关注时间、空间和人文三大要素：时间上考虑季节和气候对舒适度的影响；空间上考虑目的地距离，存在距离衰减效应；人文上考虑游客的情感倾向和偏好选择。该程序从这三个角度综合分析旅游决策问题，帮助游客优化行程安排，提高旅游体验。""")
st.divider()
data = {"指标": ["TEMP", "DEWP", "SLP", "STP", "VISIB", "WDSP", "MXSPD", "MAX", "MIN", "PRCP", "SNDP"],
    "描述": ["平均温度", "平均露点", "平均海平面压力", "平均感测站压力", "平均能见度", "平均风速", "最大持续风速", "最高温度", "最低温度", "降水量", "积雪深度"],
    "单位": ["华氏度", "华氏度", "毫巴/百帕", "毫巴/百帕", "英里", "节", "节", "华氏度", "华氏度", "英寸", "英寸"]}

df = pd.DataFrame(data)
st.markdown("""
气象数据来源于美国国家海洋和大气管理局（NOAA）下设的国家环境信息中心(NCEI)，包括了1929—2024年的气象数据。数据可在[NCEI官网](https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive/)获取。
""")
st.write("### 气象指标描述及单位")
st.dataframe(df)
st.divider()
st.markdown("""- 孙根年等学者对气候舒适度有着相当广泛的应用研究，他们提出了一种综合舒适指数为:""")
st.latex(r'C = 0.6X_{THI} + 0.3X_K + 0.1X_I')
st.markdown("""
其中：
- $C$ 是综合舒适指数
- $X_{THI}$ 是湿温指数
- $X_K$ 是风寒指数
- $X_I$ 是穿衣指数
""")
st.markdown("""由于气象指标受限，且为了简便运算，作者选择权重最大的THI（湿温指数）代表气候舒适度。""")
st.divider()
# 公式解释和变量解释
st.markdown("""### 计算湿温指数 (THI) 
温湿指数（THI）是用来评估人体对热环境舒适程度的一种指数。它综合了气温和湿度的影响，能够更准确地反映人体对环境热湿度的感受。""")
st.latex(r'''e_{\text{temp}} = 6.11 \times 10^{\left(\frac{7.5 \times \text{temp}}{237.3 + \text{temp}}\right)}''')
st.latex(r'''e_{\text{dew}} = 6.11 \times 10^{\left(\frac{7.5 \times \text{dewp}}{237.3 + \text{dewp}}\right)}''')
st.latex(r'''RH = 100 \times \left(\frac{e_{\text{dew}}}{e_{\text{temp}}}\right)''')
st.latex(r'''THI = (1.8 \times \text{temp} + 32) - 0.55 \times \left(1 - \frac{RH}{100}\right) \times (1.8 \times \text{temp} - 26)''')
st.markdown("""
- **temp**：气温（摄氏度）
- **dewp**：露点温度（摄氏度）
- **e_temp**：饱和水汽压（以气温计算）
- **e_dew**：饱和水汽压（以露点温度计算）
- **RH**：相对湿度（百分比）
- **THI**：湿温指数""")
st.divider()
st.markdown("""### 湿温指数 (THI)分级表
下表展示了不同温湿指数 (THI) 范围对应的人体感受、适宜着衣和等级赋值。""")
data = {
    "湿温指数(THI)": ["<40", "40~45", "45~55", "55~60", "60~65", "65~70", "70~75", "75~80", ">80"],
    "人体感受": ["极冷， 极不舒适", "寒冷， 不舒适", "偏冷， 较不舒适", "清凉， 舒适", "凉， 非常舒适", "暖， 舒适", "偏热， 较舒适", "闷热， 不舒适", "极闷热， 极不舒适"],
    "适宜着衣": ["羽绒或毛皮衣", "便服加坚实外套", "冬季常用服装", "春秋季常用便服", "衬衫和常用便服", "轻便的夏装", "短袖开领衫", "热带单衣", "超短裙"],
    "等级赋值": [1, 3, 5, 7, 9, 7, 5, 3, 1]
}

df = pd.DataFrame(data)
st.table(df)
st.markdown("""
- **湿温指数 (THI)**：表示温湿指数的范围。
- **人体感受**：描述在该温湿指数范围内人体的主观感受。
- **适宜着衣**：在该温湿指数范围内适宜的着装建议。
- **等级赋值**：对每个温湿指数范围的等级进行赋值，用于进一步分析或计算。
""")