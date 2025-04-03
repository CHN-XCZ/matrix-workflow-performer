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
        time.sleep(5)
    except Exception as e:
        logger.exception(f"启动xhs应用时发生错误: {e}")
        raise e

def is_element_within_bounds(element, target_bounds):
    """
    检查元素是否在指定目标区域内。

    :param element: 要检查的 uiautomator2 元素对象
    :param target_bounds: 目标区域的 (left, top, right, bottom) 坐标
    :return: 如果元素在目标区域内返回 True，否则返回 False
    """
    element_bounds = get_element_bounds(element)
    if not element_bounds or not target_bounds:
        return False

    el_left, el_top, el_right, el_bottom = element_bounds
    target_left, target_top, target_right, target_bottom = target_bounds

    # 判断元素是否完全在目标区域内
    return (
            el_left >= target_left and el_top >= target_top and
            el_right <= target_right and el_bottom <= target_bottom
    )


def get_element_bounds(element):
    """
    获取元素的坐标边界。

    :param element: uiautomator2 元素对象
    :return: 元素的 (left, top, right, bottom) 坐标
    """
    bounds = element.info.get("bounds")
    if bounds:
        return bounds["left"], bounds["top"], bounds["right"], bounds["bottom"]
    return None