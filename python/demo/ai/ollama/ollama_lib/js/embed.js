import ollama from 'ollama';

// 请求对象，设置模型和输入文本
const request = {
  model: "bge-m3",  // 指定用于生成向量的模型
  input: "The quick brown fox jumps over the lazy dog.",  // 要生成向量的输入文本
  keep_alive: "1h"  // 保持模型加载1小时
};

// 调用 embed 函数生成文本向量
const response = await ollama.embed(request);

// 输出生成的文本向量
console.log("Generated Text Vector:");
console.log(response.embeddings);
