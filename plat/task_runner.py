from collections import defaultdict
from threading import Lock

import uiautomator2
from loguru import logger
from enums.xhs_enums import OperateEnums
from plat.xhs import follow
from plat.xhs.device.adb_device import adb_connect_device
from plat.facebook.u2_common import post_photo, comment_post, like_post, follow_user

device_lock = defaultdict(Lock)

def start_script_by_type(device_id, operate_cmd, task_json, soft_type=4):
    with device_lock[device_id]:
        device = uiautomator2.connect(device_id)
        device_id = device.serial
        operation = OperateEnums.from_str(operate_cmd)
        logger.info(f"[主动任务] 设备ID: {device_id} , 等待执行操作:{operation}")
        try:
            # 发送推文
            if  operation == OperateEnums.POST:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始发送推文操作")
                xhs_content = task_json['content']
                title = task_json.get('title')  # 如果不存在，默认为 None
                img_url = task_json.get('img_url')  # 如果不存在，默认为 None
                is_success = start_link_reply_retweet(device_id, None, title=title, img_url=img_url, comment=xhs_content, start_type=0, soft_type=soft_type)
            # 评论
            elif operation == OperateEnums.REPLY:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始评论操作")
                xhs_content = task_json['content']
                post_url = task_json['post_url']
                img_url = task_json.get('img_url')
                is_success = start_link_reply_retweet(device_id, post_url, img_url=img_url, comment=xhs_content,
                                                      start_type=1, soft_type=soft_type)
            # 点赞
            elif operation == OperateEnums.LIKE:
                logger.info(f"[ActiveTask] 设备ID: {device_id} 开始点赞操作")
                post_url = task_json['post_url']
                is_success = start_link_reply_retweet(device_id, post_url, start_type=2, soft_type=soft_type)
            # 关注
            elif operation == OperateEnums.FOLLOW:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始关注操作")
                user_id = task_json['user_id']
                is_success = start_link_reply_retweet(device_id, user_id, start_type=3, soft_type=soft_type)
            # 采集
            elif operation == OperateEnums.COLLECT:
                logger.info(f"[主动任务] 设备ID: {device_id} 开始采集操作")
                is_success = start_link_reply_retweet(device_id, "",start_type=4, soft_type=soft_type)
            else:
                raise Exception(f"[主动任务] 设备ID: {device_id} 不支持的操作:{operation}")
            return is_success
        except Exception as e:
            logger.error('scheduler, script by type error: {}', e)
            raise e

def start_link_reply_retweet(param_serial, param_link, title = None, img_url=None, comment=None, start_type=1, soft_type=4):
    try:
        # 校验设备状态
        device = adb_connect_device(param_serial)

        # 根据类型执行操作
        def execute_operation():
            operations = {
                 # 发布
                (0, 4): lambda: follow.operate_xhs_link(device, param_link, img_url=img_url, title= title, action_type=OperateEnums.POST, content=comment),
                (0, 5): lambda: post_photo(device, param_link, comment),
                # 评论
                (1, 4): lambda: follow.operate_xhs_link(device, param_link, img_url=img_url, title= title, action_type=OperateEnums.REPLY, content=comment),
                (1, 5): lambda: comment_post(device, param_link, comment),
                # 点赞
                (2, 4): lambda: follow.operate_xhs_link(device, param_link, img_url=img_url, title= title, action_type=OperateEnums.LIKE, content=comment),
                (2, 5): lambda: like_post(device, param_link),
                # 关注
                (3, 4): lambda: follow.operate_xhs_link(device, param_link, img_url=img_url, title= title, action_type=OperateEnums.FOLLOW, content=comment),
                (3, 5): lambda: follow_user(device, param_link),
                # 采集
                (4, 4): lambda: follow.operate_xhs_link(device, param_link, img_url=img_url, title= title, action_type=OperateEnums.COLLECT, content=comment)
            }
            return operations.get((start_type, soft_type), lambda: False)()

        operate_status = execute_operation()
        return operate_status
    except Exception as e:
        logger.error('login error: {}', e)
        raise e