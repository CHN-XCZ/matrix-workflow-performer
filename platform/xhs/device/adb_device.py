import os
import platform
import subprocess
from loguru import logger
import uiautomator2 as u2

def get_adb_path():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. 优先在当前目录的平级目录中查找
    adb_dir = os.path.join(current_dir, 'adb')
    if not os.path.exists(adb_dir):  # 如果当前平级目录没有 adb
        # 2. 回退到项目根目录查找
        project_root = os.path.dirname(current_dir)
        project_root = os.path.dirname(project_root)
        project_root = os.path.dirname(project_root)
        adb_dir = os.path.join(project_root, 'adb')

    # 3. 根据系统构建 adb 路径
    system = platform.system().lower()
    if 'windows' in system:
        adb_path = os.path.join(adb_dir, 'windows', 'adb.exe')
    elif 'darwin' in system:
        adb_path = os.path.join(adb_dir, 'mac', 'adb')
    elif 'linux' in system:
        adb_path = os.path.join(adb_dir, 'linux', 'adb')
    else:
        adb_path = None

    # 4. 检查路径是否存在
    if adb_path and os.path.exists(adb_path):
        return adb_path
    else:
        raise FileNotFoundError("ADB executable not found in expected paths.")

# 获取已连接的设备列表
def get_connected_devices(path):
    try:
        # 获取 adb 路径（假设 adb 存放在项目的 'adb/' 文件夹下）
        # adb_path = os.path.join(os.path.dirname(__file__), 'adb', 'adb.exe')

        # 确保 adb 设备命令能正常运行
        result = subprocess.run([path, 'devices'], stdout=subprocess.PIPE, text=True)
        # logger.info(result.stdout)
        lines = result.stdout.strip().split("\n")
        ds = [line.split()[0] for line in lines[1:] if "device" in line]
        return ds
    except FileNotFoundError:
        logger.error("adb command not found. Please ensure adb is included in the package.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def adb_connect_device(serial):
    try:
        device = u2.connect(serial)
        device.set_orientation("n")  # 强制横屏
        return device
    except u2.ConnectError as e:
        raise Exception(e)