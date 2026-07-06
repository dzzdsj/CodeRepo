
import requests
import json
import base64
from PIL import Image
import io

# API 地址
url = "http://192.168.31.80:7860/sdapi/v1/img2img"  # 替换为你的 WebUI 地址

# 读取初始图像并进行 Base64 编码
with open("generated_image.png", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    # image_file.read() 读取图像文件的二进制数据
    # base64.b64encode() 将二进制数据编码为 Base64 字符串
    # .decode('utf-8') 将 bytes 类型转换为 str 类型

# 请求参数
payload = {
    "init_images": [encoded_string],  # 初始图像 (Base64 编码)
    "prompt": "A cute panda wearing a Superman costume is dancing on a cliff,highly detailed,4k,masterpiece",  # 正面提示词
    "negative_prompt": "blurry, low quality, deformed, cartoon",  # 负面提示词
    "denoising_strength": 0.6,   #重绘幅度
    "steps": 30,                 # 采样步数
    "cfg_scale": 7,            #提示强度
    "width": 512,              # 图像宽度
    "height": 512,             # 图像高度
    "seed": -1,                  # 随机种子
    "sampler_name": "DPM++ 2M",  # 采样器
}

# 发送 POST 请求
response = requests.post(url, json=payload)

# 解析响应
if response.status_code == 200:
    # 获取生成的图像（Base64 编码）
    r = response.json()
    image_data = r["images"][0]

    # 解码并保存图像
    image = Image.open(io.BytesIO(base64.b64decode(image_data.split(",", 1)[0])))
    image.save("output.png")  # 将生成的图像保存为 output.png
    print("图像已保存为 output.png")

else:
    # 请求失败，打印错误信息
    print("请求失败，状态码:", response.status_code)
    print("错误信息:", response.text)