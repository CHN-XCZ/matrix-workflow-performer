import time

from loguru import logger


def go_back(device):
    try:
        device(resourceId='com.android.systemui:id/back').click()
    except Exception as e:
        logger.error(f"点击返回键时发生错误: {e}")


def swipe_screen(device, direction="up", duration=0.5):
    """滑动屏幕一页
    :param direction: 滑动方向 up/down/left/right
    :param duration: 滑动持续时间（秒）
    """
    width, height = device.window_size()
    if direction == "up":
        device.swipe(0.5*width, 0.8*height, 0.5*width, 0.2*height, duration)
    elif direction == "down":
        device.swipe(0.5*width, 0.2*height, 0.5*width, 0.8*height, duration)
    elif direction == "left":
        device.swipe(0.8*width, 0.5*height, 0.2*width, 0.5*height, duration)
    elif direction == "right":
        device.swipe(0.2*width, 0.5*height, 0.8*width, 0.5*height, duration)
    time.sleep(1)