import ollama from 'ollama';

// --------------------------- 单轮会话 ---------------------------
// 使用 generate 函数进行单轮会话，并使用流式输出

const singleRoundQuestion = "天空为什么是蓝色的？";

const responseSingleRound = await ollama.generate({ model: 'deepseek-r1:1.5b_new', prompt: singleRoundQuestion, stream: true });

console.log("Single Round Response:");
for await (const part of responseSingleRound) {
    process.stdout.write(part.response);  // 输出每部分内容
}

// --------------------------- 多轮会话 ---------------------------
// 第一次对话
const message1 = { role: 'user', content: '请问北京有哪些著名的旅游景点？' };
const responseFirstRound = await ollama.chat({ model: 'deepseek-r1:1.5b_new', messages: [message1], stream: true });

console.log("\n\n第一轮会话:");
let assistantResponse = '';
for await (const part of responseFirstRound) {
    process.stdout.write(part.message.content);  // 输出第一次的响应内容
    assistantResponse += part.message.content;   // 保存助手的回复
}

// 第二次对话，传递历史对话
const message2 = { role: 'user', content: '在这些景点中，哪个最适合春天去游玩？' };
const messages = [
    { role: 'user', content: '请问北京有哪些著名的旅游景点？' },
    { role: 'assistant', content: assistantResponse },  // 使用第一次的助手回复
    { role: 'user', content: '在这些景点中，哪个最适合春天去游玩？' }
];

const responseSecondRound = await ollama.chat({ model: 'deepseek-r1:1.5b_new', messages: messages, stream: true });

console.log("\n第二轮会话:");
for await (const part of responseSecondRound) {
    process.stdout.write(part.message.content);  // 输出第二次的响应内容
}

console.log();  // 换行
