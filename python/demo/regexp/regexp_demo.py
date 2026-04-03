import re
def regexp_multiline():
    with open("./test_regexp.sql", "r", encoding="utf-8") as f:
        text = f.read()
        print(f'======================original text====================== \n{text}')
    # 提取所有 CREATE TABLE 语句块
    tables = re.findall(r'create\s+table\s+(\w+)\s*\(.*?\).*?(?:shardkey\s*=\s*(\w+))?;', text,
                        re.DOTALL | re.IGNORECASE)
    for table_name, shardkey in tables:
        print(f'{table_name} -> {shardkey if shardkey else "NULL"}')


if __name__ == '__main__':
    regexp_multiline()