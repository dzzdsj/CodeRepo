
import os
import docx
import re
from datetime import datetime
import requests
import json
import base64
from PIL import Image
import io
from openai import OpenAI

# 全局变量定义
OLLAMA_MODEL = "deepseek-r1:14b"  # 替换为你的 Ollama 模型名称
OLLAMA_BASE_URL = 'http://192.168.31.208:11434/v1'  # 默认 Ollama OpenAI 兼容 API 地址
OLLAMA_API_KEY = 'ollama'  # Ollama API Key 可以设置为任意值
SD_API_URL = "http://192.168.31.80:7860/sdapi/v1/txt2img"


def generate_image_for_article(path, width=512, height=512):
    """
    为Word或txt格式文章配图的函数。

    Args:
        path: Word或txt文档的路径。
        width: 生成图像的宽度，默认为512。
        height: 生成图像的高度，默认为512。
    """

    # 1. 读取文章内容
    try:
        if path.endswith('.docx'):
            doc = docx.Document(path)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            text = '\n'.join(full_text)
        elif path.endswith('.txt'):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file format. Only .docx and .txt are supported.")

        text = text[:3000]  # 截取前3000字

    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. 调用 Ollama 大模型生成图像提示词
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

    user_message = f"""Below is an article. Now I need to create an image for this article. Please extract a prompt for generating related image from this article, within 80 words.  And convert to English. Do not add other prefixes, Chinese version etc. directly output the English version of the prompt\n\n{text}."""

    try:
        chat_completion = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "user", "content": user_message}
            ],
            stream=False
        )
        image_prompt = chat_completion.choices[0].message.content
        # print(f"Generated Image Prompt: {image_prompt}") # 可以打印看看生成的prompt

        # 提取 </think> 之后的内容（如果存在）
        match = re.search(r"</think>(.*)", image_prompt, re.DOTALL)  # re.DOTALL 让 . 匹配包括换行符在内的所有字符
        if match:
            image_prompt = match.group(1).strip()  # .strip() 去除首尾空白字符


    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return
    print(image_prompt)
    # 3. 调用 SD API 生成图像
    payload = {
        "prompt": image_prompt,
        "negative_prompt": "",  # 可选，添加负面提示词
        "steps": 20,
        "cfg_scale": 7,
        "width": width,
        "height": height,
        "seed": -1,
        "sampler_name": "Euler a",
    }

    try:
        response = requests.post(SD_API_URL, json=payload)
        response.raise_for_status()  # 检查请求是否成功，如果不成功会抛出异常

        r = response.json()
        image_data = r["images"][0]
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))

        # 4. 保存图像
        file_name, _ = os.path.splitext(os.path.basename(path))
        now = datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
        image_path = os.path.join(os.path.dirname(path), f"{file_name}_{timestamp}.png")
        image.save(image_path)
        print(f"Image saved to: {image_path}")
        return image_path


    except requests.exceptions.RequestException as e:
        print(f"Error calling SD API: {e}")
    except Exception as e:
        print(f"Error saving image: {e}")



if __name__ == '__main__':
    # 使用示例 - 替换为你的文件路径
    article_path = "article.docx"  # 或者 "article.txt"

    # 创建一个测试用的docx文件，用于程序测试。如果已经存在，就不用创建了,注意这里创建的是txt文件
    if not os.path.exists(article_path):
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write("这是一个测试文档，用于测试自动配图程序。\n")
            f.write("This is a test document for the automatic image generation program.\n")
            f.write("生成图像的提示词应该与文档内容相关。\n")



    print(generate_image_for_article(article_path, width=933, height=313))  # 可选：指定图像尺寸