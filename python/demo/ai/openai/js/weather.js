
const { OpenAI } = require('openai');

// 1. 初始化 OpenAI 客户端，连接 Ollama 服务
const client = new OpenAI({
    baseURL: 'http://192.168.31.208:11434/v1/',  // Ollama 的本地 API 地址
    apiKey: 'ollama',                            // 占位符 API 密钥
});

// 2. 定义模拟的天气查询函数
function getWeather(location) {
    // 模拟天气查询工具，这里返回预设数据
    const weatherData = {
        'Tokyo': { temperature: '10°C', conditions: 'Cloudy' },
        'London': { temperature: '5°C', conditions: 'Rainy' },
        'New York': { temperature: '0°C', conditions: 'Snowy' },
    };
    return weatherData[location] || { error: 'Location not found' };  
}

// 3. 定义工具列表
const tools = [
    {
        type: 'function',
        function: {
            name: 'get_weather',
            description: '获取指定地点的天气信息，将指定地点转换为英文，首字母大写',
            parameters: {
                type: 'object',
                properties: {
                    location: {
                        type: 'string',
                        description: '需要查询天气的地点 (城市名称)，需要转换为英文，首字母大写',
                    },
                },
                required: ['location'],
            },
        },
    },
];

// 4. 实现函数调用的异步函数
async function runFunctionCall() {
    // 用户输入
    const userMessage = '今天东京天气怎么样？';

    // 5. 发送请求，检查是否需要函数调用
    const chatCompletion = await client.chat.completions.create({
        model: 'qwen2.5:0.5b',       // 支持函数调用的模型
        messages: [{ role: 'user', content: userMessage }],
        tools: tools,
        tool_choice: 'auto',         // 让模型自动决定是否调用函数
        stream: false,               // 禁用流式响应以简化演示
    });

    const message = chatCompletion.choices[0].message;

    // 6. 处理函数调用
    if (message.tool_calls) {
        const toolCall = message.tool_calls[0];
        const toolFunction = toolCall.function;
        const toolName = toolFunction.name;
        const toolArguments = JSON.parse(toolFunction.arguments);

        if (toolName === 'get_weather') {
            // 7. 执行函数
            const weatherInfo = getWeather(toolArguments.location);

            // 8. 将结果反馈给模型
            const toolResponse = await client.chat.completions.create({
                model: 'qwen2.5:0.5b',
                messages: [
                    { role: 'user', content: userMessage },
                    message,
                    {
                        role: 'tool',
                        tool_call_id: toolCall.id,
                        name: toolName,
                        content: JSON.stringify(weatherInfo),
                    },
                ],
                tools: tools,
                tool_choice: 'auto',
                stream: false,
            });
            const finalResponse = toolResponse.choices[0].message.content;
            console.log(`最终回复: ${finalResponse}`);
        }
    } else {
        console.log(`模型回复: ${message.content}`);
    }
}

// 运行案例
runFunctionCall().catch(console.error);