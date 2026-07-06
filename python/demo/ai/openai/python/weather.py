from openai import OpenAI
import json

if __name__ == "__main__":
    # 1. 初始化 OpenAI 客户端，指向 Ollama OpenAI 兼容 API
    client = OpenAI(
        base_url='http://localhost:11434/v1',  # 默认 Ollama OpenAI 兼容 API 地址，请根据实际情况修改
        api_key='ollama', # Ollama API Key 可以设置为任意值，这里设置为 'ollama'
    )

    # 2. 定义函数列表，格式与 OpenAI Function Calling 兼容
    tools = [
        {
            "type": "function",
            "function": {
                "name": "draw_image",
                "description": "当用户想要绘制图像时调用此函数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_description": {
                            "type": "string",
                            "description": "绘制图像的详细描述，例如：a photo-realistic image of a cat wearing sunglasses",
                        },
                    },
                    "required": ["image_description"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_word_document",
                "description": "当用户想要生成 Word 文档时调用此函数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_content": {
                            "type": "string",
                            "description": "Word 文档的内容，例如：请撰写一份关于人工智能的报告。",
                        },
                    },
                    "required": ["document_content"],
                },
            },
        },
    ]

    # 用户 prompt 示例
    prompts = [
        "请绘制一张戴着墨镜的猫的图像",
        "请生成一份关于人工智能的 Word 文档",
        "今天天气怎么样？" # 不触发函数调用的 prompt
    ]

    for user_message in prompts:
        print(f"\n**用户 Prompt:** {user_message}")

        # 3. 调用 OpenAI 兼容 API (Ollama)，发送用户消息和工具列表
        chat_completion = client.chat.completions.create(
            model="qwen2.5:0.5b",  # 替换为你的 Ollama 模型名称 (例如 llama2)
            messages=[
                {"role": "user", "content": user_message}
            ],
            tools=tools,
            tool_choice="auto", #  设置为 "auto" 让模型决定是否使用工具
            stream=False #  这里为了代码简洁，先禁用流式响应，可以设置为 True 启用
        )

        message = chat_completion.choices[0].message

        # 4. 检查模型是否请求工具调用
        tool_calls = message.tool_calls
        if tool_calls:
            print(f"message.tool_calls 的类型: {type(message.tool_calls)}") # 添加打印语句
            print(f"message.tool_calls 的内容: {message.tool_calls}")   # 添加打印语句
            tool_call = tool_calls[0]
            tool_function = tool_call.function # Line 75 - 错误发生行
            tool_name = tool_function.name
            tool_arguments = json.loads(tool_function.arguments)

            print(f"函数调用被触发: {tool_name}")
            print(f"函数参数: {tool_arguments}")

            # 在这里可以根据 tool_name 和 tool_arguments 调用其他系统处理任务
            if tool_name == "draw_image":
                image_description = tool_arguments.get("image_description")
                print(f"意图: 绘制图像，描述: {image_description}")
                # 调用图像绘制系统，例如 Stable Diffusion API 等
                #... 调用图像绘制系统的代码...

            elif tool_name == "generate_word_document":
                document_content = tool_arguments.get("document_content")
                print(f"意图: 生成 Word 文档，内容: {document_content}")
                # 调用 Word 文档生成系统，例如 python-docx 等
                #... 调用 Word 文档生成系统的代码...

            # 中断模型回复，因为意图已经通过函数调用识别
            print("模型回复已中断，任务将通过其他系统处理。")

        else:
            # 如果模型没有请求工具调用，直接输出模型回复
            print("模型正常回复:")
            print(message.content)