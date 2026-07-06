from flask import Flask, render_template, request
import requests
import json # 导入 json 库

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API 地址
API_TAGS_ENDPOINT = "/tags" #  列出模型端点
API_SHOW_ENDPOINT = "/show" # 获取模型信息端点

@app.route('/', methods=['GET', 'POST']) #  同时处理 GET 和 POST 请求
def model_info():
    models = [] #  模型列表
    model_details = None # 模型详细信息，初始为 None
    error_message = None # 错误消息，初始为 None

    try:
        # 1. 获取模型列表 (使用 /api/tags 端点)
        tags_response = requests.get(f"{OLLAMA_API_URL}{API_TAGS_ENDPOINT}")
        tags_response.raise_for_status()
        models_data = tags_response.json()
        models = models_data.get('models', [])
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching model list: {e}"

    if request.method == 'POST': #  如果是 POST 请求 (用户提交了模型选择)
        selected_model_name = request.form.get('model_name') # 获取用户选择的模型名称
        if selected_model_name:
            try:
                # 2. 获取模型详细信息 (使用 /api/show 端点)
                show_response = requests.post( #  /api/show 使用 POST 方法
                    f"{OLLAMA_API_URL}{API_SHOW_ENDPOINT}",
                    headers={'Content-Type': 'application/json'}, # 设置 Content-Type
                    data=json.dumps({'model': selected_model_name, 'verbose': True}) #  构建 JSON 请求体, verbose=True 获取详细信息
                )
                show_response.raise_for_status()
                model_details = show_response.json() # 解析模型详细信息 JSON
            except requests.exceptions.RequestException as e:
                error_message = f"Error fetching details for model '{selected_model_name}': {e}"

    return render_template('model_info.html', models=models, model_details=model_details, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
