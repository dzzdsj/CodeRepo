import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api"
API_EMBED_ENDPOINT = "/embed"
MODEL_NAME = "bge-m3"  #  使用 bge-m3 模型
INPUT_TEXT = "Hello world" #  固定输入文本

def get_text_embedding(model_name, prompt_text):
    """
    调用 Ollama API 的 /api/embed 接口生成文本向量。
    简化版本，直接返回 embedding 向量，出错时返回 None.
    """
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        "model": model_name,
        "input": prompt_text
    })

    try:
        response = requests.post(f"{OLLAMA_API_URL}{API_EMBED_ENDPOINT}", headers=headers, data=data)
        response.raise_for_status()
        json_data = response.json()
        return json_data.get("embeddings") #  直接返回 embeddings 字段 (注意复数形式)

    except requests.exceptions.RequestException as e:
        print(f"Error calling /api/embed: {e}")
        return None


if __name__ == '__main__':

    embedding_result = get_text_embedding(MODEL_NAME, INPUT_TEXT) #  获取固定输入文本的向量

    if embedding_result:
        print("\n文本向量:")
        print(embedding_result) #  直接打印向量结果
    else:
        print("\n获取文本向量失败.")