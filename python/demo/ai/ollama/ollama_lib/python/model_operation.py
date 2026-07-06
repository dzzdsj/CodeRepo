import ollama

# 1. 列出当前可用的所有模型
models = ollama.list()
print("Current models:", models)

# 2. 显示模型 'deepseek-r1:1.5b' 的详细信息
model_info = ollama.show('deepseek-r1:1.5b')
print("Model deepseek-r1:1.5b details:", model_info)

# 3. 创建一个新模型 'new_model' 从 'deepseek-r1:1.5b' 基础上，设置系统指令
new_model = ollama.create(model='new_model', from_='deepseek-r1:1.5b', system="You are Mario from Super Mario Bros.")
print("New model created:", new_model)

# 4. 将模型 'deepseek-r1:1.5b' 复制到 'deepseek-r1:1.5b_new'
copy_model = ollama.copy('deepseek-r1:1.5b', 'deepseek-r1:1.5b_new')
print("Model 'deepseek-r1:1.5b' copied to 'deepseek-r1:1.5b_new':", copy_model)

# 5. 删除模型 'deepseek-r1:1.5b'
delete_status = ollama.delete('deepseek-r1:1.5b')
print("Model 'deepseek-r1:1.5b' deleted:", delete_status)

# 6. 拉取模型 'deepseek-r1:1.5b' 从远程仓库
pull_status = ollama.pull('deepseek-r1:1.5b')
print("Model 'deepseek-r1:1.5b' pulled from remote:", pull_status)


# 7. 显示当前运行中的模型状态
running_status = ollama.ps()
print("Running model status:", running_status)
