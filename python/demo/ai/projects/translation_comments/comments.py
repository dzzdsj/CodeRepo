import os

def extract_comments(path):
    """
    提取指定路径源代码文件中的所有注释，并记录注释文本的起始和结束位置。

    支持的编程语言: Python, Java, JavaScript, C++, Go
    考虑单行注释和多行注释。

    Args:
        path (str): 源代码文件路径。

    Returns:
        list: 一个包含注释对象的数组。每个对象包含:
            - comment (str): 注释文本 (去除注释标记)。
            - start (int): 注释在文件中的起始位置 (字符索引)。
            - end (int): 注释在文件中的结束位置 (字符索引)。
            如果文件读取失败或不支持的语言，返回 None。
    """
    if not os.path.isfile(path):
        print(f"错误: 文件路径 '{path}' 无效。")
        return None

    language = get_language_from_path(path)
    if not language:
        print(f"错误: 不支持的文件类型: '{path}'。")
        return None

    try:
        with open(path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        print(f"文件读取错误: {e}")
        return None

    comments = []
    if language == 'python':
        comments = extract_comments_python(code_content)
    elif language in ['java', 'javascript', 'cpp', 'go']:
        comments = extract_comments_c_style(code_content, language) # C-style 注释处理 (Java, JavaScript, C++, Go)

    return comments

def get_language_from_path(path):
    """
    根据文件路径的文件扩展名判断编程语言类型。

    Args:
        path (str): 文件路径。

    Returns:
        str: 编程语言类型 (python, java, javascript, cpp, go)，如果不支持则返回 None。
    """
    _, file_extension = os.path.splitext(path)
    file_extension = file_extension.lower()
    if file_extension == '.py':
        return 'python'
    elif file_extension == '.java':
        return 'java'
    elif file_extension == '.js':
        return 'javascript'
    elif file_extension == '.cpp' or file_extension == '.c' or file_extension == '.h': # 考虑 .c 和 .h 文件
        return 'cpp'
    elif file_extension == '.go':
        return 'go'
    return None

def extract_comments_python(code_content):
    """
    提取 Python 代码中的注释。

    Args:
        code_content (str): Python 源代码字符串。

    Returns:
        list: 包含 Python 注释对象的列表。
    """
    comments = []
    lines = code_content.splitlines()
    in_multiline_comment = False
    multiline_start_pos = -1

    for line_num, line in enumerate(lines):
        line_start_pos = sum(len(l) + 1 for l in lines[:line_num]) # 计算行起始位置的字符索引

        # 处理多行注释 (多行注释的 start 和 end 已经指向文本，不需要修改)
        if in_multiline_comment:
            if line.strip().endswith(("'''", '"""')):
                comment_text = code_content[multiline_start_pos: line_start_pos + line.rfind(line.strip().rstrip(("'''", '"""')))]
                comments.append({
                    "comment": comment_text.strip(),
                    "start": multiline_start_pos,
                    "end": line_start_pos + line.rfind(line.strip().rstrip(("'''", '"""')))
                })
                in_multiline_comment = False
            continue

        if line.strip().startswith(("'''", '"""')):
            multiline_start_pos = line_start_pos + line.find(line.strip().lstrip(("'''", '"""')))
            if not line.strip().endswith(("'''", '"""')):
                in_multiline_comment = True
            else:
                comment_text = line[line.find(line.strip().lstrip(("'''", '"""'))):line.rfind(line.strip().rstrip(("'''", '"""')))]
                comments.append({
                    "comment": comment_text.strip(),
                    "start": line_start_pos + line.find(line.strip().lstrip(("'''", '"""'))),
                    "end": line_start_pos + line.rfind(line.strip().rstrip(("'''", '"""')))
                })
            continue


        # 处理单行注释
        comment_start_index = line.find('#')
        if comment_start_index != -1:
            comment_text = line[comment_start_index + 1:] # 提取单行注释内容

            # **修改 start 位置计算，包含 '#' 后的所有空格**
            start_pos_comment_text = line_start_pos + comment_start_index + 1 #  Start after '#'
            # Find the index of the first non-space character after '#'
            first_non_space_index = 0
            for i, char in enumerate(comment_text):
                if not char.isspace():
                    first_non_space_index = i
                    break
            start_pos_comment_text += first_non_space_index # Move start to the first non-space character

            comments.append({
                "comment": comment_text[first_non_space_index:].strip(), # 注释文本去除 leading/trailing spaces
                "start": start_pos_comment_text, #  使用新的 start 位置
                "end": line_start_pos + len(line) # 单行注释结束位置为行尾
            })

    return comments
def extract_comments_c_style(code_content, language):
    """
    提取 C-style (Java, JavaScript, C++, Go) 代码中的注释 (单行 // 和多行 /* ... */)。

    Args:
        code_content (str): C-style 源代码字符串。
        language (str): 编程语言类型 (用于区分不同语言，虽然这里 C-style 注释语法相同)。

    Returns:
        list: 包含 C-style 注释对象的列表。
    """
    comments = []
    i = 0
    while i < len(code_content):
        if code_content[i:i+2] == '//': # 单行注释
            start_pos = i
            end_pos = code_content.find('\n', i)
            if end_pos == -1:
                end_pos = len(code_content)
            comment_text = code_content[start_pos+2:end_pos] # 注释文本从 // 之后开始

            # **Modified start position calculation for C-style single-line comments**
            start_pos_comment_text = start_pos + 2 # Start after '//'
            # Find the index of the first non-space character after '//'
            first_non_space_index = 0
            for index, char in enumerate(comment_text):
                if not char.isspace():
                    first_non_space_index = index
                    break
            start_pos_comment_text += first_non_space_index # Move start to the first non-space character

            comments.append({
                "comment": comment_text[first_non_space_index:].strip(), # 注释文本去除 leading/trailing spaces
                "start": start_pos_comment_text, # Use the new start position
                "end": end_pos
            })
            i = end_pos
        elif code_content[i:i+2] == '/*': # 多行注释
            start_pos = i
            end_pos = code_content.find('*/', i)
            if end_pos == -1:
                print("警告: 发现未闭合的多行注释，从位置", start_pos, "开始。")
                break
            comment_text = code_content[start_pos+2:end_pos] # 注释文本从 /* 之后开始
            comments.append({
                "comment": comment_text.strip(),
                "start": start_pos + 2,  # start 指向 /* 之后 (No change needed for multiline)
                "end": end_pos + 2
            })
            i = end_pos + 2
        else:
            i += 1

    return comments

def test_extract_comments(file_path, language):
    """
    测试 extract_comments 函数，直接使用文件路径。
    """
    if not os.path.exists(file_path):
        print(f"错误: 测试文件 '{file_path}' 不存在，请先创建示例代码文件。")
        return

    comments = extract_comments(file_path)
    print(f"\n{language.upper()} 代码注释提取结果 ({file_path}):")
    if comments:
        for comment_obj in comments:
            print(comment_obj)
    else:
        print("没有找到注释或文件处理出错。")

def generate_prompts(comments, lang):
    """
    根据提取的注释列表和目标语言，生成用于大模型翻译的 Prompt 列表。

    Args:
        comments (list): extract_comments 函数返回的注释对象列表。
        lang (str): 目标语言的英文缩写，例如 "zh" (中文), "en" (英文), "fr" (法文) 等。

    Returns:
        list: 包含 Prompt 字符串的列表，每个 Prompt 对应一个注释。
    """
    prompts = []
    prompt_header = f"将下面的文本翻译成【{lang}】:\n" # 修改 prompt header

    for comment_obj in comments:
        prompt_content = prompt_header + comment_obj['comment'] # 组合 prompt header 和 注释文本
        prompts.append(prompt_content) # 添加到 prompts 列表

    return prompts
if __name__ == '__main__':
    comments = extract_comments("/Users/dzzdsj/git/dzzdsj-git/github/CodeRepo/python/demo/ai/ollama/ollama_lib/python/chat.py")
    for comment in comments:
        print(comment)
    prompts = generate_prompts(comments, "英文")        
    for prompt in prompts:
        print(prompt)


    


   