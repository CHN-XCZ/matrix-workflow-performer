import requests
import uiautomator2 as u2
from loguru import logger
def open_xhs_link(url, device):
    content_id = get_content_id(url)
    d = u2.connect(device)
    d.app_start("com.xingin.xhs")
    d.shell(f'am start -a android.intent.action.VIEW -d "xhsdiscover://item/{content_id}"')

def open_xhs_user_home(device, user_id):
    d = u2.connect(device)
    d.app_start("com.xingin.xhs")
    d.shell(f'am start -a android.intent.action.VIEW -d "xhsdiscover://user/{user_id}"')

def get_content_id(url):
    if url.startswith("http://xhslink.com"):
        response = requests.get(url)
        if response.status_code != 200:
            logger.error('请求失败', url)
        # /discovery/item/6794a1a70000000018009196?app_platform=android&ignoreEngage=true&app_version=8.68.5&share_from_user_hidden=true&xsec_source=app_share&type=normal&xsec_token=CBV0fgKLBwgk1rADnzp3nu1Lr_pvC6BoBMztPWef17Kl0=&author_share=1&xhsshare=CopyLink&shareRedId=OD06NEc-Nj02NzUyOTgwNjY7OTpHPExM&apptime=1739260530&share_id=2a2d800802d4452e86171ff8f33f9b04
        content_id = response.request.path_url.split("?")[0].split("/discovery/item/")[1]
    else:
        content_id = url
    return content_id

def open_xhs_post(device):
    d = u2.connect(device)
    d.app_start("com.xingin.xhs")
    d.shell(f'am start -a android.intent.action.VIEW -d "xhsdiscover://home"')


if __name__ == '__main__':
    open_xhs_link("67c81f10000000002903e864")