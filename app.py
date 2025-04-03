import json
import queue
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from core.matrix_workflow.workflow_runner.runner import MatrixWorkflowRunner, post_task

task_executor = ThreadPoolExecutor(max_workers=10)  # 任务线程池

scheduler = None

task_queue = queue.Queue()

heartbeat_request_url = "http://192.168.5.13:8000/api/matrix/task/retrieve-task"
report_request_url = "http://192.168.5.13:8000/api/matrix/task/results"


def init_scheduled_job():
    global scheduler
    if not scheduler:
        scheduler = BackgroundScheduler()
        scheduler.add_job(scheduler_executor_heartbeat_queue, 'interval', max_instances=1, seconds=5)
        scheduler.start()
        logger.info("定时任务执行")

def scheduler_executor_heartbeat_queue():
    global task_queue
    try:
        response = requests.get(heartbeat_request_url)
        if response.status_code != 200:
            # logger.error('scheduler, heartbeat request error， code != 200, response: {}'.format(response))
            return
        result_arr_json = json.loads(response.text)
        task_config = result_arr_json['data']
        task_queue.put(task_config)
    except Exception as e:
        logger.error('scheduler, heartbeat request error, {}'.format(e))

def run_task():

    while True:
        try:
            global task_queue
            if task_queue.empty():
                continue
            task_config = task_queue.get()
            logger.info('run task, graph_config: {}'.format(task_config))
            flow_run_result = MatrixWorkflowRunner(task_config).run()
            report = {}
            # TODO 调用任务回调接口
            if len(flow_run_result) >=1:
                count = 0
                for key, value in flow_run_result.items():
                    if value.status:
                        count +=1
                if count == len(flow_run_result):
                    report["status"] = 0
                elif 0 < count < len(flow_run_result):
                    report["status"] = 1
                else:
                    report["status"] = 2
                report["task_uuid"] = task_config['uuid']
                report["results"] = {
                    key: result.to_dict()  # 对每个 DeviceRunResult 调用 to_dict()
                    for key, result in flow_run_result.items()
                }
                response = requests.post(report_request_url, json=report)
                if response.status_code!= 201:
                    logger.error('run task, report request error， code!= 201, response: {}'.format(response))
                else:
                    logger.info('run task, report request success')
            logger.info('run task, result_Mapping: {}'.format(flow_run_result))
        except Exception as e:
            logger.error('run task, error, {}'.format(e))


def init_task_runner():
    task_executor.submit(run_task)


app = Flask(__name__)

if __name__ == '__main__':
    logger.add(
        "logs/workflow.log",  # 日志文件
        rotation='100 MB', retention='10 days', compression="zip",  # 最大10M, 保留10天, 压缩ZIP
        enqueue=True,  # 多进程安全, 防止阻塞
    )

    logger.info('程序初始化 ...')
    init_scheduled_job()
    init_task_runner()
    post_task()
    logger.info('初始化结束 ...')
    # use_reloader=False 禁用自动重载，防止定时器触发两次
    app.run(host='0.0.0.0', port=9090, debug=True, use_reloader=False)
