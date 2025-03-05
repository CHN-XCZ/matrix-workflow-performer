from loguru import logger

from utils.clipboard import get_clipboard_text
import time
from utils.click import click_resource_timeout_button
import re

def copy_xhs_link(device):

    click_resource_timeout_button(device, "com.xingin.xhs:id/moreOperateIV", 'android.widget.Button')
    click_resource_timeout_button(device, "com.xingin.xhs:id/j_8", 'android.widget.TextView', btn_text='复制链接')
    time.sleep(1)
    xhs_link = get_clipboard_text(device)
    # 正则表达式提取链接
    link_pattern = r"http[s]?://[^\s，]+"

    links = re.findall(link_pattern, xhs_link)
    return links[0]


def restart_xhs(d):
    """
    重启xhs应用。

    :param d: uiautomator2连接的设备对象
    """
    try:
        # 启动 xhs 应用
        d.app_stop("com.xingin.xhs")
        time.sleep(1)
        d.app_start("com.xingin.xhs")
        # logger.warning("xhs应用已启动")
        d.set_orientation("n")  # 设置为自然方向（竖屏）
        time.sleep(3)
    except Exception as e:
        logger.exception(f"启动xhs应用时发生错误: {e}")