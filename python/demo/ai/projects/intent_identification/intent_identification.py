
import inspect
import json
from typing import get_type_hints
from functools import wraps
from openai import OpenAI

def map_python_to_openai_type(python_type): 
    """映射 Python 数据类型到 OpenAI API 类型。"""
    if python_type is str:
        return "string"
    elif python_type is int:
        return "integer"
    elif python_type is float:
        return "number"
    elif python_type is bool:
        return "boolean"
    elif python_type is dict:
          return "object"
    elif python_type is list:
          return "array"        
    #Add other python types here if needed
    else:
        
        return "string" #Default to string
        # raise ValueError(f"Unsupported Python type: {python_type}")

def openai_function(description, required_params=None, param_descriptions=None):
    """
    装饰器，用于定义 OpenAI 函数调用的相关信息。
    """
    def decorator(func):
        @wraps(func)  # 使用 functools.wraps
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.openai_function_info = {
            "name": func.__name__,
            "description": description,
            "required": required_params or [],
            "param_descriptions": param_descriptions or {},
        }
        return wrapper
    return decorator

class IntentIdentification:
    default_api_key = "default_api_key"

    def __init__(self, base_url, api_key=default_api_key, model="qwen2.5:0.5b"):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self._user_functions = None
    
    def set_functions(self, user_functions):
        self._user_functions = user_functions
    
    def get_openai_tools(self):
        tools = []
        
        #获取用户定义的函数
        if self._user_functions:
           for name, method in inspect.getmembers(self._user_functions, predicate=inspect.ismethod):
            if hasattr(method, "openai_function_info"):
                func_info = method.openai_function_info
                parameters = {
                    "type": "object",
                    "properties": {}
                }
                type_hints = get_type_hints(method)
                sig = inspect.signature(method)

                for param_name, param in sig.parameters.items():
                    if param_name != 'self':
                        python_type = type_hints.get(param_name)
                        openai_type = map_python_to_openai_type(python_type)
                        parameters["properties"][param_name] = {
                            "type": openai_type,
                            "description": func_info["param_descriptions"].get(param_name, ""),
                        }

                tools.append({
                    "type": "function",
                    "function": {
                        "name": func_info["name"],
                        "description": func_info["description"],
                        "parameters": parameters,
                        "required": func_info["required"],
                    },
                })
        return tools

    def identify(self, prompt, model=None):
        tools = self.get_openai_tools()
        use_model = model if model else self.model  # 选择模型

        chat_completion = self.client.chat.completions.create(
            model=use_model,  # 使用选定的模型
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="auto",
            stream=False
        )

        message = chat_completion.choices[0].message
        tool_calls = message.tool_calls

        if tool_calls:
            results = []
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                func = getattr(self._user_functions, func_name)
                # 使用关键字参数调用函数
                result = func(**arguments)
                results.append(result)
            return results
        else:
            return []