import os
import re
import subprocess
import time

from loguru import logger

from core.matrix_workflow.nodes.xhs.utils import scroll_until_element_and_scroll_distance, close_update_popup
from enums.operate_enums import OperateEnums
from utils.click import click_resource_timeout_button
from utils.clipboard import get_clipboard_text
from utils.common import go_home, go_back
from utils.image import os_push_image, select_image_in_gallery, export_gallery_to_computer
from utils.str import extract_filename_from_url
from plat.xhs.common import restart_xhs, is_element_within_bounds, get_element_bounds
from plat.xhs.intent import open_xhs_link, open_xhs_user_home


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
                        if article["title"] == "" and article["content"] == "" and article["username"] == "":
                            skip = True
                        for art in articles:
                            if article["title"] == art["title"] and article["content"] == art["content"]:
                                skip = True
                                break
                        if skip:
                            d.press('back')
                            return articles
                        logger.info(f"设备：{d.serial},采集：{article}")
                        articles.append(article)
                    d.press('back')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        if len(articles) == 0:
            raise Exception("没有找到文章")
        return articles
    except Exception as e:
        logger.error(f'设备号{d.serial}: 采集小红书文章时发生错误{e}')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        raise e


# 搜索采集
def s_collect_articles(d):
    articles = []
    logger.info(f"设备：{d.serial}: 开始采集文章")
    #
    try:
        # 最长等待 10 秒查找目标控件
        if d(resourceId='com.xingin.xhs:id/g7j').wait(timeout=10):
            logger.info("找到 articles_button，准备点击")
            # print("当前Activity：", d.app_current())
            articles_button = d(resourceId='com.xingin.xhs:id/g7j')
            logger.info(f"articles_button数量:{len(articles_button)}")
        else:
            return logger.error("未找到 articles_button，超过 10 秒")
        if len(articles_button) > 0:
            for article_element in articles_button:
                video_button = article_element.sibling(resourceId='com.xingin.xhs:id/g7k')
                if video_button.exists and is_element_within_bounds(video_button,
                            get_element_bounds(article_element)):
                    # 如果为视频,则返回
                    return articles
                if article_element.exists:
                    article_element.click()
                    time.sleep(2) # 等待 2 秒
                    close_update_popup(d)
                    article = get_article_noimg(d)
                    if article is not None:
                        skip = False
                        if article["title"] == "" and article["content"] == "" and article["username"] == "":
                            skip = True
                        for art in articles:
                            if article["title"] == art["title"] and article["content"] == art["content"]:
                                skip = True
                                break
                        if skip:
                            d.press('back')
                            return articles
                        logger.info(f"设备：{d.serial},采集：{article}")
                        articles.append(article)
                    d.press('back')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        if len(articles) == 0:
            raise Exception("没有找到文章")
        return articles
        # return True
    except Exception as e:
        logger.error(f'设备号{d.serial}: 采集小红书文章时发生错误{e}')
        logger.info(f"设备: {d.serial}: 完成采集文章，共计{len(articles)}篇")
        raise e

# 采集评论
def collect_reply(d,tweet_url):
    close_update_popup(d)
    replies = []
    # replies = [{'user_name': '当时明月', 'content': '发现了宝藏 6天前  江苏 回复'}]
    width, height = d.window_size()
    start_x = width // 2
    swipe__y = int(height * 0.5)
    logger.info(f"设备：{d.serial}: 开始采集评论操作")
    try:
        reply_action(d) # 点击评论按钮
        main_reply = get_main_reply(d)
        replies = [*main_reply]
        print(replies)
        return replies
    except Exception as e:
        logger.error(f'设备号{d.serial}: 采集小红书评论时发生错误{e}')
        logger.info(f"设备: {d.serial}: 完成采集评论，共计{len(replies)}篇")
        raise e

