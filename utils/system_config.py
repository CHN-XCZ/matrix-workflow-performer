from dotenv import load_dotenv
import os
# 加载.env文件
load_dotenv()

def load_config():
    if not os.getenv("Authorization_KEY"):
        raise ValueError("Authorization_KEY is not set in .env file")
def get_config(key:str) -> str:
    return os.getenv(key)