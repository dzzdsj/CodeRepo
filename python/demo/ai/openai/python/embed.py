
from openai import OpenAI


# 初始化 OpenAI 客户端，配置 Ollama 的本地服务地址
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama 的默认 API 地址
    api_key="ollama"                       # Ollama 不需要真实的 API 密钥，使用占位符
)

# 输入文本
text = "这是一个测试句子，用于生成文本向量。"

try:
    # 调用嵌入端点生成文本向量
    response = client.embeddings.create(
        model="bge-m3",  # 使用支持嵌入的模型
        input=text                 # 输入单个字符串（也可以传入字符串列表）
    )

    # 获取生成的向量
    embedding = response.data[0].embedding

    # 打印向量的前几个值（完整向量可能很长）
    print("生成的文本向量（前5个值）：", embedding[:5])
    print("向量长度：", len(embedding))

  

except Exception as e:
    print(f"发生错误：{e}")