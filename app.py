import json
import os
import queue
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from core.matrix_workflow.workflow_runner.runner import MatrixWorkflowRunner, post_task
from plat.device.adb_device import get_connected_devices, get_adb_path
from utils.system_config import load_config, get_config

task_executor = ThreadPoolExecutor(max_workers=10)  # 任务线程池

scheduler = None

task_queue = queue.Queue() # 任务队列

heartbeat_request_url = "http://121.43.149.18:8000/api/matrix/task/retrieve-task"
report_request_url = "http://121.43.149.18:8000/api/matrix/task/results"


def init_scheduled_job():
    global scheduler # 定时任务
    if not scheduler: # 定时任务未启动
        scheduler = BackgroundScheduler() # 定时任务
        scheduler.add_job(scheduler_executor_heartbeat_queue, 'interval', max_instances=1, seconds=5)
        scheduler.start()
        logger.info("定时任务执行")

def scheduler_executor_heartbeat_queue():
    global task_queue # 任务队列
    try:
        adb_path = get_adb_path() # adb 路径
        devices_list = get_connected_devices(adb_path) # 设备列表
        authorization_key = get_config("Authorization_KEY") # 授权码
        headers = {'Authorization': authorization_key} # 请求头
        response = requests.post(heartbeat_request_url, headers=headers, json={"devices_list": devices_list}) # 请求接口 设备列表
        if response.status_code != 200:
            # logger.error('scheduler, heartbeat request error， code != 200, response: {}'.format(response))
            return
        result_arr_json = json.loads(response.text) # 解析响应
        task_config = result_arr_json['data'] # 任务配置
        task_queue.put(task_config) # 将任务配置放入队列
    except Exception as e:
        logger.error('scheduler, heartbeat request error, {}'.format(e))

def run_task():

    while True:
        try:
            global task_queue # 这一步是 多进程安全, 防止阻塞
            if task_queue.empty(): # 如果队列为空，则继续循环
                continue
            task_config = task_queue.get() # 从队列中取出任务配置
            logger.info('run task, graph_config: {}'.format(task_config))
            flow_run_result = MatrixWorkflowRunner(task_config).run() # 执行任务 传入 任务配置 task_config 是 json 从 flask 传递过来的 json
            report = {}
            # TODO 调用任务回调接口
            report["task_uuid"] = task_config['uuid'] # 任务uuid
            if len(flow_run_result) >=1: # 判断任务结果
                count = 0 # 计算任务结果
                for key, value in flow_run_result.items(): # 遍历任务结果
                    if value.status:
                        count +=1
                if count == len(flow_run_result):
                    report["status"] = 0
                elif 0 < count < len(flow_run_result):
                    report["status"] = 1
                else:
                    report["status"] = 2
                report["results"] = {
                    key: result.to_dict()  # 对每个 DeviceRunResult 调用 to_dict()
                    for key, result in flow_run_result.items()
                }
                authorization_key = get_config("Authorization_KEY")
                headers = {'Authorization': authorization_key}
                response = requests.post(report_request_url, headers=headers, json=report)
                if response.status_code!= 201:
                    logger.error('run task, report request error， code!= 201, response: {}'.format(response))
                else:
                    logger.info('run task, report request success')
            logger.info('run task, result_Mapping: {}'.format(flow_run_result))
        except Exception as e:
            logger.error('run task, error, {}'.format(e))


def init_task_runner():
    task_executor.submit(run_task) # 提交任务


app = Flask(__name__)

if __name__ == '__main__':
    logger.add(
        "logs/workflow.log",  # 日志文件
        rotation='100 MB', retention='10 days', compression="zip",  # 最大10M, 保留10天, 压缩ZIP
        enqueue=True,  # 多进程安全, 防止阻塞
    )
    logger.info('程序初始化 ...')
    load_config() # 加载配置
    init_scheduled_job() # 初始化定时任务
    init_task_runner() # 初始化任务执行器

    # post_task()
    logger.info('初始化结束 ...')
    # use_reloader=False 禁用自动重载，防止定时器触发两次
    app.run(host='0.0.0.0', port=9090, debug=True, use_reloader=False)
