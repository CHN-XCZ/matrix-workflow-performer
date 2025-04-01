import subprocess
from concurrent.futures import ThreadPoolExecutor

from plat.xhs.device.adb_device import get_connected_devices, get_adb_path

app_path = "D:\\work\\matrix-workflow-performer\\apps\\xhs.apk"
task_executor = ThreadPoolExecutor(max_workers=100)


def install_app(device_id):
    try:
        print(f"installing to {device_id}")
        command = f"adb -s {device_id} install {app_path}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"{device_id}: {result.stdout}")
        print(f"{device_id}: {result.returncode}")
    except Exception as e:
        print(f"{device_id}: install failed {str(e)}")


if __name__ == '__main__':
    adb_path = get_adb_path()
    devices = get_connected_devices(adb_path)
    if not devices:
        print("no devices found")
        exit(1)
    for device_id in devices:
        task_executor.submit(install_app, device_id)
