import os
import re
import subprocess
import time

from loguru import logger

from enums.xhs_enums import OperateEnums
from utils.click import click_resource_timeout_button
from utils.clipboard import get_clipboard_text
from utils.image import os_push_image, select_image_in_gallery
from utils.str import extract_filename_from_url
from platform.xhs.common import restart_xhs, is_element_within_bounds, get_element_bounds
from platform.xhs.intent import open_xhs_link, open_xhs_user_home

local_directory = "D:\\work\\matrix-workflow-performer\\collect\\images\\"


def collect_articles(d):
    articles = []
    logger.info(f"设备：{d.serial}: 开始采集文章")
    try:
        articles_button = d(resourceId='com.xingin.xhs:id/e6p')
        if len(articles_button) > 0:
            for article_element in articles_button:
                video_button = article_element.sibling(resourceId='com.xingin.xhs:id/e94')
                if video_button.exists and is_element_within_bounds(video_button,
                                                                    get_element_bounds(article_element)):
                    return articles
                if article_element.exists:
                    article_element.click()
                    time.sleep(2)
                    count = int(get_image_count(d))
                    article = get_article(d, count)
                    if article is not None:
                        skip = False
                        if article["title"] == "" and article["tweet"] == "" and article["username"] == "":
                            skip = True
                        for art in articles:
                            if article["title"] == art["title"] and article["tweet"] == art["tweet"]:
                                skip = True
                                break
                        if skip:
                            d.press('back')
                            return articles
                        logger.info(f"设备：{d.serial},采集：{article}")
                        articles.append(article)
                    d.press('back')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        return articles
    except Exception as e:
        logger.error(f'设备号{d.serial}: 采集小红书文章时发生错误{e}')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        return articles


