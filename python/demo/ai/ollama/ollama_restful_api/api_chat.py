
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api"
API_CHAT_ENDPOINT = "/chat"
MODEL_NAME = "deepseek-r1:8b"  #  请替换为您想要使用的模型

def generate_chat_stream(messages):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True  #  启用流式响应
    })

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_CHAT_ENDPOINT}", headers=headers, data=data, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                json_data = json.loads(line.decode('utf-8'))
                message_content = json_data.get("message", {}).get("content", "") #  从 message.content 中获取文本
                if message_content:
                    yield message_content
                if json_data.get("done"):
                    break

    except requests.exceptions.RequestException as e:
        error_message = f"Error during chat generation: {e}"
        if response is not None:
            error_message += f"\nResponse status code: {response.status_code}"
            error_message += f"\nResponse text: {response.text}"
        yield error_message

if __name__ == "__main__":
    #  定义对话消息历史
    chat_history = [
        {"role": "user", "content": "请问北京有哪些著名的旅游景点？"} #  第一轮用户提问
    ]

    print("User: 请问北京有哪些著名的旅游景点？")
    print("Assistant: ", end="", flush=True) #  准备输出助手回复

    #  第一轮对话，获取模型回复并流式输出
    assistant_response_1 = "" #  用于积累第一轮助手的完整回复
    for token in generate_chat_stream(chat_history):
        print(token, end="", flush=True) #  逐 token 打印
        assistant_response_1 += token #  积累回复文本
    print("\n")

    #  将第一轮助手回复添加到对话历史
    chat_history.append({"role": "assistant", "content": assistant_response_1})

    #  第二轮用户提问，关联到第一轮回复
    user_prompt_2 = "在这些景点中，哪个最适合春天去游玩？"
    chat_history.append({"role": "user", "content": user_prompt_2}) #  添加到对话历史

    print(f"User: {user_prompt_2}")
    print("Assistant: ", end="", flush=True) #  准备输出助手回复
    print("第二轮")
    #  第二轮对话，获取模型回复并流式输出
    for token in generate_chat_stream(chat_history):
        print(token, end="", flush=True) #  逐 token 打印
    print("\n")