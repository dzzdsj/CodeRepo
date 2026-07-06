import chromadb
import os

# 定义持久化路径
CHROMA_PATH = "./chroma"

# 检查持久化路径是否存在，选择打开或创建
if os.path.exists(CHROMA_PATH):
    print(f"检测到现有持久化数据库 '{CHROMA_PATH}'，直接打开进行检索...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="persistent_collection")
else:
    print(f"持久化数据库 '{CHROMA_PATH}' 不存在，创建并存储数据...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.create_collection(name="persistent_collection")
    
    # 示例文本和假设的嵌入向量
    texts = [
        "软件开发是一个复杂的过程。",
        "人工智能正在改变世界。",
        "网络安全至关重要。"
    ]
    embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    ids = ["doc1", "doc2", "doc3"]

    # 存储向量和文本
    collection.add(embeddings=embeddings, documents=texts, ids=ids)

# 查询示例
query_embedding = [0.25, 0.35]
results = collection.query(query_embeddings=[query_embedding], n_results=2)

# 输出结果
print("查询结果：")
for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
    print(f"匹配 {i+1}: {doc} (距离: {dist:.4f})")