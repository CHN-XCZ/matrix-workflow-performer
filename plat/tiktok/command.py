import uiautomator2

from enums.tiktok_enums import OperateEnums
from loguru import logger
import uiautomator2 as u2

from plat.tiktok.intent import open_tiktok_user_home, open_tiktok_link, back_tiktok_home
from plat.tiktok.common import TIKTOK_RESOURCE_ID_MAP, restart_tiktok
from utils.clipboard import get_clipboard_text
from utils.image import os_push_image, clear_gallery
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
    restart_tiktok(d)
    if action_type == OperateEnums.POST:
        logger.info(f"Performing Concern...")
        # return open_new_post(device, img_url, title, content)
        return open_new_post(device.serial, img_url, content, title)
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
    

def open_new_post(device_serial, media_url,content_text,title=None):
    d = u2.connect(device_serial)
    in_home = back_tiktok_home(device=d, timeout=20)
    file_path = extract_filename_from_url(media_url)
    try:
        if in_home:
            post_button = d(resourceId=TIKTOK_RESOURCE_ID_MAP["home_post_button"])
            gallery_button = d(resourceId="com.zhiliaoapp.musically:id/fnu")

            post_button.click_exists(timeout=10)

            # TODO 根据media_url下载资源
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
            if title:
                title_area = d(resourceId='com.zhiliaoapp.musically:id/en_')
                if title_area.wait(10):
                    title_area.send_keys(title)
                else:
                    logger.warning("[TIKTOK POST] post error: title area not found")
            d(resourceId='com.zhiliaoapp.musically:id/n_x').click_exists(timeout=10)
            try:
                if d(resourceId='com.zhiliaoapp.musically:id/pbn').click_exists(timeout=20):
                    logger.info("[TIKTOK POST] Post Successfully")
                    d(resourceId='com.zhiliaoapp.musically:id/pb6',text='复制链接').click_exists(timeout=10)
                    post_link = get_clipboard_text(d)
                    return post_link
                else:
                    return ""
            except Exception as e:
                logger.error("[TIKTOK POST] Post Failed: {}".format(e))
                return ""
    except Exception as e:
        logger.error("[TIKTOK POST] Post Failed: {}".format(e))
        raise e
    # finally:
    #     clear_gallery(device_serial, file_path="*")

        # d(resourceId='com.zhiliaoapp.musically:id/na0').click_exists(timeout=10)
    logger.info("[TIKTOK POST] Post Failed")
    raise Exception("[TIKTOK POST] Post Failed")





if __name__ == '__main__':
    d = uiautomator2.connect()
    open_new_post(d,"https://pica.zhimg.com/v2-93a9c0544f7157ddd0b7ef52bcad358d_xl.jpg?source=32738c0c&needBackground=1","111")

        
        

    

    