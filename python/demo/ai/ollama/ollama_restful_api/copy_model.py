
import requests
import json
import sys

OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API 地址
API_COPY_ENDPOINT = "/copy" #  复制模型端点

def copy_model(source_model_name, destination_model_name):
    """
    调用 Ollama API /api/copy 端点复制模型。
    """
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'source': source_model_name,
        'destination': destination_model_name
    })

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_COPY_ENDPOINT}", headers=headers, data=data)
        response.raise_for_status() # 检查请求状态码

        if response.status_code == 200: #  成功复制 (200 OK)
            print(f"Model '{source_model_name}' successfully copied to '{destination_model_name}'!")
        else: #  其他成功状态码 (理论上不应该出现，作为保险)
            print(f"Model copy operation completed with status code: {response.status_code}")
            print(f"Response text: {response.text}") #  打印响应文本 (如果有)


    except requests.exceptions.RequestException as e:
        print(f"Error copying model '{source_model_name}' to '{destination_model_name}': {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            if response.status_code == 404: #  源模型未找到 (404 Not Found)
                print(f"Error: Source model '{source_model_name}' not found.")
            else: #  其他错误 (打印响应文本)
                print(f"Response text: {response.text}")


if __name__ == '__main__':
    if len(sys.argv) != 3: # 检查命令行参数数量
        print("Usage: python copy_model.py <source_model_name> <destination_model_name>")
        sys.exit(1)

    source_model_name = sys.argv[1] #  获取源模型名称
    destination_model_name = sys.argv[2] #  获取目标模型名称

    print(f"Copying model '{source_model_name}' to '{destination_model_name}'...")
    copy_model(source_model_name, destination_model_name) #  调用复制模型函数
