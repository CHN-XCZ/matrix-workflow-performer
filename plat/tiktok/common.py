from uiautomator2 import Device
import time
from loguru import logger

TIKTOK_APP_NAME = "com.zhiliaoapp.musically"

TIKTOK_RESOURCE_ID_MAP = {
    "home_post_button": "com.zhiliaoapp.musically:id/k0k"
}

def restart_tiktok(d:Device):
    """
    重启tiktok应用。

    :param d: uiautomator2连接的设备对象
    """
    try:
        # 启动 xhs 应用
        d.app_stop("TIKTOK_APP_NAME")
        time.sleep(1)
        d.app_start("TIKTOK_APP_NAME")
        # logger.warning("xhs应用已启动")
        d.set_orientation("n")  # 设置为自然方向（竖屏）
        time.sleep(5)
    except Exception as e:
        logger.exception(f"启动tiktok应用时发生错误: {e}")
        raise e