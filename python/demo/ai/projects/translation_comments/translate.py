# translate.py
import os
from openai import OpenAI
from comments import extract_comments, generate_prompts  # 引用 comments.py 文件
import datetime
def load_config(config_file="config.txt"):
    """
    从配置文件中加载 base_url, api_key 和 model。

    Args:
        config_file (str): 配置文件路径，默认为 config.txt。

    Returns:
        dict: 包含 base_url, api_key, model 的字典。如果配置文件不存在或读取失败，返回 None。
    """
    config = {}
    if not os.path.exists(config_file):
        print(f"错误: 配置文件 '{config_file}' 不存在。")
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except Exception as e:
        print(f"读取配置文件错误: {e}")
        return None

    required_keys = ["base_url", "api_key", "model"]
    for key in required_keys:
        if key not in config:
            print(f"错误: 配置文件缺少必要的配置项: '{key}'。")
            return None

    return config

def translate_comments(comments, lang, config):
    """
    使用 OpenAI API 翻译注释列表中的每段注释。

    Args:
        comments (list): extract_comments 函数返回的注释对象列表。
        lang (str): 目标语言的英文缩写。
        config (dict): 包含 OpenAI API 配置信息的字典 (base_url, api_key, model)。

    Returns:
        list:  翻译后的注释对象列表，comment 字段的内容已被替换为翻译后的文本。
                 如果翻译过程中出现错误，则返回原始的 comments 列表，并在控制台输出错误信息。
    """
    client = OpenAI(
        base_url=config['base_url'],
        api_key=config['api_key'],
    )
    model = config['model']

    translated_comments = []
    prompts = generate_prompts(comments, lang) # 生成 prompt 列表

    if len(comments) != len(prompts):
        print("错误: 注释列表和 prompt 列表长度不一致，无法进行翻译。")
        return comments # 返回原始 comments，不进行翻译

    for i, comment_obj in enumerate(comments):
        prompt_content = prompts[i] # 获取对应的 prompt
        print("翻译 prompt: ", prompt_content)
        try:
            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_content}
                ],
                stream=False
            )
            translated_text = chat_completion.choices[0].message.content
            print("<",translated_text,">")
            if translated_text:
                comment_obj['comment'] = translated_text.strip() # 更新 comment 字段为翻译后的文本
                translated_comments.append(comment_obj) # 添加到新的列表
            else:
                print(f"警告: 注释序号 {i} 翻译结果为空，使用原始注释。")
                translated_comments.append(comment_obj) # 翻译为空，使用原始注释
        except Exception as e:
            print(f"翻译注释序号 {i} 出错: {e}")
            translated_comments.append(comment_obj) # 翻译出错，使用原始注释

    return translated_comments

def replace_comments_in_code(file_path, translated_comments):
    """
    将翻译后的注释替换回源代码文件内容中。

    Args:
        file_path (str): 源代码文件路径。
        translated_comments (list): 翻译后的注释对象列表，包含 'comment', 'start', 'end' 字段。

    Returns:
        str:  替换注释后的源代码文件内容。
              如果文件读取失败，返回 None。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"文件读取错误: {e}")
        return None

    modified_code_content = code_content # 初始值

    offset = 0 # 偏移量，用于处理注释长度变化

    for comment_obj in translated_comments:
        start = comment_obj['start'] + offset # 应用偏移量
        end = comment_obj['end'] + offset   # 应用偏移量
        translated_comment = comment_obj['comment']

        modified_code_content = modified_code_content[:start] + translated_comment + modified_code_content[end:]

        offset += len(translated_comment) - (end - start) # 更新偏移量

    return modified_code_content

if __name__ == '__main__':
    config = load_config() # 加载配置文件
    if not config:
        print("程序配置加载失败，请检查 config.txt 文件。")
    else:
        file_path = "/System/Volumes/Data/MyStudio/resources_books/deepseek_books/src/ollama_lib/python/aa.py" # 替换为你的代码文件路径
        language_code = "英文"  # 目标语言代码，例如 "zh" 代表中文

        comments = extract_comments(file_path) # 从 comments.py 中调用 extract_comments
        if comments:
            translated_comments = translate_comments(comments, language_code, config) # 调用翻译函数
            
            if translated_comments:
                modified_code = replace_comments_in_code(file_path, translated_comments) # 调用代码替换函数
                print(modified_code)


            else:
                print("\n注释翻译失败，请检查错误信息。")
        else:
            print("\n未能提取到任何注释。")
