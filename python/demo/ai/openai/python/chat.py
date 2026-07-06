
from openai import OpenAI
import os
if __name__ == "__main__":
    #如果开了代理，会报502，此时开启下面的代码才能调用成功
    # os.environ["http_proxy"] = "http://127.0.0.1:11434"
    # os.environ["https_proxy"] = "http://127.0.0.1:11434"
    # 1. 初始化 OpenAI 客户端，连接 Ollama 服务
    client = OpenAI(
        base_url='http://localhost:11434/v1/',  # Ollama 的本地 API 地址
        api_key='ollama',                            # Ollama 的占位符 API 密钥
    )

    # 2. 第一次对话
    message1 = {'role': 'user', 'content': '请问北京有哪些著名的旅游景点？'}
    response_first_round = client.chat.completions.create(
        model='deepseek-r1:8b',          # 指定 Ollama 中的模型
        messages=[message1],              # 单条用户消息
        stream=True                       # 启用流式响应
    )

    # 输出第一次的响应
    print("第一轮会话:")
    assistant_response = ''
    for chunk in response_first_round:
        content = chunk.choices[0].delta.content or ''  # 获取每个数据块的内容
        print(content, end='')
        assistant_response += content

    # 3. 第二次对话，传递历史对话
    message2 = {'role': 'user', 'content': '在这些景点中，哪个最适合春天去游玩？'}
    messages = [
        {'role': 'user', 'content': '请问北京有哪些著名的旅游景点？'},  # 第一次用户提问
        {'role': 'assistant', 'content': assistant_response},               # 第一次助手回答
        {'role': 'user', 'content': '在这些景点中，哪个最适合春天去游玩？'}  # 第二次用户提问
    ]

    response_second_round = client.chat.completions.create(
        model='deepseek-r1:8b',  # 使用不同的模型（模拟灵活性）
        messages=messages,             # 包含完整对话历史
        stream=True                    # 启用流式响应
    )

    # 输出第二次的响应
    print("\n第二轮会话:", end=" ")
    for chunk in response_second_round:
        content = chunk.choices[0].delta.content or ''  # 获取每个数据块的内容
        print(content, end='')

    print()  # 换行

    # os.environ["http_proxy"] = "http://127.0.0.1:11434"
    # os.environ["https_proxy"] = "http://127.0.0.1:11434"
    # client = OpenAI(
    #
    #     base_url="http://localhost:11434/v1",
    #
    #     api_key="ollama",
    #
    # )
    #
    # response = client.chat.completions.create(
    #
    #     model="deepseek-r1:8b",
    #
    #     messages=[
    #
    #         {"role": "user", "content": "你好"}
    #
    #     ],
    #
    # )