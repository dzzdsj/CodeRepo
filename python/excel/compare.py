import pandas as pd
import re

# 用于收集输出行
output_rows = []

# 读取文件
file_path = '/Users/dzzdsj/tmp/workbook.xlsx'
df = pd.read_excel(file_path, dtype={"短号列": str,"长号列": str,"短号金额": str,"长号金额": str})

# 提取纯数字字符串
short_ids = df.iloc[:, 0].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))
val1s = df.iloc[:, 1].astype(str)
long_ids = df.iloc[:, 2].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))
val2s = df.iloc[:, 3].astype(str)

# 嵌套比较：每一个短号去所有长号中查找
for i in range(len(df)):
    short = short_ids.iloc[i]
    val1 = val1s.iloc[i]

    # 清理空值或空格
    if not short.strip() or pd.isna(val1):
        continue

    for j in range(len(df)):
        long = long_ids.iloc[j]
        val2 = val2s.iloc[j]

        if not long.strip() or pd.isna(val2):
            continue

        if short in long and val1 != val2:
            print(f"短号在第{i}行，长号在第{j}行：短号 {short} 包含于长号 {long}，但值不同: {val1} ≠ {val2}")
            output_rows.append({
                "短号行": i,
                "长号行": j,
                "短号": short,
                "长号": long,
                "值1": val1,
                "值2": val2
            })

# 输出到 Excel 文件
if output_rows:
    result_df = pd.DataFrame(output_rows)
    result_df.to_excel('对比结果.xlsx', index=False)