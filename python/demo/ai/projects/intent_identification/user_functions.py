from intent_identification import openai_function

class UserFunctions:
    @openai_function(
        description="当用户想要绘制图像时调用此函数",
        required_params=["image_description"],
        param_descriptions={
            "image_description": "绘制图像的详细描述,需要转换为英文，例如：a photo-realistic image of a cat wearing sunglasses",
        },
    )
    def draw_image(self, image_description: str):
        """绘制图像的函数。"""
        return {
            "type": "draw_image",
            "image_description": image_description
        }

    @openai_function(
        description="当用户要为指定路径下的文档(.txt或.docx）配置指定尺寸（width和height）的图像时调用此函数",
        required_params=["document_content"],
        param_descriptions={
            "path": "用户指定的需要配图的文档的文件路径",
            "width": "图像的宽度",
            "height": "图像的高度",
        },
    )
    def article_image(self, path: str, width:int = 512, height: int = 512):
        """为文章配图"""
        return {
            "type": "article_image",
            "path": path,
            "width" : width,
            "height": height
        }       
   

        

# 测试代码
if __name__ == "__main__":
    from intent_identification import IntentIdentification
    base_url = "http://localhost:11434/v1" #请替换成您的base_url
    api_key = "ollama"  #请替换成您的api_key

    intent_identifier = IntentIdentification(base_url, api_key)
    user_funcs = UserFunctions()
    intent_identifier.set_functions(user_funcs)

    prompt = "生成一个excel文档：数据：姓名,年龄,性别,城市\n张三,25,男,北京\n李四,30,女,上海"
    results = intent_identifier.identify(prompt,"qwen2.5:1.5b")
    print("<:",results)

    prompt = "画一只小狗在喝水，非常欢乐。"
    results = intent_identifier.identify(prompt)
    print("<:",results)

    prompt = "你叫什么名字"
    results = intent_identifier.identify(prompt)
    print("<:",results)

    prompt = r"将c:\Users\qwen\Desktop路径中的所有源代码文件中的注释翻译为德文"
    results = intent_identifier.identify(prompt,"qwen2.5:1.5b")
    print("<:",results)