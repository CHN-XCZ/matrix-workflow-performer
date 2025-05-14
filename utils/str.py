import os
import re
from urllib.parse import urlparse


def is_prefix_matching(str1, str2, keyword="Received at"):
    # 找到 "Received at" 前面的部分
    prefix1 = str1.split(keyword)[0].strip()
    prefix2 = str2.split(keyword)[0].strip()

    # 判断前面的部分是否匹配
    return prefix1 == prefix2


def extract_message_info(message):
    """
    根据换行符分隔信息并提取用户名、消息内容和接收时间
    """
    lines = message.splitlines()

    if len(lines) >= 3:
        message_username = lines[0].strip()
        message_text = lines[1].strip()
        received_time = lines[2].replace("Received at", "").strip()

        return {
            "message_username": message_username,
            "message_text": message_text,
            "received_time": received_time
        }
    else:
        # print("信息格式不正确")
        return None

# 示例使用
# res_message = """James
# hi
# Received at 18:43"""
#
# info = extract_message_info(res_message)
#
# if info:
#     print(f"Nickname: {info['nickname']}")
#     print(f"Message: {info['message_content']}")
#     print(f"Received time: {info['received_time']}")


def extract_filename_from_url(url):
    # 使用 urlparse 从 URL 中提取路径
    parsed_url = urlparse(url)
    # 使用 os.path.basename 获取路径中的文件名
    filename = os.path.basename(parsed_url.path)
    return filename


def extract_digits(phone_number):
    """
    从手机号中提取纯数字

    :param phone_number: 原始手机号字符串
    :return: 仅包含数字的字符串
    """
    # 使用正则表达式提取数字
    digits_only = re.sub(r'\D', '', phone_number)
    return digits_only
