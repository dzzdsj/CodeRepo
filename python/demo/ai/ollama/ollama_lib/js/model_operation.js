
import ollama from 'ollama';

// 1. 列出当前可用的所有模型
ollama.list().then(models => {
  console.log("Current models:", models);
}).catch(err => console.error('Error listing models:', err));

// 2. 显示模型 'deepseek-r1:1.5b' 的详细信息
ollama.show('deepseek-r1:1.5b').then(model_info => {
  console.log("Model deepseek-r1:1.5b details:", model_info);
}).catch(err => console.error('Error showing model details:', err));

// 3. 创建一个新模型 'new_model' 从 'deepseek-r1:1.5b' 基础上，设置系统指令
ollama.create({model: 'new_model', from_: 'deepseek-r1:1.5b', system: "You are Mario from Super Mario Bros."})
  .then(new_model => {
    console.log("New model created:", new_model);
  }).catch(err => console.error('Error creating new model:', err));

// 4. 将模型 'deepseek-r1:1.5b' 复制到 'deepseek-r1:1.5b_new'
ollama.copy('deepseek-r1:1.5b', 'deepseek-r1:1.5b_new')
  .then(copy_model => {
    console.log("Model 'deepseek-r1:1.5b' copied to 'deepseek-r1:1.5b_new':", copy_model);
  }).catch(err => console.error('Error copying model:', err));

// 5. 删除模型 'deepseek-r1:1.5b'
ollama.delete('deepseek-r1:1.5b')
  .then(delete_status => {
    console.log("Model 'deepseek-r1:1.5b' deleted:", delete_status);
  }).catch(err => console.error('Error deleting model:', err));

// 6. 拉取模型 'deepseek-r1:1.5b' 从远程仓库
ollama.pull('deepseek-r1:1.5b')
  .then(pull_status => {
    console.log("Model 'deepseek-r1:1.5b' pulled from remote:", pull_status);
  }).catch(err => console.error('Error pulling model:', err));

// 7. 显示当前运行中的模型状态
ollama.ps().then(running_status => {
  console.log("Running model status:", running_status);
}).catch(err => console.error('Error fetching running model status:', err));
