
from flask import Flask, render_template
import requests

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434/api"  # Ollama API 地址
API_ENDPOINT = "/tags" #  更正为 /api/tags  的正确端点路径

@app.route('/models')
def list_models():
    """
    调用 Ollama API /api/tags 端点，获取本地模型列表，
    并在 Web 页面上展示模型名称。
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}{API_ENDPOINT}") # 使用正确的 API 端点路径
        response.raise_for_status()  # 检查请求状态码
        models_data = response.json()  # 解析 JSON 响应
        models = models_data.get('models', [])  # 获取模型列表，默认为空列表
        return render_template('models.html', models=models)  # 渲染模板
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching models from Ollama API: {e}"
        return render_template('models.html', models=[], error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
