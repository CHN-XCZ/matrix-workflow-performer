import uiautomator2

from enums.tiktok_enums import OperateEnums
from loguru import logger
import uiautomator2 as u2

from plat.tiktok.intent import open_tiktok_user_home, open_tiktok_link, back_tiktok_home
from plat.tiktok.common import TIKTOK_RESOURCE_ID_MAP, restart_tiktok
from utils.image import os_push_image
from utils.str import extract_filename_from_url


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
    

def open_new_post(device_serial, media_url,content_text):
    d = u2.connect(device_serial)
    restart_tiktok(d)
    in_home = back_tiktok_home(device=d, timeout=20)

    if in_home:
        post_button = d(resourceId=TIKTOK_RESOURCE_ID_MAP["home_post_button"])
        gallery_button = d(resourceId="com.zhiliaoapp.musically:id/fnu")

        post_button.click_exists(timeout=10)

        # TODO 根据media_url下载资源
        file_path = extract_filename_from_url(media_url)
        os_push_image(d,media_url,file_path)

        gallery_button.click_exists(timeout=10)
        medias = d(resourceId='com.zhiliaoapp.musically:id/fnv')[0]
        medias.click_exists(timeout=10)

        # 点击下一步
        d(resourceId='com.zhiliaoapp.musically:id/qs4').click_exists(timeout=10)
        d(resourceId='com.zhiliaoapp.musically:id/l1k').click_exists(timeout=10)
        text_area = d(resourceId='com.zhiliaoapp.musically:id/en9')
        if text_area.wait(10):
            text_area.send_keys(content_text)
        else:
            logger.error("[TIKTOK POST] post error: content area not found")
            raise Exception("[TIKTOK POST] post error: content area not found")
        d(resourceId='com.zhiliaoapp.musically:id/n_x').click_exists(timeout=10)
        # d(resourceId='com.zhiliaoapp.musically:id/na0').click_exists(timeout=10)
        return True
    else:
        return False





if __name__ == '__main__':
    d = uiautomator2.connect()
    open_new_post(d,"https://pica.zhimg.com/v2-93a9c0544f7157ddd0b7ef52bcad358d_xl.jpg?source=32738c0c&needBackground=1","111")

        
        

    

    