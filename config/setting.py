import os

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if not ZHIPUAI_API_KEY:
    raise ValueError("ZHIPUAI_API_KEY 未设置，请检查 .env 文件或系统环境变量")