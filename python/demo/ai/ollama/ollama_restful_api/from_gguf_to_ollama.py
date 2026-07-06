
import requests
import json
import hashlib
import os

OLLAMA_API_URL = "http://localhost:11434/api"
API_CREATE_ENDPOINT = "/create"

def calculate_sha256(filepath):
    """
    计算文件的 SHA256 摘要.

    Args:
        filepath (str): 文件路径.

    Returns:
        str: 文件的 SHA256 摘要 (十六进制字符串).
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f: #  以二进制读取模式打开文件
        for byte_block in iter(lambda: f.read(4096), b""): #  分块读取文件内容
            sha256_hash.update(byte_block) #  更新哈希对象
    return "sha256:" + sha256_hash.hexdigest() #  返回带 "sha256:" 前缀的十六进制摘要字符串


def create_model_from_gguf(new_model_name, files_data):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "model": new_model_name,
        "files": files_data
    })

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_CREATE_ENDPOINT}", headers=headers, data=data, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8')) #  直接打印 SSE 原始数据 (JSON 字符串)

        print(f"\nModel '{new_model_name}' creation from GGUF completed!")

    except requests.exceptions.RequestException as e:
        print(f"Error creating model '{new_model_name}' from GGUF: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")

if __name__ == '__main__':
    new_model_name = "my-gguf-model" #  新模型名称
    gguf_filepath = "DeepSeek-R1-Distill-Qwen-7B-Q8_0.gguf" #  GGUF 文件路径

    # 计算 GGUF 文件的 SHA256 摘要
    gguf_digest = calculate_sha256(gguf_filepath)
    print(f"Calculated SHA256 digest for {gguf_filepath}: {gguf_digest}")

    files_data = {
        gguf_filepath: gguf_digest
    }

    print(f"Creating model '{new_model_name}' from GGUF file '{gguf_filepath}'...")
    create_model_from_gguf(new_model_name, files_data)