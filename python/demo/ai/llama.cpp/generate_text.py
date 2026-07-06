from llama_cpp import Llama

# 创建模型实例，加载本地 GGUF 文件
model = Llama(model_path="/System/Volumes/Data/models/deepseek/deepseek-r1/DeepSeek-R1-Distill-Qwen-7B-Q8_0.gguf", n_ctx=4096, n_threads=4)
# 设置提示词
prompt = "以梅花为题作一首诗"


# 生成流式文本
for chunk in model.create_completion(prompt, max_tokens=10000, temperature=0.7, top_p=0.9, stream=True):
    print(chunk['choices'][0]['text'], end='', flush=True)