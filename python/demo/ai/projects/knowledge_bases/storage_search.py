import chromadb

# 创建内存模式的客户端和集合
client = chromadb.Client()
collection = client.create_collection(name="example_collection")

# 示例文本和假设的嵌入向量（简化为一维列表，实际为多维）
texts = [
    "软件开发是一个复杂的过程。",
    "人工智能正在改变世界。",
    "网络安全至关重要。"
]
embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]  # 假设的向量
ids = ["doc1", "doc2", "doc3"]

# 存储向量和文本
collection.add(embeddings=embeddings, documents=texts, ids=ids)

# 查询示例
query_embedding = [0.25, 0.35]  # 假设的查询向量
results = collection.query(query_embeddings=[query_embedding], n_results=2)

# 输出结果
print("查询结果：")
for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
    print(f"匹配 {i+1}: {doc} (距离: {dist:.4f})")
