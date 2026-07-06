
import requests
import json
import sys

OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API 地址
API_DELETE_ENDPOINT = "/delete" #  删除模型端点

def delete_model(model_name):
    """
    调用 Ollama API /api/delete 端点删除模型.
    """
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'model': model_name})

    try:
        response = requests.delete(f"{OLLAMA_API_URL}{API_DELETE_ENDPOINT}", headers=headers, data=data) #  使用 requests.delete() 发送 DELETE 请求
        response.raise_for_status() # 检查请求状态码

        if response.status_code == 200: #  成功删除 (200 OK)
            print(f"Model '{model_name}' successfully deleted!")
        else: #  其他成功状态码 (理论上不应该出现，作为保险)
            print(f"Model deletion operation completed with status code: {response.status_code}")
            print(f"Response text: {response.text}") #  打印响应文本 (如果有)

    except requests.exceptions.RequestException as e:
        print(f"Error deleting model '{model_name}': {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            if response.status_code == 404: #  模型未找到 (404 Not Found)
                print(f"Error: Model '{model_name}' not found and cannot be deleted.")
            else: #  其他错误 (打印响应文本)
                print(f"Response text: {response.text}")


if __name__ == '__main__':
    if len(sys.argv) != 2: # 检查命令行参数数量
        print("Usage: python delete_model.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1] #  获取命令行参数中的模型名称

    print(f"Deleting model '{model_name}'...")
    delete_model(model_name) #  调用删除模型函数
