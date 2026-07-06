
const { OpenAI } = require('openai');

// 初始化 OpenAI 客户端，配置 Ollama 的本地服务地址
const client = new OpenAI({
    baseURL: 'http://localhost:11434/v1',  // Ollama 的默认 API 地址
    apiKey: 'ollama'                       // Ollama 不需要真实的 API 密钥，使用占位符
});

// 输入文本
const text = '这是一个测试句子，用于生成文本向量。';

async function getEmbedding() {
    try {
        // 调用嵌入端点生成文本向量
        const response = await client.embeddings.create({
            model: 'bge-m3',  // 使用支持嵌入的模型
            input: text       // 输入单个字符串（也可以传入字符串数组）
        });

        // 获取生成的向量
        const embedding = response.data[0].embedding;

        // 打印向量的前几个值（完整向量可能很长）
        console.log('生成的文本向量（前5个值）：', embedding.slice(0, 5));
        console.log('向量长度：', embedding.length);
    } catch (e) {
        console.log('发生错误：', e);
    }
}

// 运行案例
getEmbedding();
