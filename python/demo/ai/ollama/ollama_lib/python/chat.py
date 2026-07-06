from ollama import generate
from ollama import chat
# 使用 generate 函数进行单轮会话，并使用流式输出

single_round_question = "天空为什么是蓝色的？"
response_single_round = generate(model='deepseek-r1:1.5b_new',prompt=single_round_question, stream=True)

# 逐步输出流式响应
print("Single Round Response:")
for part in response_single_round:
    print(part['response'], end='')


# --------------------------- 多轮会话 ---------------------------
# 第一次对话
message1 = {'role': 'user', 'content': '请问北京有哪些著名的旅游景点？'}
response_first_round = chat(model='deepseek-r1:8b', messages=[message1], stream=True)

# 输出第一次的响应
print("第一轮会话:")
assistant_response = ''
for part in response_first_round:
    print(part['message']['content'], end='')
    assistant_response += part['message']['content']



# 第二次对话，传递历史对话
message2 = {'role': 'user', 'content': 'What is the weather like in Paris?'}
messages = [    
    {'role': 'user', 'content': '请问北京有哪些著名的旅游景点？'},
    {'role': 'assistant', 'content': assistant_response},  # 使用第一次的助手回复
    {'role': 'user', 'content': '在这些景点中，哪个最适合春天去游玩？'}
]

response_second_round = chat(model='deepseek-r1:1.5b_new', messages=messages, stream=True)

# 输出第二次的响应
print("\n第二轮会话:", end=" ")
for part in response_second_round:
    print(part['message']['content'], end='')

print()  # 换行


