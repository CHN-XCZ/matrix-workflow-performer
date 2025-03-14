import io
import os
import subprocess
from urllib.parse import urlparse

import requests
import uiautomator2
from loguru import logger


def extract_filename_from_url(url):
    # 使用 urlparse 从 URL 中提取路径
    parsed_url = urlparse(url)
    # 使用 os.path.basename 获取路径中的文件名
    filename = os.path.basename(parsed_url.path)
    return filename

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
            device.push(image_data, f"/sdcard/DCIM/Screenshots/{file_path}")
            logger.info(f"图片已推送到设备 {device.serial} 的相册目录")

            # 刷新设备媒体库
            device.shell(
                f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "
                f"file:///sdcard/DCIM/Screenshots/{file_path}"
            )
            logger.info(f"设备 {device.serial} 的媒体库已刷新")
            return True
        else:
            logger.error("图片下载失败")
            return False
    except Exception as e:
        logger.exception(f"处理设备 {device.serial} 时发生错误: {e}")

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

def clear_camera_cache():
    # 目标目录
    camera_dir = "/sdcard/DCIM/Screenshots/"

    # 获取目录下所有文件的命令
    list_files_cmd = f'adb shell ls {camera_dir}'

    # 执行命令并获取输出
    result = subprocess.run(list_files_cmd, shell=True, capture_output=True, text=True)
    files = result.stdout.strip().split('\n')

    # 过滤掉非文件项（例如目录名）
    # 注意：这个过滤可能不完美，具体取决于ls命令的输出和文件系统的实际情况
    # files = [f for f in files if not f.endswith('/')]

    # 删除文件的命令模板
    delete_file_cmd_template = 'adb shell rm {}'

    # 逐一删除文件
    for file in files:
        if file == "":
            continue
        file_path = f'{camera_dir}{file}'
        delete_cmd = delete_file_cmd_template.format(file_path)
        try:
            subprocess.run(delete_cmd, shell=True, check=True)
            logger.info(f'Successfully deleted {file_path}')
        except subprocess.CalledProcessError as e:
            logger.info(f'Failed to delete {file_path}: {e}')


if __name__ == '__main__':
    # device = uiautomator2.connect()
    clear_camera_cache()
