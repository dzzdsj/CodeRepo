
from ollama import embed

# 请求对象，设置模型和输入文本
request = {
    "model": "bge-m3",  # 指定用于生成向量的模型
    "input": "The quick brown fox jumps over the lazy dog.",  # 要生成向量的输入文本
    "keep_alive": "1h"  # 保持模型加载1小时
}

# 调用 embed 函数生成文本向量
response = embed(request)

# 输出生成的文本向量
print("Generated Text Vector:")
print(response['embedding'])