# 回复评论
def reply_comment(d, reply_list):
    logger.info(f"设备：{d.serial}: 开始回复评论操作")
    close_update_popup(d)
    reply_action(d)

    replied_set = set() # 存储已回复的评论
    expand_clicked_users = set() # 存储已展开的评论
    checked_main_comments = set()  # 仅记录主评论 et3
    checked_sub_comments = set()  # 仅记录子评论 ibc
    max_checked_comments = 10 # 最大回复数量
    reply_status_map = {} # 存储回复状态

    def match_comment(user_name, content):
        for item in reply_list:
            if item["user_name"] == user_name and item["comment"].strip() in content.strip():
                return item  # ✅ 返回整个匹配项
        return None

    def process_comment_blocks(d, comment_blocks,isMainComment=True):
        nonlocal checked_main_comments, replied_set,  checked_sub_comments, max_checked_comments

        for item in comment_blocks:  # ⚠️ 保证是列表结构
            try:
                user_el = item.child(resourceId="com.xingin.xhs:id/jjp")
                content_el = item.child(resourceId="com.xingin.xhs:id/jci")
                if not user_el.exists or not content_el.exists:
                    continue

                user = user_el.info["text"].strip()
                content = content_el.info["text"].strip()
                # print(user)
                unique_key = (user, content)

                # 判断是否重复（主/子评论分别判断）
                if isMainComment:
                    if unique_key in checked_main_comments:
                        continue
                    checked_main_comments.add(unique_key)
                    # print(len(checked_main_comments))
                    if len(checked_main_comments) >= max_checked_comments:
                        return  # 主评论检查超出限制则退出
                else:
                    if unique_key in checked_sub_comments:
                        continue
                    checked_sub_comments.add(unique_key)

                matched_item = match_comment(user, content)
                if matched_item:
                    key = (matched_item["user_name"], matched_item["comment"].strip())
                    if key in replied_set:
                        continue

                    logger.info(f"准备回复【{user}】的评论：{content}")
                    content_el.click()
                    time.sleep(1)

                    input_box = d(resourceId="com.xingin.xhs:id/f33")
                    if input_box.wait(timeout=3):
                        input_box.set_text(matched_item["reply"])
                        time.sleep(0.5)

                        send_btn = d(resourceId="com.xingin.xhs:id/fb0")
                        if send_btn.exists(timeout=2):
                            send_btn.click()
                            time.sleep(2)
                            input_box = d(resourceId="com.xingin.xhs:id/f33")
                            if input_box.exists(timeout=2):
                                # 点击
                                d(resourceId="com.android.systemui:id/back").click()
                                logger.error(f"发送失败：{matched_item['reply']}")
                                reply_status_map[key] = {"status": "发送失败", "error": None}
                                time.sleep(0.5)
                                continue
                            logger.info(f"已成功发送评论：{matched_item['reply']}")
                            replied_set.add(key)
                            reply_status_map[key] = {"status": "已执行回复", "error": None}
                            time.sleep(2)
                        else:
                            reply_status_map[key] = {"status": "failed", "error": "发送按钮不存在"}
                    else:
                        reply_status_map[key] = {"status": "failed", "error": "输入框不存在"}

            except Exception as e:
                logger.warning(f"处理评论出错: {e}")
                reply_status_map[unique_key] = {"status": "failed", "error": str(e)}
                continue

    retry_limit = 20
    attempts = 0

    while attempts < retry_limit and len(replied_set) < len(reply_list):
        # 展开“更多回复”按钮
        expand_buttons = d(resourceId="com.xingin.xhs:id/euc")
        if expand_buttons.exists:
            for btn in expand_buttons:
                try:
                    related_comment = btn.down(resourceId="com.xingin.xhs:id/et3")
                    user_el = related_comment.child(resourceId="com.xingin.xhs:id/jjp")
                    if not user_el.exists:
                        continue
                    user_name = user_el.info["text"]
                    if user_name in expand_clicked_users:
                        continue
                    btn.click()
                    expand_clicked_users.add(user_name)
                    logger.info(f"展开了【{user_name}】上面的的更多评论按钮")
                    time.sleep(1)
                except Exception as e:
                    continue
                    # logger.warning(f"点击展开按钮失败: {e}")

        comment_blocks = d(resourceId="com.xingin.xhs:id/et3")
        process_comment_blocks(d, comment_blocks,True)
        comment_blocks = d(resourceId="com.xingin.xhs:id/ibc")
        process_comment_blocks(d, comment_blocks,False)

        if len(checked_main_comments) >= max_checked_comments or len(replied_set) >= len(reply_list):
            break

        # 滑动加载更多
        width, height = d.window_size()
        start_x = width // 2
        swipe_y = int(height * 0.5)
        d.swipe(start_x, swipe_y + 300, start_x, swipe_y - 300, 0.2)
        time.sleep(1)
        attempts += 1

    # 为未匹配成功的评论补状态
    for item in reply_list:
        key = (item["user_name"], item["comment"].strip())
        if key not in reply_status_map:
            reply_status_map[key] = {"status": "未找到", "error": "在页面中未找到该评论"}

    # 构建返回结构
    result_data = []
    for item in reply_list:
        key = (item["user_name"], item["comment"].strip())
        status_info = reply_status_map.get(key, {"status": "unknown", "error": "未知状态"})
        result_data.append({
            "user_name": item["user_name"],
            "comment": item["comment"],
            "reply": item["reply"],
            "status": status_info["status"],
            "error": status_info["error"]
        })

    return {
        "replied_count": len(replied_set),
        "data": result_data
    }


