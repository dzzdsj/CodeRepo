
from openai import OpenAI
import sys
import requests
import json
from draw_image import draw_and_show_image,open_image
from article_image import generate_image_for_article

def load_config(config_file="config.txt"):
    """从 config.txt 文件加载配置"""
    config = {}
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        base_url = config.get('base_url', 'http://localhost:11434/v1')
        api_key = config.get('api_key', 'ollama')
        model = config.get('model', 'qwen2.5:1.5b')
        intent_url = config.get('intent_identification_url', 'http://localhost:5001/identify_intent')
        txt2img_url = config.get('txt2img_url', 'http://192.168.31.80:7860/sdapi/v1/txt2img')
        
        return base_url, api_key, model, intent_url, txt2img_url
    except FileNotFoundError:
        print(f"找不到配置文件: {config_file}")
        sys.exit(1)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        sys.exit(1)

def create_client(base_url, api_key):
    """创建 OpenAI 客户端"""
    return OpenAI(
        base_url=base_url,
        api_key=api_key
    )

def identify_intent(intent_url, user_input):
    """发送 HTTP 请求判断意图"""
    url = intent_url
    headers = {"Content-Type": "application/json"}
    data = {"prompt": user_input}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"意图判断请求失败: {e}")
        return {"results": []}

def stream_chat(client, model, user_input, tools=None):
    """与模型进行流式聊天"""
    try:
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": user_input}
            ],
            tools=tools,
            tool_choice="auto",
            stream=True
        )
        
        for chunk in chat_completion:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"聊天过程中发生错误: {e}")

def main():
    # 加载配置
    base_url, api_key, model, intent_url, txt2img_url = load_config()
    
    # 创建 OpenAI 客户端
    client = create_client(base_url, api_key)
    
    # 主循环
    while True:
        try:
            user_input = input("prompt: ")
            if not user_input.strip():
                continue
            
            # 判断意图
            intent_result = identify_intent(intent_url, user_input)
            results = intent_result.get("results", [])
            
            if results:
                intent = results[0]
                if intent.get("type") == "draw_image":
                    print("正常生成图像...")
                    draw_and_show_image(txt2img_url, intent.get("image_description"))
                    continue
                elif intent.get("type") == "article_image":
                    print(f"正在为【{intent.get('path')}】配图...")
                    article_image_path = generate_image_for_article(intent.get("path"), width=intent.get("width"), height=intent.get("height"))
                    if article_image_path:
                        open_image(article_image_path)
                    print(f"已经完成配图，图像文件名：{article_image_path}")
                    continue
            filename_string = None  
            # 无意图或未处理的意图类型，继续正常聊天
            if(user_input):
                # user_input的首字母为@，则认为是@指令
                if user_input[0] == "@":
                    url = "http://localhost:5005/search"
                    headers = {"Content-Type": "application/json"}
                    data = {"prompt": user_input}
                    response = requests.post(url, headers=headers, data=json.dumps(data))
 
                    # 检查响应状态码
                    if response.status_code == 200:
                        # 请求成功，打印响应内容
                        response_json = response.json()
                        contents = []
                        filenames = []

                        if 'results' in response_json and isinstance(response_json['results'], list):
                            for item in response_json['results']:
                                if isinstance(item, dict):
                                    if 'content' in item and isinstance(item['content'], str):
                                        contents.append(item['content'])
                                    if 'filename' in item and isinstance(item['filename'], str):
                                        filenames.append(item['filename'])

                            content_string = '\n'.join(contents)
                            filename_string = ','.join(filenames)
                            user_input = user_input[1:] + '\n下面是相关的领域知识，可以参考下面的内容解答：\n【' + content_string + '】\n\n'
            if filename_string:
                print("使用的知识库:" + filename_string + "\n") 
            stream_chat(client, model, user_input)
            
        except KeyboardInterrupt:
            print("\n程序已退出")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()