def get_article(device, count):
    clear_gallery(device.serial)
    save_image(device, count)
    article = {}
    title_button = device(resourceId='com.xingin.xhs:id/g8t')
    if title_button.exists:
        title = title_button.get_text()
        article['title'] = title
    else:
        article['title'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章标题')
    articles_area = device(resourceId='com.xingin.xhs:id/dqd')
    if articles_area.exists:
        article_text = articles_area.get_text()
        article['tweet'] = article_text
    else:
        article['tweet'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章内容')
    user_button = device(resourceId='com.xingin.xhs:id/nickNameTV')
    if user_button.exists:
        user = user_button.get_text()
        article['username'] = user
    else:
        article['username'] = ""
        logger.error(f'设备：{device.serial}:没有找到用户名称')
    share_button = device(resourceId='com.xingin.xhs:id/moreOperateIV')
    if share_button.exists:
        share_button.click()
        time.sleep(1)
        copy_button = device(resourceId='com.xingin.xhs:id/j_8', text='复制链接')
        if copy_button.wait(timeout= 3) and copy_button.exists:
            copy_button.click()
            time.sleep(1)
            xhs_link = get_clipboard_text(device)
            if xhs_link:
                # 正则表达式提取链接
                link_pattern = r"http[s]?://[^\s，]+"
                links = re.findall(link_pattern, xhs_link)
                if len(links) > 0:
                    article['link'] = links[0]
                else:
                    article['link'] = ""
        else:
            logger.error(f'设备：{device.serial}:没有找到复制按钮')
    image_path = device.serial + "\\" + article["title"] + article["username"]
    export_gallery_to_computer(image_path, device.serial)
    return article


# '65 Amber Lee发布了一篇小红书笔记，快来看吧！ 😆 Dirvawmprxtvxhh 😆 Http://Xhslink.Com/A/Uycel4Cdziv3，复制本条信息，打开【小红书】App查看精彩内容！'
# def swipe_up(d):
#     # 获取设备的屏幕尺寸
#     device_width, device_height = d.window_size()
#
#     # 定义滑动的起始点和结束点
#     start_x = device_width // 2
#     start_y = device_height * 3 // 4
#     end_x = start_x
#     end_y = device_height // 4
#
#     # 模拟上滑手势
#     d.swipe(start_x, start_y, end_x, end_y)


def click_search(device):
    search = device(resourceId='com.xingin.xhs:id/hmg', index=2)
    if search.exists:
        search.click()
    else:
        logger.warning("没有找到Search元素")


def search_keyword(device, search_text):
    """
    在应用中点击底部的icon并输入搜索文字。

    :param device: uiautomator2连接的设备对象
    :param search_text: 要输入的搜索内容
    """
    try:
        click_search(device)
        time.sleep(1)
        # 查找输入框
        search_box = device(resourceId="com.xingin.xhs:id/fam")

        if search_box.exists:
            # 查找虚拟键盘
            search_input = device(resourceId='com.google.android.inputmethod.latin:id/0_resource_name_obfuscated',
                                  className="android.widget.FrameLayout")
            if search_input.exists:
                search_box.set_text(search_text)
                # 点击键盘的搜索按钮
                device(resourceId='com.xingin.xhs:id/luz', text='搜索').click()
                # d.press("enter")
        else:
            logger.warning("没有找到搜索框")

    except Exception as e:
        logger.exception(f"异常: {e}")


def search_follow(device, search_text):
    """
    在应用中点击底部的icon并输入搜索文字。

    :param device: uiautomator2连接的设备对象
    :param search_text: 要输入的搜索内容
    """
    try:
        click_search(device)
        time.sleep(1)
        # 查找输入框
        search_box = device(resourceId="com.xingin.xhs:id/fam")

        if search_box.exists:
            # 查找虚拟键盘
            search_input = device(resourceId='com.google.android.inputmethod.latin:id/0_resource_name_obfuscated',
                                  className="android.widget.FrameLayout")
            if search_input.exists:
                search_box.set_text(search_text)
                # 点击搜索按钮
                device(resourceId='com.xingin.xhs:id/luz', text='搜索').click()
                # d.press("enter")
                # 点击上方的账号栏
                device(className='androidx.appcompat.app.ActionBar$Tab', index=1).click()
                time.sleep(1)
                follow_account(device)
        else:
            logger.warning("没有找到搜索框")

    except Exception as e:
        logger.exception(f"异常: {e}")


def follow_account(device):
    follow_button = device(className="android.view.ViewGroup", index=1).child(resourceId='com.xingin.xhs:id/cmo',
                                                                              text='关注')
    if follow_button.exists:

        # logger.info(f"找到关注按钮，模拟已关注！")
        follow_button.click()
    else:
        logger.warning("未找到关注按钮")


def open_tweet_link(device, tweet_url):
    # 关闭xhs应用
    # subprocess.run(["adb", "shell", "am force-stop com.twitter.android"])
    device.app_stop("com.xingin.xhs")
    time.sleep(1)

    # 用 subprocess 打开推文链接
    subprocess.run(
        ["adb", "-s", device.serial, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d",
         tweet_url])
    apply_button = device(resourceId='com.vivo.browser:id/buttonDefaultPositive', text='允许')
    if apply_button.wait(timeout=10) and apply_button.exists:
        apply_button.click()
        logger.info(f"点击允许按钮")
    logger.info(f"Opening 小红书: {tweet_url}")
    # 等待推文页面加载
    time.sleep(3)


def operate_xhs_link(device, tweet_url, img_url, title=None, action_type=None, content=None):
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
        return open_new_post(device, img_url, title, content)
    elif action_type == OperateEnums.REPLY:
        logger.info(f"Performing Comment...{content}")
        open_xhs_link(tweet_url, device.serial)
        return reply_post(device, content)
    elif action_type == OperateEnums.LIKE:
        logger.info("Performing Like...")
        open_xhs_link(tweet_url, device.serial)
        return like_post(device)
    elif action_type == OperateEnums.FOLLOW:
        logger.info("Performing Follow...")
        open_xhs_user_home(device.serial, tweet_url)
        return concern_post(device)
    elif action_type == OperateEnums.COLLECT:
        logger.info("Performing COLLECT...")
        restart_xhs(device)
        return collect_articles(device)
    else:
        logger.warning("Invalid action type. Please use 0 for POST,1 for REPLY, 2 for LIKE, 3 for FOLLOW, or 4 for COLLECT")
        return False


# 关注
# def concern_post(device):
#     try:
#         has_concern = device(text='已关注', className='android.widget.TextView')
#         if has_concern.wait(timeout=3) and has_concern.exists:
#             logger.info("已经关注过了")
#             return True
#         concern = device(text='关注', className='android.widget.TextView')
#         if concern.wait(timeout=5) and concern.exists:
#             concern.click()
#             time.sleep(1)
#             logger.info("关注成功")
#             return True
#         return False
#     except Exception as e:
#         logger.exception(f"发生错误: {e}")
#         return False

def concern_post(device):
    try:
        has_concern = device(resourceId='com.xingin.xhs:id/jo8', text='发私信')
        if has_concern.wait(timeout=3) and has_concern.exists:
            logger.info("已经关注过了")
            return True
        concern = device(resourceId='com.xingin.xhs:id/jo8', text='关注')
        if concern.wait(timeout=5) and concern.exists:
            concern.click()
            time.sleep(1)
            logger.info("关注成功")
            return True
        return False
    except Exception as e:
        logger.exception(f"发生错误: {e}")
        return False


# 评论
def reply_post(device, reply_text):
    """
    点击当前屏幕上推文的评论按钮。

    :param reply_text: 回复消息内容
    :param device: uiautomator2连接的设备对象
    """
    try:
        dvr = device(resourceId='com.xingin.xhs:id/dvr')
        if dvr.wait(timeout=5):
            dvr.click()
            time.sleep(1)
            device.send_keys(reply_text)
            time.sleep(1)
            device(text='发送', resourceId='com.xingin.xhs:id/fb0').click()
            logger.info(f"设备号 {device.serial} 评论成功")
            return True
        return False
    except Exception as e:
        logger.exception(f"发生错误: {e}")
        return False


# 发布,不能发纯文字，没有Post_Type
def open_new_post(device, image_url, title_text=None, content_text=None):
    restart_xhs(device)
    # open_xhs_post(device.serial)
    try:
        if not image_url:
            logger.error(f"设备号 {device.serial} 未上传图片")
            return False
        # 手机存储地址
        file_path = extract_filename_from_url(image_url)
        # 下载图片
        logger.info(f"设备 {device.serial} 开始下载图片...")
        flag = os_push_image(device, image_url, file_path)
        if not flag:
            logger.error(f"设备号 {device.serial} 下载图片失败")
            return False
        click_tab(device, 3)
        # 选择第一张图片
        select_image_in_gallery(device)
        # 点击第一次下一步
        click_resource_timeout_button(device, 'com.xingin.xhs:id/a_v', 'android.widget.TextView')
        # 点击第二次下一步
        click_resource_timeout_button(device, 'com.xingin.xhs:id/aqe', 'android.widget.TextView')
        # 发布标题 可以为none
        if title_text:
            click_resource_timeout_button(device, 'com.xingin.xhs:id/c3j', class_name='android.widget.EditText',
                                          btn_text='添加标题')
            device.send_keys(title_text)
        # 发布正文内容 可以为none
        if content_text:
            click_resource_timeout_button(device, 'com.xingin.xhs:id/gqy', class_name='android.widget.EditText',
                                          btn_text='添加正文')
            device.send_keys(content_text)
        click_resource_timeout_button(device, 'com.xingin.xhs:id/ap2', class_name='android.widget.Button',
                                      btn_text='发布')
        return True
    except Exception as e:
        logger.exception(f"发生错误: {e}")
        return False


# 点赞
def like_post(device):
    try:
        like_button = device(resourceId='com.xingin.xhs:id/g7x')
        if like_button.wait(timeout=10) and like_button.exists:
            if like_button.info['selected']:
                logger.info(f"设备号 {device.serial} 已经点过赞了")
                return True
            like_button.click()
            logger.info(f"设备号 {device.serial} 点赞成功")
            return True
        return False
    except Exception as e:
        logger.exception(f"发生错误: {e}")
        return False


'''
# 发现，获取最新的文章
@param max_tweets 最大采集数量
'''


# def collect_following_tweets(d, article_element):
#     # restart_xhs(d)
#
#     new_articles = []
#     tweets = collect_articles(d, article_element)
#     # 判断是否重复
#     data = read_from_json(d.serial)
#     if len(tweets) > 0:
#         for tweet in tweets:
#             if not is_content_in_list(tweet, data):
#                 new_articles.append(tweet)
#         tweets.reverse()
#         write_to_json(d.serial, tweets)
#     else:
#         restart_xhs(d)
#     return new_articles


# 从我的页面获取信息
# def get_profile_username(device):
#     """
#     参数:
#         device: uiautomator2 的设备对象。
#
#     返回:
#         匹配的用户名 (str)，如果没有找到则返回 None。
#     """
#     try:
#         restart_xhs(device)
#         # 进入我的界面
#         click_tab(device, 5)
#         toolbar = device(resourceId='com.xingin.xhs:id/e5p')
#         if toolbar.wait(timeout=3):
#             # 查找目标元素的所有兄弟节点
#             following_num = 0
#             following = device(resourceId='com.xingin.xhs:id/y4')
#             if following.wait(timeout=3):
#                 text = following.get_text()
#                 if text:
#                     # 总关注数量
#                     text = text.replace(",", "")
#                     following_num = int(text)
#             followers = device(resourceId='com.xingin.xhs:id/cdd')
#             follower_num = 0
#             # 获取粉丝数量
#             if followers.wait(timeout=3):
#                 text = followers.get_text()
#                 if text:
#                     # 总粉丝数量
#                     text = text.replace(",", "")
#                     follower_num = int(text)
#
#             user = device(resourceId='com.xingin.xhs:id/gxr', className='android.widget.TextView')
#             users = []
#             if user.exists:
#                 text = user.get_text()
#                 userid = text.split("：")[1]
#                 users.append(userid)
#                 logger.info(
#                     f"机器序列号:{device.serial}, 找到小红书ID: {userid} ,关注数量: {following_num}，粉丝数量:{follower_num}")
#                 return users, following_num, follower_num
#         else:
#             logger.warning(f"机器序列号: {device.serial} 未找到头像按钮")
#         return [], 0, 0  # 如果没有找到匹配的元素，返回 None
#     except Exception as e:
#         logger.exception(f"机器序列号: {device.serial} 获取用户名时发生错误: {e}")
#         return [], 0, 0


def click_tab(d, tab_type):
    """
        点击导航栏
        tab_type: 1:首页 2:热门 3:发作品 4:消息 5:我
    """
    # 找到底部的tab栏
    resource = ''
    match tab_type:
        case 1:
            resource = 'com.xingin.xhs:id/du5'
        case 2:
            resource = 'com.xingin.xhs:id/du_'
        case 3:
            resource = 'com.xingin.xhs:id/du1'
        case 4:
            resource = 'com.xingin.xhs:id/du7'
        case 5:
            resource = 'com.xingin.xhs:id/du6'
    tab_bar = d(resourceId=resource)
    if tab_bar.wait(timeout=5):
        tab_bar.click()
        # logger.info(f"点击进入{text}导航栏")
    else:
        logger.warning(f"{d.serial} 没有找到导航栏元素")


# def xhs_task():
#     heartbeat_request_url = x_app.get_heartbeat_request_url()
#     heartbeat_config = x_app.get_heartbeat_config()
#     response = requests.post(heartbeat_request_url, json=heartbeat_config)
#     if response.status_code != 200:
#         logger.error('scheduler, heartbeat request error， code != 200, response: {}'.format(response))
#         return
#     result_arr_json = json.loads(response.text)
#     task_arr = result_arr_json['operate_list']
#
#     if task_arr is None or len(task_arr) <= 0:
#         return
#     for result_json in task_arr:
#         device_id = result_json['device_id']
#         soft_type = 0
#         for device_config in heartbeat_config['devices']:
#             if device_config['device_id'] == device_id:
#                 soft_type = device_config['soft_type']
#         if soft_type != 4:
#             continue
#         operate_cmd = result_json['operate_cmd']
#         operate_data = result_json['operate_data']
#         operate_callback_url = result_json['operate_callback_url']
#         x_app.start_script_by_type(device_id, operate_callback_url, operate_cmd, operate_data,
#                                    soft_type)


def save_image(device, count):
    times = 1
    while True:
        image_area = device(resourceId="com.xingin.xhs:id/dq7")
        if image_area.wait(timeout=1) and image_area.exists:
            image_area.long_click(duration=1)
            save_button = device(resourceId="com.xingin.xhs:id/cr_", text="保存")
            if save_button.wait(timeout=1) and save_button.exists:
                save_button.click()
            else:
                logger.error(f"{device.serial} 没有找到保存按钮")
        else:
            logger.error(f"{device.serial} 没有找到图片区域")
        times += 1
        if times > count:
            break
        left_swipe(device, image_area)


def left_swipe(device, image_area):
    bounds = get_element_bounds(image_area)
    start_x, start_y = bounds[0] + bounds[2] // 2, bounds[1] + bounds[3] // 2
    end_x, end_y = bounds[0], bounds[1] + bounds[3] // 2
    device.swipe(start_x, start_y, end_x, end_y, duration=0.1)


def get_image_count(device):
    image_area = device(resourceId="com.xingin.xhs:id/dqe")
    if image_area.exists:
        text = image_area.get_text()
        text_arr = text.split("/")
        count = text_arr[1]
        logger.info(f"设备：{device.serial}: 自动采集已识别 {count} 张图片")
        return count
    else:
        return 0


# 清除保存的文件
def clear_gallery(serial):
    # 相册文件通常存储在 /sdcard/DCIM/Camera/ 目录下
    gallery_path = "/sdcard/DCIM/*.jpg"

    # 构造 adb shell 命令来删除相册中的文件
    command = f"adb -s {serial} shell rm -r {gallery_path}"

    # 执行命令
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 检查命令执行结果
    if result.returncode == 0:
        logger.info(f"设备：{serial}:相册已清空")
    else:
        logger.warning(f"设备：{serial} 清空相册失败: {result.stderr}")


# device_gallery_path = "/sdcard/DCIM/*.jpg"  local_directory = D:\work\groupc\xhsv2\image
def export_gallery_to_computer(image_path, serial, device_gallery_path = "/sdcard/DCIM/"):
    # 检查本地目录是否存在，如果不存在则创建
    local_path = local_directory + image_path
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    command = f"adb -s {serial} shell ls {device_gallery_path}"
    files = subprocess.run(command, capture_output=True,
                           text=True).stdout.splitlines()
    jpg_files = [f for f in files if f.endswith('.jpg')]

    # 导出每个 jpg 文件
    for jpg_file in jpg_files:
        full_device_path = f"{device_gallery_path}{jpg_file}"
        full_local_path = os.path.join(local_path, jpg_file)
        save_command = f"adb -s {serial} pull {full_device_path} {full_local_path}"
        subprocess.run(save_command)

#
# if __name__ == '__main__':
#     d = uiautomator2.connect()
#     image_area = d(resourceId="com.xingin.xhs:id/dq7")
#     left_swipe(d, image_area)
#     # count = int(get_image_count(d))
#     # save_image(d,count)
#
#     # local = "test"
#     # export_gallery_to_computer(device_gallery_path, local)
#     # clear_gallery()
