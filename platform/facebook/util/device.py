import os
import platform
import subprocess
import time

from loguru import logger
import uiautomator2 as u2


# 获取 adb 路径
# def get_adb_path():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     system = platform.system().lower()
#     if 'windows' in system:
#         return os.path.join(base_dir, 'adb', 'windows', 'adb.exe')
#     if 'darwin' in system:
#         return os.path.join(base_dir, 'adb', 'mac', 'adb')
#     if 'linux' in system:
#         return os.path.join(base_dir, 'adb', 'linux', 'adb')
#     else:
#         return None


def get_adb_path():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. 优先在当前目录的平级目录中查找
    adb_dir = os.path.join(current_dir, 'adb')
    if not os.path.exists(adb_dir):  # 如果当前平级目录没有 adb
        # 2. 回退到项目根目录查找
        project_root = os.path.dirname(current_dir)
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


# 获取设备信息
def get_device_info(d):
    try:
        device_info = d.device_info
        result = {
            "serial": device_info["serial"],
            "sdk": device_info["sdk"],
            "brand": device_info["brand"],
            "model": device_info["model"],
            "arch": device_info["arch"],
            "version": device_info["version"]
        }
        return result
    except u2.UiObjectNotFoundError:
        pass


# 判断应用是否安装
def app_check(d, package_name):
    try:
        if package_name in d.app_list():
            return True
        else:
            return False
    except u2.UiObjectNotFoundError:
        pass


clash_package_name = 'com.github.kr328.clash'
telegram_package_name = 'org.telegram.messenger.web'
uiautomator_package_name = 'com.github.uiautomator'
truthsocial_package_name = 'com.truthsocial.android.app'
twitter_package_name = 'com.twitter.android'
twitterMy_package_name = 'com.tt.x'

# 判断设备是否准备好
def check_ready(d):
    try:
        result = get_device_info(d)
        telegram_check = app_check(d, telegram_package_name)
        if result is not None and result['serial'] != '' and telegram_check:
            return True
        else:
            return False
    except u2.UiObjectNotFoundError:
        pass


def check_package(d):
    try:
        app_list = d.app_list()
        if clash_package_name not in app_list:
            d.app_install('../apk/Clash-Android.apk')
        time.sleep(0.5)
        if telegram_package_name not in app_list:
            d.app_install('../apk/Telegram.apk')
        time.sleep(0.5)
        if uiautomator_package_name not in app_list:
            d.app_install('../apk/app-uiautomator.apk')
        time.sleep(0.5)
       # if truthsocial_package_name not in app_list:
            # truthSocial安装包路径
            # https://dw.uptodown.net/dwn/2swizlR4SlmfZh2VpWzCDmaWB2hhW8oy7GLDpLMwDNNLx1HuSBXUgIdZfg8QUeIci2GqPExvW9bj8pjf39ffD6AOmfigf3lBY2ToGnSH7ULDnDKqKKZ1sK0w8MtFaGNb/EpdgiJP18WGnMhkJPmucZc2ebxNLfUqRFsar5y-nlqhF-rcB9lH1FpQjCOIZKtWa6U2wwgbzVe08n1OSOMhILqG2_kgmlrY1jbdwAzOaOA9aspLlRP3MkPWhHlDv_KXb/y3uz3P1ywavgjWtl3BKTT2FSm4Soic7wCMEumFkuHkEMwGjNXGYJgVdRcN4qLaS6P1AemiB4Im8Qy8TnSQhnwA==/truth-social-1-11-2.apk
           # d.app_install('../apk/truthSocial.apk')
           # time.sleep(0.5)
        if twitter_package_name not in app_list and twitterMy_package_name not in app_list:
            d.app_install('../apk/Twitter.apk')
    except u2.UiObjectNotFoundError:
        pass


def app_wakeup(d):
    try:
        time.sleep(0.5)
        if not d.info['screenOn']:
            d.screen_on()

        time.sleep(0.5)
        lock_icon = d(resourceId='com.android.systemui:id/lock_icon')  # 针对特定手机 锁屏图标
        if lock_icon.exists():
            d.swipe(540, 1900, 540, 960, 0.1)

        time.sleep(0.5)
        d.shell("input keyevent 3")
        time.sleep(0.5)
        d.freeze_rotation()  # 锁定屏幕方向
    except u2.UiObjectNotFoundError:
        pass


def app_connect_wifi(d, account, password):
    try:
        is_connected = False
        wifi_status_result = d.shell(f"cmd wifi status")
        wifi_status_lines = wifi_status_result.output.split("\n")
        for line in wifi_status_lines:
            if "Wifi is connected to" in line:
                is_connected = True
                break

        if not is_connected:
            time.sleep(0.5)
            d.shell(f"cmd wifi connect-network {account} wpa2 {password}")
    except u2.UiObjectNotFoundError:
        pass


# 输入按键代码
# https://blog.csdn.net/qq78442761/article/details/139911910
def app_input_keycode(d, keycode):
    try:
        d.shell("input keyevent " + keycode)
    except u2.UiObjectNotFoundError:
        pass


def app_telegram_open(d):
    login_status = d.xpath("//android.widget.ImageButton[@content-desc='Search']")
    login_status_cn = d.xpath("//android.widget.ImageButton[@content-desc='搜索']")
    if not login_status.exists and not login_status_cn.exists:
        d.app_start(telegram_package_name)
        time.sleep(3)

    time.sleep(0.5)
    if d.orientation != "natural":
        d.orientation = "natural"  # 强制竖屏


# 设备操作状态，True 运行中，False 未运行
device_operate = {'serial': True}
device_login = {'serial': True}
api_result = {'code': 200, 'msg': 'success', 'data': None}
heartbeat_config = {'machine_id': '', 'devices': []}


def get_device_operate(serial):
    return device_operate[serial]


def set_device_operate(serial, operate):
    device_operate[serial] = operate
    update_heartbeat_config(serial, None, operate, None)


def get_device_login(serial):
    return device_login[serial]


def set_device_login(serial, login):
    device_login[serial] = login
    update_heartbeat_config(serial, None, None, login)


def update_heartbeat_config(serial, ready, operate, login):
    for device in heartbeat_config['devices']:
        if device['device_id'] == serial:
            if ready is not None:
                device['status_ready'] = ready
            if operate is not None:
                device['status_operate'] = operate
            if login is not None:
                device['is_login'] = login
