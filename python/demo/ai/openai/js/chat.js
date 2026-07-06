
const { OpenAI } = require('openai/index.mjs');

// 1. 初始化 OpenAI 客户端，连接 Ollama 服务
const client = new OpenAI({
    baseURL: 'http://localhost:11434/v1/',  // Ollama 的本地 API 地址
    apiKey: 'ollama',                            // Ollama 的占位符 API 密钥
});

// 2. 定义异步函数处理会话
async function runConversation() {
    // 第一次对话
    const message1 = { role: 'user', content: '请问北京有哪些著名的旅游景点？' };
    const responseFirstRound = await client.chat.completions.create({
        model: 'deepseek-r1:14b',    // 指定 Ollama 中的模型
        messages: [message1],        // 单条用户消息
        stream: true,                // 启用流式响应
    });

    // 输出第一次的响应
    process.stdout.write('第一轮会话: ');
    let assistantResponse = '';
    for await (const chunk of responseFirstRound) {
        const content = chunk.choices[0]?.delta?.content || '';
        process.stdout.write(content);
        assistantResponse += content;
    }

    // 第二次对话，传递历史对话
    const message2 = { role: 'user', content: '在这些景点中，哪个最适合春天去游玩？' };
    const messages = [
        { role: 'user', content: '请问北京有哪些著名的旅游景点？' },      // 第一次用户提问
        { role: 'assistant', content: assistantResponse },                    // 第一次助手回答
        { role: 'user', content: '在这些景点中，哪个最适合春天去游玩？' } // 第二次用户提问
    ];

    const responseSecondRound = await client.chat.completions.create({
        model: 'deepseek-r1:1.5b_new',  // 使用不同的模型
        messages: messages,             // 包含完整对话历史
        stream: true,                   // 启用流式响应
    });

    // 输出第二次的响应
    process.stdout.write('\n第二轮会话: ');
    for await (const chunk of responseSecondRound) {
        const content = chunk.choices[0]?.delta?.content || '';
        process.stdout.write(content);
    }

    console.log();  // 换行
}

// 运行会话
runConversation().catch(console.error);