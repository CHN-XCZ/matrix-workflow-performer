import time

import uiautomator2 as u2
from loguru import logger

from plat.facebook.util.common import open_link, restart_app
from plat.facebook.util.element_common import click_by_Xpath, get_text_by_className, \
    check_element_exists_by_Xpath, paste_text_by_className
from plat.facebook.util.image import clear_camera_cache, extract_filename_from_url, os_push_image


# 获取个人信息
def get_profile_username(device):
    restart_app(device)
    click_by_Xpath(device, '//*[@content-desc="Menu, tab 6 of 6"]')
    click_by_Xpath(device, '//*[@content-desc="your profile picture"]')
    users = []
    userName = get_text_by_className(device, 'android.view.View', 1)
    users.append(userName)
    # friends = get_text_by_className(device, 'android.view.View', 2)
    # click_by_className(device, 'android.view.View', 2)
    # click_by_Xpath(device, '//*[@content-desc="Following"]')
    # follow = get_text_by_className(device, 'android.view.ViewGroup', 11)
    return users, None, None


def like_post(device, post_link):
    try:
        open_link(device, post_link)
        liked = check_element_exists_by_Xpath(device, '//*[@content-desc="Like button, pressed. Double tap and hold to change reaction."]')
        if liked:
            logger.info(f"[FaceBook]: already liked, {post_link}")
            return True
        else:
            click_by_Xpath(device, '//*[@content-desc="Like button. Double tap and hold to react."]')
            liked = check_element_exists_by_Xpath(device, '//*[@content-desc="Like button, pressed. Double tap and hold to change reaction."]')
            if liked:
                logger.info(f"[FaceBook]: like success, {post_link}")
                return True
            else:
                logger.error(f"[FaceBook]: like failed, {post_link}")
                return False
    except Exception as e:
        logger.error(f"[FaceBook]: like failed, {post_link}, {e}")
        return False

def comment_post(device, post_link, comment):
    try:
        open_link(device, post_link)
        click_by_Xpath(device, '//*[@content-desc="Comment"]')
        paste_text_by_className(device, comment, "android.widget.EditText")
        click_by_Xpath(device, '//*[@content-desc="Send"]')
        logger.info(f"[FaceBook]: comment success, {post_link}")
        return True
    except Exception as e:
        logger.error(f"[FaceBook]: comment failed, {post_link}, {e}")
        return False

def post_photo(device, photo_url, content):
    try:

        clear_camera_cache()
        restart_app(device)
        # 手机存储地址
        file_path = extract_filename_from_url(photo_url)
        os_push_image(device,photo_url,file_path)
        click_by_Xpath(device, '//*[@content-desc="Create, Double tap to create a new post, story, or reel"]')
        click_by_Xpath(device,'//android.widget.TextView[@text="Post"]')

        edit_text = device(className = "android.widget.EditText")
        if edit_text.wait(3):
            edit_text.set_text(content)
        else:
            logger.info("[FaceBook]:  post photo failed, edit_text not found")

        click_by_Xpath(device,'//*[@content-desc="Photo/video"]')
        time.sleep(3)
        # click_by_Xpath(device,'//*[@content-desc="Gallery"]')
        # click_by_Xpath(device,'//*[@content-desc="Screenshots, 1, Media"]')
        device.click(180,500)
        # click_by_className(device,"android.view.ViewGroup",index=0)
        click_by_Xpath(device,'//*[@content-desc="POST"]')
        element = device.xpath('//*[@content-desc="Your post couldn\'t be shared."]').wait(3)
        if element:
            logger.error(f"[FaceBook]: post photo failed, Your post couldn\'t be shared.")
            return False
        clear_camera_cache()
        return True
    except Exception as e:
        logger.error(f"[FaceBook]: post photo failed, {photo_url}, {e}")
        return False

def follow_user(device, user_link):
    try:
        open_link(device, user_link)
        click_by_Xpath(device, '//*[@content-desc="See more"]', timeout=5)
        element = device.xpath('//*[@content-desc="Following"]').wait(3)
        if element:
            logger.info(f"[FaceBook]: already followed, {user_link}")
            return True
        click_by_Xpath(device, '//*[@content-desc="Follow"]', timeout=5)
        return True
    except Exception as e:
        logger.error(f"[FaceBook]: follow user failed, {user_link}, {e}")
        return False

def shear_post(device, post_link, content):
    try:
        open_link(device, post_link)
        click_by_Xpath(device, '//*[@content-desc="Share"]')
        paste_text_by_className(device, content, "android.widget.EditText")
        click_by_Xpath(device, '//*[@content-desc="Share now"]')
        logger.info(f"[FaceBook]: shear post success, {post_link}")
        return True
    except Exception as e:
        logger.error(f"[FaceBook]: shear post failed, {post_link}, {e}")
        return False
if __name__ == '__main__':
    d = u2.connect()
    # comment_post(d, "https://www.facebook.com/share/18kt7uggvH/", "hhhhh")
    # post_photo(d, "https://c-ssl.dtstatic.com/uploads/blog/202203/22/20220322193453_8997f.thumb.400_0.jpg", "hhhhh")
    # follow_user(d, "https://www.facebook.com/share/15dNJA7PC8/")
    shear_post(d, "https://www.facebook.com/share/18kt7uggvH/", "hhhhh")