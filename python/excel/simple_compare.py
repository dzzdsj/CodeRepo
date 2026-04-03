import pandas as pd
import re
file_path = '/Users/dzzdsj/tmp/workbook.xlsx'
df = pd.read_excel(file_path)
# 重命名列（可选）
# df.columns = ['ID', 'Value1', 'Name', 'Value2']
# 按位置取列，假设为第1~4列= Value2 的行
col1 = df.iloc[:, 0].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))  # 提取连续数字作为短卡号
col2 = df.iloc[:, 1].astype(str)  # 值1
col3 = df.iloc[:, 2].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))  # 提取连续数字作为长卡号
col4 = df.iloc[:, 3].astype(str)  # 值2

# 遍历比较
for i in range(len(df)):
    short = col1.iloc[i]
    long = col3.iloc[i]
    val1 = col2.iloc[i]
    val2 = col4.iloc[i]

    if short in long and val1 != val2:
        print(f"行 {i}: 短号 {short} 包含于长号 {long}，但值不同: {val1} ≠ {val2}")
