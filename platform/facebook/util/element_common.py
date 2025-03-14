import subprocess

import uiautomator2
from loguru import logger


def click_by_Xpath(device, xpath:str, timeout=15.0):
    element = device.xpath(xpath).wait(timeout=timeout)
    if element:
        button = device.xpath(xpath).get()
        button.click()
    else:
        raise Exception("element not found")

def click_by_resourceId(device, resourceId: str, text=None, timeout=15.0):
    element = None
    if text is None:
        element = device(resourceId=resourceId)
    else:
        element = device(resourceId=resourceId, text=text)
    if element.wait(timeout=timeout):
        element.click()
    else:
        raise Exception("element not found")

def click_by_className(device, className: str, index=0, timeout=15.0):
    element = device(className=className)
    if element.wait(timeout=timeout):
        element[index].click()
    else:
        raise Exception("element not found")

def get_text_by_className(device, className: str, index=0):
    element = device(className=className)
    if element[index].exists():
        return element[index].get_text()
    else:
        raise Exception("element not found")

def check_element_exists_by_Xpath(device, xpath: str, timeout=3):
    element = device.xpath(xpath).wait(timeout=timeout)
    if element:
        return element
    else:
        return False

def paste_text_by_className(device, text, className: str):
    element = device(className=className)
    if element.exists():
        element.set_text(text)
    else:
        raise Exception("element not found")

def paste_text_by_bounds(device, text, x1, y1):
    try:
        # 发送空文本实现清除
        subprocess.run(f"adb -s {device.serial} shell am broadcast -a clipper.set -e text ''",
                       shell=True,
                       check=True)

        # 使用adb shell命令设置剪切板
        subprocess.run(f"adb -s {device.serial} shell am broadcast -a clipper.set -e text '{text}'",
                       shell=True,
                       check=True)
        device.long_click(x1, y1)
        click_by_resourceId(device, "android:id/floating_toolbar_menu_item_text", text="Paste", timeout=3)
    except Exception as e:
        logger.error(f"paste_text_by_bounds error: {e}")
        raise e

if __name__ == '__main__':
    device = uiautomator2.connect()
    paste_text_by_className(device, "test", "android.widget.EditText")