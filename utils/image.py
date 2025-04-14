import io
import subprocess

import requests
import uiautomator2
from loguru import logger
import time

from utils.str import extract_filename_from_url


def os_push_image(device, url, file_path):
    """
    从指定 URL 下载图片并推送到设备的相册目录，不保存到本地。

    参数:
    - device: uiautomator2 设备对象
    - url: 图片下载链接
    """
    try:
        # 下载图片到内存
        response = requests.get(url)
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            logger.info("图片已成功下载到内存中")

            # 使用 uiautomator2 的 push 方法直接传输内存中的文件
            device.push(image_data, f"/sdcard/DCIM/Camera/{file_path}")
            logger.info(f"图片已推送到设备 {device.serial} 的相册目录")

            # 刷新设备媒体库
            device.shell(
                f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "
                f"file:///sdcard/DCIM/Camera/{file_path}"
            )
            logger.info(f"设备 {device.serial} 的媒体库已刷新")
            return True
        else:
            logger.error("图片下载失败")
            return False
    except Exception as e:
        logger.exception(f"处理设备 {device.serial} 时发生错误: {e}")

# 清除保存的文件
def clear_gallery(serial, file_path = "*.jpg"):
    # 相册文件通常存储在 /sdcard/DCIM/Camera/ 目录下
    gallery_path = "/sdcard/DCIM/Camera/"+file_path
    adb_path = get_adb_path()
    # 构造 adb shell 命令来删除相册中的文件
    command = f"{adb_path} -s {serial} shell rm -r {gallery_path}"

    # 执行命令
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 检查命令执行结果
    if result.returncode == 0:
        logger.info(f"设备：{serial}:相册已清空")
    else:
        logger.warning(f"设备：{serial} 清空相册失败: {result.stderr}")

def select_image_in_gallery(device):
    """
    定位并点击相册中的最新图片。

    参数:
        device: uiautomator2 连接的设备对象。
    """

    # 定位到相册的网格布局
    gallery_grid = device(resourceId="com.xingin.xhs:id/brd")
    if gallery_grid.wait(timeout=30):
        # 获取网格中的第一个 FrameLayout 并点击
        first_image = device(resourceId="com.xingin.xhs:id/dr9")[0]
        if first_image.exists:
            first_image.click()
        else:
            logger.warning("未找到图片")
    else:
        logger.warning("未打开相册")

if __name__ == '__main__':
    d = uiautomator2.connect()
    file_path = extract_filename_from_url('https://pica.zhimg.com/v2-93a9c0544f7157ddd0b7ef52bcad358d_xl.jpg?source=32738c0c&needBackground=1')
    os_push_image(d,"https://pica.zhimg.com/v2-93a9c0544f7157ddd0b7ef52bcad358d_xl.jpg?source=32738c0c&needBackground=1",file_path)