# 点击评论按钮
def reply_action(d):
        # 1.首次进入作品页面, 点击 一次 评论按钮
        click_repl = d(resourceId='com.xingin.xhs:id/g6e')
        if click_repl.wait(timeout=5):
            click_repl.click()
        else:
            logger.warning("未找到评论按钮")
            return False
        # 2.判断是否正确跳转
        enterkey = d(resourceId='com.google.android.inputmethod.latin:id/key_pos_ime_action')
        if enterkey.wait(timeout=5):
            logger.warning("暂无评论!")
            return False
        else:
            return True

# 获取<=5个主评论
def get_main_reply(d):
    main_reply = []
    seen_comment_ids = set()  # 用于防止重复添加
    max_comments = 5
    retry_limit = 15  # 最大尝试次数，防止死循环
    attempts = 0

    while len(main_reply) < max_comments and attempts < retry_limit:
        # 获取当前屏幕上所有主评论框
        comment_blocks = d(resourceId='com.xingin.xhs:id/et3')
        if not comment_blocks.exists:
            logger.warning("未找到任何主评论框")
            break

        for comment in comment_blocks:
            try:
                if len(main_reply) >= max_comments:
                    break

                content_el = comment.child(resourceId='com.xingin.xhs:id/jci')

                # 1. 不存在文字控件，跳过
                if not content_el.exists:
                    continue

                # 2. 获取文本内容
                content = content_el.info['text'].strip()

                # 3. 只包含表情标签（如 [doge]、[飞吻R] 等）
                # 匹配内容是否全部是 [xxx] 形式，可重复
                only_tags_or_mentions = re.fullmatch(r'((\[[^\[\]]{1,10}\])|(@\S{1,20}))[ \u200b]*',content.replace('\u200b', ''))
                if only_tags_or_mentions:
                    continue  # 跳过无实质内容的评论

                user_el = comment.child(resourceId='com.xingin.xhs:id/jjp')
                content_el = comment.child(resourceId='com.xingin.xhs:id/jci')

                if not user_el.exists or not content_el.exists:
                    continue

                user_name = user_el.info['text']
                content = content_el.info['text']

                print(f"[主评论] 用户：{user_name} 内容：{content}")

                # 构造唯一ID（可用用户+内容简单hash）
                unique_id = f"{user_name}-{content}"
                if unique_id in seen_comment_ids:
                    continue


                scroll_until_element_and_scroll_distance(d, text=content)
                child_reply = get_child_reply(d, content)
                print(child_reply)
                main_reply.append({"user_name": user_name, "content": content,"sub_comments":  child_reply})
                seen_comment_ids.add(unique_id)


            except Exception as e:
                logger.warning(f"解析评论块失败: {e}")
                continue

        # 滑动查找下一屏
        width, height = d.window_size()
        start_x = width // 2
        swipe_y = int(height * 0.5)
        d.swipe(start_x, swipe_y + 100, start_x, swipe_y - 100, 0.2)

        attempts += 1
        time.sleep(1)

    return main_reply

# 获取<=3个子评论
def get_child_reply(d, text=''):
    def extract_reply_info(element):
        try:
            user_name = element.child(resourceId='com.xingin.xhs:id/jjp').info['text']
            content = element.child(resourceId='com.xingin.xhs:id/jci').info['text']
            return {"user_name": user_name, "content": content}
        except Exception as e:
            print(f"解析评论失败: {e}")
            return None

    chil_reply = []
    expand_num = 0

    # 判断是否存在2条以上子评论
    if no_only_one(d, text):
        # 尝试点击“查看更多”
        expand = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/euc")
        if expand.wait(timeout=5):
            try:
                expand_num = int(expand.info['text'].split(' ')[1])
            except:
                expand_num = 0

            expand.click()

            # 获取第一条子评论
            first_child = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/bgr")
            if first_child.wait(timeout=5):
                reply = extract_reply_info(first_child)
                if reply:
                    chil_reply.append(reply)

            # 获取更多子评论
            for i in range(min(expand_num,2)):  # 减去第一条已处理
                if i >= len(chil_reply):
                    break  # 避免 index 越界
                prev_reply = chil_reply[i]
                next_element = d(text=prev_reply['content']).down(resourceId='com.xingin.xhs:id/bgr')
                if next_element.wait(timeout=5):
                    reply = extract_reply_info(next_element)
                    if reply:
                        chil_reply.append(reply)

                    # 模拟滑动加载
                    width, height = d.window_size()
                    x = width // 2
                    y = int(height * 0.5)
                    d.shell(f"input swipe {x} {y + 75} {x} {y - 75} 150")
        return chil_reply

    # 如果只有一条子评论
    elif no_only_one(d, text,1):
        first_child = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/bgr")
        if first_child.wait(timeout=5):
            reply = extract_reply_info(first_child)
            if reply:
                chil_reply.append(reply)
        return chil_reply

    # 无子评论
    logger.info("该主评论没有子评论")
    return chil_reply

