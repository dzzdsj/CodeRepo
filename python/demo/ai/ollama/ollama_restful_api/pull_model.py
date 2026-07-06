
import requests
import json
import sys

OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API 地址
API_PULL_ENDPOINT = "/pull" #  拉取模型端点

def pull_model(model_name):
    """
    调用 Ollama API /api/pull 端点拉取模型，并显示进度 (根据最新文档和实际响应更新, 优化 100% 输出).
    """
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'model': model_name}) #  请求体只需 model 参数
    download_100_printed = {} # 【新增】 记录已打印 100% 消息的 digest

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_PULL_ENDPOINT}", headers=headers, data=data, stream=True) #  使用 stream=True 启用 SSE
        response.raise_for_status() # 检查请求状态码

        for line in response.iter_lines(): # 逐行处理 SSE 响应
            if line:
                try:
                    event_data = json.loads(line) #  解析 JSON 格式的 SSE 数据
                    if 'status' in event_data:
                        status = event_data['status']
                        if status.startswith('pulling'): #  【修正】 判断 status 是否以 "pulling" 开头 (下载进度事件)
                            digest = event_data.get('digest') #  获取 digest
                            completed = event_data.get('completed', 0) #  已完成大小
                            total = event_data.get('total', 0) #  总大小
                            if digest and total > 0: #  确保 digest 和 total 存在
                                progress = (completed / total) * 100
                                if progress < 100: # 【新增】 只在进度小于 100% 时才输出
                                    print(f"Status: Downloading {progress:.2f}% ({completed}/{total} bytes)") #  显示更详细的下载状态
                                elif not download_100_printed.get(digest, False): # 【新增】 进度 100% 且未打印过 100% 消息
                                    print(f"Status: Downloading 100.00% ({completed}/{total} bytes)") #  显示 100% 状态 (只打印一次)
                                    download_100_printed[digest] = True # 【新增】 标记已打印 100% 消息
                            else:
                                print(f"Status: {status}") #  其他状态信息 (例如 pulling manifest, verifying 等)
                        else:
                             print(f"Status: {status}") #  打印其他状态信息 (例如 pulling manifest, verifying, complete 等)
                except json.JSONDecodeError:
                    print(f"Received non-JSON line: {line.decode('utf-8')}") #  处理非 JSON 行 (例如 SSE 注释)

        print(f"\nModel '{model_name}' pull complete!") #  拉取完成消息

    except requests.exceptions.RequestException as e:
        print(f"Error pulling model '{model_name}': {e}")
        if response is not None: # 打印详细错误信息 (如果 response 对象存在)
             print(f"Response status code: {response.status_code}")
             print(f"Response text: {response.text}")


if __name__ == '__main__':
    if len(sys.argv) != 2: # 检查命令行参数
        print("Usage: python pull_model.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1] #  获取命令行参数中的模型名称
    print(f"Pulling model '{model_name}'...")
    pull_model(model_name) #  调用拉取模型函数