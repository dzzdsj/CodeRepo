
import requests
import json
import base64
from PIL import Image
import io

# API 地址
url = "http://192.168.31.80:7860/sdapi/v1/txt2img"

# 请求参数
payload = {
    "prompt": "A cute panda wearing a Superman costume is dancing on a cliff,highly detailed,4k,masterpiece",  # 提示词
    "negative_prompt": "blurry, low quality, deformed, cartoon",  # 负面提示词（可选）
    "steps": 20,  # 生成步数
    "cfg_scale": 7,  # 提示词相关性
    "width": 512,  # 图像宽度
    "height": 512,  # 图像高度
    "seed": -1,  # 随机种子，-1 表示随机
    "sampler_name": "DPM++ 2M",  # 采样器
}

# 发送 POST 请求
response = requests.post(url, json=payload)

# 解析响应
if response.status_code == 200:
    # 获取生成的图像（base64 编码）
    r = response.json()
    image_data = r["images"][0]
    # 解码并保存图像
    image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))
    image.save("generated_image.png")
    print("图像已保存为 generated_image.png")
else:
    print("请求失败，状态码:", response.status_code)
    print("错误信息:", response.text)