# 判断当前页面是否有子评论,如果有,子评论是否属于需要查找的主评论
def no_only_one(d,text,status=0):
    global middle_zk, middle_fmp, middle_lmp, middle_fmpzp
    fmp = d(resourceId="com.xingin.xhs:id/jci", text=text)
    zk = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/euc")
    fmpzp = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/bgr")
    lmp = d(resourceId="com.xingin.xhs:id/jci", text=text).down(resourceId="com.xingin.xhs:id/et3")
    if fmp is None or  zk is  None or  fmpzp is  None or lmp is  None:
        print("目标元素不存在")
        if status == 0:
            if zk is None:
                print("✅有0或1条")
                return False
        elif status == 1:
            if fmpzp is None:
                print("❌没有子评论")
                return False
        # exit() # 退出程序


    # 中间区域的垂直范围
    if not fmp is None:
        middle_fmp = fmp.center()[1]
    if not zk is None:
        middle_zk = zk.center()[1]
    if not fmpzp is None:
        middle_fmpzp = fmpzp.center()[1]
    if not lmp is None:
        middle_lmp = lmp.center()[1]


    if status == 0:
        if middle_fmp < middle_lmp < middle_zk:
            # print("✅有0或1条")
            return False
        else:
            # print("✅有1条以上")
            return True
    elif  status == 1:
        if middle_fmp < middle_fmpzp < middle_lmp:
           return True
        else:
            print("❌没有子评论")
            return False

