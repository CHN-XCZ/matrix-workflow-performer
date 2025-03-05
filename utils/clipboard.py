import uiautomator2 as u2
from loguru import logger


def get_clipboard_text(device):
    """
    从设备剪贴板读取文本内容。

    参数:
        device: uiautomator2 的设备对象。

    返回:
        剪贴板中的文本内容（字符串）。
    """
    try:
        # 使用 adb shell 命令获取剪贴板内容
        stdout, exit_code = device.shell("am broadcast -a clipper.get")
        if exit_code == 0:  # 检查命令是否成功
            clipboard_text = device.clipboard
            # logger.info(f"剪贴板内容: {clipboard_text}")
            return clipboard_text.strip()
        else:
            logger.error(f"获取剪贴板失败，错误: {exit_code}")
            return None
    except Exception as e:
        logger.exception(f"获取剪贴板内容时出错: {e}")
        return None


# 示例用法
if __name__ == "__main__":
    d = u2.connect()  # 确保设备已连接
    clipboard_content = get_clipboard_text(d)
    logger.info(f"剪贴板中的文字: {clipboard_content}")
