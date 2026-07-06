
import chromadb
import requests
import json
import os
from typing import List, Dict
import logging
from flask import Flask, request, jsonify

# 设置日志级别
logging.getLogger("chromadb").setLevel(logging.ERROR)

# --- 设置 ---
OLLAMA_API_URL = "http://192.168.31.208:11434/v1/embeddings"  # Ollama API 地址
MODEL_NAME = "bge-m3"  # 使用的模型名称
CHROMA_DB_PATH = "./chroma_data"  # ChromaDB 数据存储路径
KNOWLEDGE_BASE_DIR = "./knowledge_bases"  # 知识库目录
PORT = 5005  # Flask 服务端口号

# 初始化 ChromaDB 客户端和集合
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name="knowledge_bases")

# 初始化 Flask 应用
app = Flask(__name__)

# --- 函数：使用 Ollama API 获取文本的嵌入向量 ---
def get_embedding(text: str) -> List[float]:
    """通过 Ollama API 获取文本的嵌入向量"""
    headers = {"Content-Type": "application/json"}
    data = {"model": MODEL_NAME, "input": text}
    
    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
    except requests.RequestException as e:
        print(f"Error during Ollama API call: {e}")
        return None

# --- 函数：加载知识库 ---
def load_knowledge_bases() -> None:
    """加载知识库到 ChromaDB，无论数据库是否存在，都确保 filename 正确设置"""
    global collection

    # 检查目录是否存在
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"Error: Knowledge base directory '{KNOWLEDGE_BASE_DIR}' does not exist.")
        return
    
    # 获取 txt 文件列表
    txt_files = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"No .txt files found in '{KNOWLEDGE_BASE_DIR}'.")
        return
    
    # 检查现有数据
    current_count = collection.count()
    reload_needed = False

    if current_count > 0:
        # 检查元数据是否有效
        sample = collection.peek(min(current_count, 1))  # 获取一个样本
        metadatas = sample.get("metadatas", [])
        if not metadatas or not isinstance(metadatas, list) or len(metadatas) == 0 or "filename" not in metadatas[0]:
            print("Existing data lacks valid metadata. Clearing and reloading knowledge base...")
            client.delete_collection(name="knowledge_bases")
            collection = client.get_or_create_collection(name="knowledge_bases")
            reload_needed = True
        elif current_count < len(txt_files):
            print(f"Existing data has {current_count} documents, but {len(txt_files)} files found. Reloading to update...")
            client.delete_collection(name="knowledge_bases")
            collection = client.get_or_create_collection(name="knowledge_bases")
            reload_needed = True
        else:
            print(f"Knowledge base already loaded with {current_count} documents. Verifying filenames...")
            # 检查所有文件的元数据
            existing_data = collection.get(include=["metadatas"])
            existing_filenames = {item["filename"] for item in existing_data["metadatas"] if item}
            expected_filenames = {filename for filename in txt_files}
            if existing_filenames != expected_filenames:
                print("Filenames mismatch detected. Reloading knowledge base...")
                client.delete_collection(name="knowledge_bases")
                collection = client.get_or_create_collection(name="knowledge_bases")
                reload_needed = True
            else:
                print("All filenames are correct. Skipping reload.")
                return

    # 如果需要重新加载或数据库为空，则加载所有文件
    if reload_needed or current_count == 0:
        for filename in txt_files:
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if not text:
                        print(f"Warning: File '{filename}' is empty.")
                        continue
                
                embedding = get_embedding(text)
                if embedding is None:
                    continue
                
                collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[{"filename": filename}],
                    ids=[filename.split(".")[0]]
                )
                print(f"Processed and added: {filename}")
            
            except FileNotFoundError:
                print(f"Error: File not found: {filepath}")
            except Exception as e:
                print(f"Error processing '{filename}': {e}")

# --- 函数：根据 prompt 获取匹配的知识库内容 ---
def get_knowledge_items_from_prompt(prompt: str, threshold: float = 0.7) -> List[Dict[str, str]]:
    """根据 prompt 获取匹配的知识库内容"""
    if not prompt.strip():
        print("Error: Prompt is empty.")
        return []

    query_embedding = get_embedding(prompt)
    if query_embedding is None:
        return []

    if collection.count() == 0:
        print("Error: Knowledge base is empty. Please load data first.")
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=collection.count(),
        include=["documents", "distances", "metadatas"]
    )

    matched_contents = []
    distances = results.get("distances", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0] or []

    for i, distance in enumerate(distances):
        similarity = 1 - (distance ** 2) / 2       
        if similarity >= threshold:
            filename = metadatas[i]["filename"] if i < len(metadatas) and metadatas[i] else f"unknown_{i}.txt"
            
            matched_contents.append({
                "filename": filename,
                "content": documents[i]
            })

    if not matched_contents:
        print(f"No matches found above threshold {threshold}.")
    
    return matched_contents

# --- Flask Web 服务 ---
@app.route('/search', methods=['POST'])
def search_knowledge():
    """POST 接口，接收 prompt 并返回匹配结果"""
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    prompt = data["prompt"]
    matches = get_knowledge_items_from_prompt(prompt, threshold=0.4)
    return jsonify({"results": matches})

# --- 主程序 ---
if __name__ == "__main__":
    load_knowledge_bases()
    print(f"Starting Flask server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)