def get_article(device, count):
    clear_gallery(device.serial)
    save_image(device, count)
    article = {}
    title_button = device(resourceId='com.xingin.xhs:id/g8t')
    if title_button.wait(timeout=10):
        title = title_button.get_text()
        article['title'] = title
    else:
        article['title'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章标题')
    articles_area = device(resourceId='com.xingin.xhs:id/dqd')
    if articles_area.wait(timeout=10):
        article_text = articles_area.get_text()
        article['content'] = article_text
    else:
        article['content'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章内容')
    user_button = device(resourceId='com.xingin.xhs:id/nickNameTV')
    if user_button.wait(timeout=10):
        user = user_button.get_text()
        article['username'] = user
    else:
        article['username'] = ""
        logger.error(f'设备：{device.serial}:没有找到用户名称')
    share_button = device(resourceId='com.xingin.xhs:id/moreOperateIV')
    if share_button.wait(timeout=10):
        share_button.click()
        time.sleep(1)
        copy_button = device(resourceId='com.xingin.xhs:id/j_8', text='复制链接')
        if copy_button.wait(timeout= 10) and copy_button.exists:
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
    # image_path = device.serial + "\\" + article["title"] + article["username"]
    image_path = os.path.join(device.serial, article["title"] + article["username"])
    export_gallery_to_computer(image_path, device.serial)
    return article

def get_article_noimg(device):
    article = {}
    title_button = device(resourceId='com.xingin.xhs:id/g8t')
    if title_button.wait(timeout=10):
        title = title_button.get_text()
        article['title'] = title
    else:
        article['title'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章标题')
    articles_area = device(resourceId='com.xingin.xhs:id/dqd')
    if articles_area.wait(timeout=10):
        article_text = articles_area.get_text()
        article['content'] = article_text
    else:
        article['content'] = ""
        logger.error(f'设备：{device.serial}:没有找到文章内容')
    user_button = device(resourceId='com.xingin.xhs:id/nickNameTV')
    if user_button.wait(timeout=10):
        user = user_button.get_text()
        article['username'] = user
    else:
        article['username'] = ""
        logger.error(f'设备：{device.serial}:没有找到用户名称')
    share_button = device(resourceId='com.xingin.xhs:id/moreOperateIV')
    if share_button.wait(timeout=10):
        share_button.click()
        time.sleep(1)
        copy_button = device(resourceId='com.xingin.xhs:id/j_8', text='复制链接')
        if copy_button.wait(timeout= 10) and copy_button.exists:
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
    # image_path = device.serial + "\\" + article["title"] + article["username"]
    # image_path = os.path.join(device.serial, article["title"] + article["username"])
    # export_gallery_to_computer(image_path, device.serial)
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
    if search.wait(timeout=5):
        search.click()
    else:
        logger.warning("未找到搜索按钮")


def search_keyword(device, search_text):
    """
    在应用中点击底部的icon并输入搜索文字。

    :param device: uiautomator2连接的设备对象
    :param search_text: 要输入的搜索内容
    """
    try:
        logger.info("当前Activity：", device.app_current())
        go_home(device)
        close_update_popup(device)
        click_search(device)
        time.sleep(1) # 等待1秒
        # print("当前Activity：", device.app_current())
        search_box_f = device(resourceId="com.xingin.xhs:id/fam")
        search_box_l = device(resourceId="com.xingin.xhs:id/fah")

        if search_box_f.exists:
            search_box_f.set_text(search_text)
            device(resourceId='com.xingin.xhs:id/luz', text='搜索').click()
        elif search_box_l.exists:
            search_box_l.click()
            search_box_f.set_text(search_text)
            device(resourceId='com.xingin.xhs:id/luz', text='搜索').click()
        else :
            click_search(device)
            time.sleep(1)
            logger.warning("没有找到搜索框")

        # if search_box.exists:
        #     # 查找虚拟键盘
        #     search_input = device(resourceId='com.google.android.inputmethod.latin:id/0_resource_name_obfuscated',
        #                           className="android.widget.FrameLayout")
        #     if search_input.exists:
        #         search_box.set_text(search_text)
        #         # 点击键盘的搜索按钮
        #         device(resourceId='com.xingin.xhs:id/luz', text='搜索').click()
        #         # d.press("enter")
        # else:
        #     logger.warning("没有找到搜索框")

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
        6 - 搜索
        7 - 采集评论
    """
    # time.sleep(3)
    # 根据操作类型执行不同的动作
    if action_type == OperateEnums.POST: # 发布文章
        logger.info(f"Performing Concern...")
        return open_new_post(device, img_url, title, content)
    elif action_type == OperateEnums.REPLY: # 评论
        logger.info(f"Performing Comment...{content}")
        open_xhs_link(tweet_url, device.serial)
        return reply_post(device, content)
    elif action_type == OperateEnums.LIKE: # 点赞
        logger.info("Performing Like...")
        open_xhs_link(tweet_url, device.serial)
        return like_post(device)
    elif action_type == OperateEnums.FOLLOW: #  关注
        logger.info("Performing Follow...")
        open_xhs_user_home(device.serial, tweet_url) # 打开用户主页
        return concern_post(device) # 关注
    elif action_type == OperateEnums.COLLECT: # 收藏
        logger.info("Performing COLLECT...")
        restart_xhs(device) # 重启xhs
        return collect_articles(device) # 收藏
    elif action_type == OperateEnums.SEARCH:
        search_keyword(device, tweet_url) # 搜索
        logger.info("搜索操作完成完成")
        return s_collect_articles(device) # 采集
    elif action_type == OperateEnums.COLLECT_REPLY:
        open_xhs_link(tweet_url, device.serial)
        logger.info("打开作品页")
        return collect_reply(device,tweet_url) # 采集评论
    elif action_type == OperateEnums.REPLY_COMMENT:
        open_xhs_link(tweet_url["link_url"], device.serial)
        logger.info("打开作品页")
        return reply_comment(device,tweet_url["execute_data"]) # 采集评论
    else:
        logger.warning("Invalid action type. Please use 0 for POST,1 for REPLY, 2 for LIKE, 3 for FOLLOW, or 4 for COLLECT")
        raise ValueError("Invalid action type. Please use 0 for POST,1 for REPLY, 2 for LIKE, 3 for FOLLOW, or 4 for COLLECT")

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
        raise e


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
        raise e


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
        raise e


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
        raise e


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
if __name__ == '__main__':
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)

    # 向上三层目录
    parent_dir = os.path.dirname(current_file_path)
    grandparent_dir = os.path.dirname(parent_dir)
    great_grandparent_dir = os.path.dirname(grandparent_dir)

    print("向上三层目录:", great_grandparent_dir)
