import streamlit as st
import random
import time
import pandas as pd

# df = pd.read_excel(r"D:\桌面\多阅阅读桥\金源乡中心小学在校生信息.xls", sheet_name=21)
# # 选择需要的列（假设是第一列，从第二行开始）
# column_name = df.columns[0]  # 获取第一列的列名
# names = df[column_name].iloc[1:].tolist()
# print(names)
names = ['张薇', '李睿婷', '贺发存', '张艺彤', '黄六顺', '佘明昊', '李开有', '张德燕', '陈宏英', '来龙江', '孙艳美', '张晓茜', '罗光耀', '李志玲', '陈加艳', '杨皓天', '蔡青赢', '周加蓉', '赵静嬿', '柏兴飞', '皮富美', '范官云', '龙颖', '周杰', '陈明', '普行瑞', '孙刘涛', '刘杰', '龙欣', '李浩', '沈妍妮', '黄渤涵', '马顺玉', '廖梓湘', '杨俊', '张警瑞', '李欣怡', '苏丽平', '秦光呈', '陈明薇', '朱福永', '苏院龙', '张龙', '陈思蕊', '李涵']

if st.button("开始"):
   # placeholder1 = st.empty()   #第一个容器
    placeholder2 = st.empty()   #第二个容器
    for i in range(15):
       # placeholder1.header(f"{i+1}秒")
        name = random.choice(names)
        placeholder2.header(name)
        time.sleep(0.2)
    st.title(f"恭喜{name}小朋友！")
