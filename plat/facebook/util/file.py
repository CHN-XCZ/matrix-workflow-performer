import os
import random
import string


def generate_random_string(length=16):
    """生成指定长度的随机字符串"""
    letters = string.ascii_letters + string.digits  # 包含字母和数字
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string.upper()  # 转换为全大写


def save_string_to_file(filename, content):
    """将字符串内容保存到文件中"""
    with open(filename, 'w') as file:
        file.write(content)


def append_to_file(filename, text):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(text + '\n')


def read_string_from_file(filename):
    """从文件中读取字符串内容"""
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as file:
        return file.read().strip()