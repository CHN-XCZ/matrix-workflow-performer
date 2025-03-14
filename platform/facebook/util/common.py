import subprocess
import time

import uiautomator2
from loguru import logger


def open_link(device, link):
    device.app_stop("com.facebook.katana")
    time.sleep(1)

    adb_command = f'adb shell am start -a android.intent.action.VIEW -d "{link}"'
    subprocess.run(adb_command, shell=True, check=True)
    # # 用 subprocess 打开推文链接
    # subprocess.run(
    #     ["adb", "-s", device.serial, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d",
    #      link])
    # apply_button = device(resourceId='com.vivo.browser:id/buttonDefaultPositive', text='允许')
    # if apply_button.wait(timeout=10) and apply_button.exists:
    #     apply_button.click()
    #     logger.info(f"点击允许按钮")
    logger.info(f"Opening Facebook: {link}")
    # 等待推文页面加载
    time.sleep(3)

def restart_app(device):
    logger.info(f"Restarting app")
    device.app_stop("com.facebook.katana")
    device.app_start("com.facebook.katana")
    time.sleep(3)

if __name__ == '__main__':
    device = uiautomator2.connect()
    open_link(device,"https://www.facebook.com/share/18kt7uggvH/")