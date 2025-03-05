# from enums import OperateEnums
from collections import defaultdict
from threading import Lock

import uiautomator2
from loguru import logger

from enums.xhs_enums import OperateEnums
from xhs import follow
from xhs.device.adb_device import adb_connect_device

device_lock = defaultdict(Lock)

def start_script_by_type(device_id, operate_cmd, task_json, soft_type=4):
    with device_lock[device_id]:
        result_json = {
            'data': None,
            'result_bool': False
        }
        device = uiautomator2.connect(device_id)
        device_id = device.serial
        operation = OperateEnums.from_str(operate_cmd)
        logger.info(f"[主动任务] 设备ID: {device_id} , 等待执行操作:{operation}")
        try:
            if operation == OperateEnums.LIKE:
                logger.info(f"[ActiveTask] 设备ID: {device_id} 开始点赞操作")
                twitter_url = task_json['twitter_url']
                is_success = start_link_reply_retweet(device_id, twitter_url, start_type=5, soft_type=soft_type)
            # 评论
            elif operation == OperateEnums.REPLY:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始评论操作")
                tweet_content = task_json['content']
                twitter_url = task_json['twitter_url']
                img_url = task_json.get('img_url')
                is_success = start_link_reply_retweet(device_id, twitter_url, img_url=img_url, comment=tweet_content,
                                                      start_type=1, soft_type=soft_type)
            # 发送推文
            elif operation == OperateEnums.POST:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始发送推文操作")
                device = adb_connect_device(device_id)
                tweet_content = task_json['content']
                title = task_json.get('title')  # 如果不存在，默认为 None
                img_url = task_json.get('img_url')  # 如果不存在，默认为 None
                is_success = follow.open_new_post(device, img_url, title, tweet_content)
            else:
                pass
            result_json['result_bool'] = is_success
        except Exception as e:
            logger.error('scheduler, script by type error: {}', e)

def start_link_reply_retweet(param_serial, param_link, img_url=None, comment=None, start_type=1, soft_type=0):
    # # 校验参数
    # if param_serial is None or param_serial == '':
    #     return set_api_result_error(500, 'serial is empty')
    # if param_link is None or param_link == '':
    #     return set_api_result_error(500, 'link is empty')

    try:
        # 校验设备状态
        device = adb_connect_device(param_serial)

        # 根据类型执行操作
        def execute_operation():
            operations = {
                # (1, 1): lambda: open_link_manager.open_tweet_reply(device, param_link, img_url, comment),
                # (1, 2): lambda: truth_follow_manager.reply_link_post(device, param_link, comment),
                # (1, 3): lambda: ins_follow_manager.instagram_link_reply(device, param_link, comment),
                (1, 4): lambda: follow.operate_xhs_link(device, param_link, OperateEnums.REPLY, comment),

                # (2, 1): lambda: open_link_manager.open_link_retweet(device, param_link, img_url, comment),
                # (2, 2): lambda: truth_follow_manager.retweet_link_post(device, param_link, comment),
                # ins和小红书 没有转发
                # (3, 1): lambda: open_link_manager.open_link_follow(device, param_link),
                # (3, 2): lambda: truth_follow_manager.follow_link_account(device, param_link),
                # (3, 3): lambda: ins_follow_manager.instagram_link_follow(device, param_link),
                # (3, 4): lambda: follow.operate_tweet_link(device, param_link, OperateEnums.CONCERN),

                # (4, 1): lambda: open_link_manager.open_link_delete(device, param_link),

                (5, 4): lambda: follow.operate_xhs_link(device, param_link, OperateEnums.LIKE, img_url),
            }
            return operations.get((start_type, soft_type), lambda: False)()

        operate_status = execute_operation()
        return operate_status
    except Exception as e:
        logger.error('login error: {}', e)
        return False