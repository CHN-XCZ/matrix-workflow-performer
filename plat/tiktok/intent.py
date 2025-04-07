import uiautomator2 as u2
import requests
# import time
from loguru import logger
from uiautomator2 import Device
from plat.tiktok.common import TIKTOK_RESOURCE_ID_MAP


def get_content_id(url):
    if url.startswith("https://www.tiktok.com/t") or url.startswith("https://tiktok.com/t"):
        response = requests.get(url)
        if response.status_code != 200:
            logger.error('请求失败', url)
        # /discovery/item/6794a1a70000000018009196?app_platform=android&ignoreEngage=true&app_version=8.68.5&share_from_user_hidden=true&xsec_source=app_share&type=normal&xsec_token=CBV0fgKLBwgk1rADnzp3nu1Lr_pvC6BoBMztPWef17Kl0=&author_share=1&xhsshare=CopyLink&shareRedId=OD06NEc-Nj02NzUyOTgwNjY7OTpHPExM&apptime=1739260530&share_id=2a2d800802d4452e86171ff8f33f9b04
        content_id = response.request.path_url.split("?")[0].split("/video/")[1]
    else:
        content_id = url
    return content_id

def open_tiktok_user_home(device, user_id):
    d = u2.connect(device)
    # d.app_start("com.zhiliaoapp.musically")
    d.shell(f'am start -a android.intent.action.VIEW -d "snssdk1233://user/profile/{user_id}"')

def open_tiktok_link(url, device):
    content_id = get_content_id(url)
    d = u2.connect(device)
    # d.app_start("com.xingin.xhs")
    d.shell(f'am start -a android.intent.action.VIEW -d "snssdk1233://aweme/detail/{content_id}"')

def back_tiktok_home(device:Device, timeout:int=0) -> bool:
    # start_time = time.time()
    device.shell(f'am start -a android.intent.action.VIEW -d "snssdk1233://feed"')

    post_button = device(resourceId=TIKTOK_RESOURCE_ID_MAP["home_post_button"])

    return post_button.wait(timeout=timeout)
    # while time.time() - start_time < timeout:

