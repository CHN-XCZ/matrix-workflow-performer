from enums.tiktok_enums import OperateEnums
from loguru import logger
import uiautomator2 as u2

from plat.tiktok.intent import open_tiktok_user_home, open_tiktok_link, back_tiktok_home
from plat.tiktok.common import TIKTOK_RESOURCE_ID_MAP


def operate_tiktok_link(device, tweet_url, img_url, title=None, action_type=None, content=None):
    """
    打开指定的推文链接，并执行相应的操作（转发、评论、点赞）。

    参数:
    tweet_url (str): 推文的链接（例如 "https://x.com/elonmusk/status/1856530955709587762"）
    action_type (int): 操作类型：
        1 - 转发
        2 - 关注
        3 - 评论
        4 - 点赞
    """
    # time.sleep(3)
    # 根据操作类型执行不同的动作
    
    if action_type == OperateEnums.POST:
        logger.info(f"Performing Concern...")
        # return open_new_post(device, img_url, title, content)
        open_new_post(device.serial, img_url, content)
        return True
    elif action_type == OperateEnums.REPLY:
        logger.info(f"Performing Comment...{content}")
        return True

    elif action_type == OperateEnums.LIKE:
        logger.info("Performing Like...")
        # open_tiktok_link(tweet_url, device.serial)
        return True
    elif action_type == OperateEnums.FOLLOW:
        logger.info("Performing Follow...")
        # open_tiktok_user_home(device.serial, tweet_url)
        return True
    elif action_type == OperateEnums.COLLECT:
        logger.info("Performing COLLECT...")
        return True
    else:
        logger.warning("Invalid action type. Please use 0 for POST,1 for REPLY, 2 for LIKE, 3 for FOLLOW, or 4 for COLLECT")
        raise ValueError("Invalid action type. Please use 0 for POST,1 for REPLY, 2 for LIKE, 3 for FOLLOW, or 4 for COLLECT")
    

def open_new_post(device_serial, media_url, content_text):
    d = u2.connect(device_serial)

    in_home = back_tiktok_home(device=d, timeout=20)

    if in_home:
        post_button = d(resourceId=TIKTOK_RESOURCE_ID_MAP["home_post_button"])
        gallery_button = d(resourceId="com.zhiliaoapp.musically:id/fnu")

        post_button.click_exists(timeout=10)
        gallery_button.click_exists(timeout=10)

        
        

    

    