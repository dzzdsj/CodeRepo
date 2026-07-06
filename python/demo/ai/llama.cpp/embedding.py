#pip install llama-cpp-python
from llama_cpp import Llama
import logging
import numpy as np

# 关闭 llama_cpp 日志
logging.getLogger("llama_cpp").setLevel(logging.CRITICAL)

# 创建模型实例，启用嵌入模式，禁用 GPU
model = Llama(
    model_path="/System/Volumes/Data/models/deepseek/deepseek-r1/bge-m3-Q8_0.gguf",
    n_ctx=2048,
    n_threads=4,
    embedding=True,
    n_gpu_layers=0,  # 禁用 GPU，使用 CPU
    verbose=False
)

# 固定文本
text = "你好，今天天气如何？"

try:
    # 尝试使用 create_embedding（如果可用）
    response = model.create_embedding(text)
    embedding = response['data'][0]['embedding']
except AttributeError:
    # 如果 create_embedding 不可用，使用 create_completion
    response = model.create_completion(text, max_tokens=1)
    embedding = response['embedding']

# 提取并输出向量
if embedding is not None:
    print(f"文本向量（前 10 维，维度总数：{len(embedding)}）：")
    print(np.array(embedding[:10]).tolist())
else:
    print("未能获取文本向量，请检查模型或 API 支持。")

# 打印文本以便对照
print(f"对应文本：{text}")