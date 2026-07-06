from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import requests
import json
import html  # 引入html模块用于转义特殊字符

app = Flask(__name__)

OLLAMA_API_URL = "http://localhost:11434/api"
API_GENERATE_ENDPOINT = "/generate"
MODEL_NAME = "deepseek-r1:8b"  # 默认模型，可以修改
CHUNK_SIZE = 50  # 设置每次返回的字符数阈值
def parse_unicode(text):
    # 查找所有的\\uXXXX模式，并将其转换为对应的Unicode字符
    import re
    def replace_unicode(match):
        return chr(int(match.group(1), 16))
    
    return re.sub(r'\\u([0-9A-Fa-f]{4})', replace_unicode, text)
def generate_streaming_text(model_name, prompt_text):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({  
        "model": model_name,
        "prompt": prompt_text,
        "stream": True  # 启用流式响应
    })

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_GENERATE_ENDPOINT}", headers=headers, data=data, stream=True)
        response.raise_for_status()

        accumulated_text = ""  # 用于积累返回的文本
        for line in response.iter_lines():
            print(line)
            if line:
            
                json_data = json.loads(line.decode('utf-8'))
                response_part = json_data.get("response", "")
                if response_part:
                    yield f"{response_part}"  # 使用 SSE 发送流式数据
                       

        # 如果最后剩余的文本不足一个块，也发送出去
        if accumulated_text:
            safe_text = html.escape(accumulated_text)
            yield f"{safe_text}\n\n"

    except requests.exceptions.RequestException as e:
        error_message = f"Error during text generation: {e}"
        if response is not None:
            error_message += f"\nResponse status code: {response.status_code}"
            error_message += f"\nResponse text: {response.text}"
        yield f"data: {html.escape(error_message)}\n\n"


@app.route('/', methods=['GET'])
def index():
    if request.method == 'POST':
        prompt = request.form['message']
        return render_template('index.html', model_response=stream_with_context(generate_streaming_text(MODEL_NAME, prompt)))

    return render_template('index.html')


@app.route('/stream', methods=['POST'])
def stream():
    prompt = request.form.get('prompt', '')  # 获取前端传来的 prompt 参数（注意使用 POST 请求）
    if prompt:
        return Response(generate_streaming_text(MODEL_NAME, prompt), content_type='text/event-stream')
    else:
        return "Prompt not provided", 400  # 返回错误信息


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
