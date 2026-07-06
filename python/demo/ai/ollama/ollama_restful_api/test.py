
import sys

def parse_unicode(text):
    # 查找所有的\\uXXXX模式，并将其转换为对应的Unicode字符
    import re
    def replace_unicode(match):
        return chr(int(match.group(1), 16))
    
    return re.sub(r'\\u([0-9A-Fa-f]{4})', replace_unicode, text)

# 示例文本
text = "\\u003cthink\\u003e"

# 解析并输出
parsed_text = parse_unicode(text)
print(parsed_text)
'''
b'{"model":"deepseek-r1:14b","created_at":"2025-02-19T02:44:01.021704Z","response":"\\u003cthink\\u003e","done":false}'
b'{"model":"deepseek-r1:14b","created_at":"2025-02-19T02:44:01.12239Z","response":"\\n\\n","done":false}'
b'{"model":"deepseek-r1:14b","created_at":"2025-02-19T02:44:01.222113Z","response":"\\u003c/think\\u003e","done":false}'
'''