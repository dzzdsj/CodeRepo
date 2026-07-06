
import requests
import json
import base64
from PIL import Image
import io
import os
from datetime import datetime
import platform
import subprocess

def generate_image(txt2img_url, image_description):
    """调用 Stable Diffusion API 生成图像"""
    url = txt2img_url
    payload = {
        "prompt": image_description,  # 使用意图中的描述作为提示词
        "negative_prompt": "",
        "steps": 20,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "seed": -1,
        "sampler_name": "Euler a",
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # 解析响应并获取图像数据
        r = response.json()
        image_data = r["images"][0]
        image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))
        
        # 创建 images 目录（如果不存在）
        os.makedirs("images", exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        filename = f"images/{timestamp}.png"
        
        # 保存图像
        image.save(filename)
        
        return filename
    except requests.exceptions.RequestException as e:
        print(f"图像生成请求失败: {e}")
        return None
    except Exception as e:
        print(f"图像处理失败: {e}")
        return None

def open_image(filename):
    """根据操作系统打开图像文件"""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", filename], check=True)
        elif system == "Windows":  # Windows
            os.startfile(filename)  # Windows 特有函数
        elif system == "Linux":  # Linux
            subprocess.run(["xdg-open", filename], check=True)
        else:
            print(f"不支持的操作系统: {system}")
    except Exception as e:
        print(f"打开图像失败: {e}")

def draw_and_show_image(txt2img_url, image_description):
    """生成并展示图像"""
    filename = generate_image(txt2img_url, image_description)
    if filename:
        print(f"图像已经生成，文件名：{filename}")
        open_image(filename)