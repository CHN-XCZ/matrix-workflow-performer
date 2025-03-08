import queue
from concurrent.futures import ThreadPoolExecutor
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from core.matrix_workflow.workflow_runner.runner import MatrixWorkflowRunner

task_executor = ThreadPoolExecutor(max_workers=10)  # 任务线程池

scheduler = None

task_queue = queue.Queue()

heartbeat_request_url = "http://127.0.0.1:8000/api/v1/heartbeat"


def init_scheduled_job():
    #     TODO: 定时获取graph任务
    global scheduler
    if not scheduler:
        scheduler = BackgroundScheduler()
        scheduler.add_job(scheduler_executor_heartbeat_queue, 'interval', max_instances=1, seconds=5)
        scheduler.start()
        logger.info("定时任务执行")


def scheduler_executor_heartbeat_queue():
    global task_queue
    try:
        # response = requests.get(heartbeat_request_url)
        # if response.status_code != 200:
        #     logger.error('scheduler, heartbeat request error， code != 200, response: {}'.format(response))
        #     return
        # result_arr_json = json.loads(response.text)
        # task_config = result_arr_json['data']
        config = {
            "edges": [{
                "source": "0",
                "target": "1"
            },
            #     {
            #         "source": "1",
            #         "target": "2"
            #     },
            # {
            #     "source": "2",
            #     "target": "3"
            # }
            ],
            "nodes": [{
                "id": "0",
                "type": "start",
                "data": "1"
            }, {
                "id": "1",
                "type": "xhs",
                "data": {
                    "operate_cmd": "4",
                    "task_json": {
                        "title": "hhhkl",
                        "content": "hhhkl",
                        "img_url": "https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpeg",
                        "xhs_url": "67c81f10000000002903e864",
                        "user_id": "6573bf0500000000190138da"
                    }
                }
            },
                # {
                #     "id": "2",
                #     "type": "xhs",
                #     "data": {
                #         "operate_cmd": "2",
                #         "task_json": {
                #             "title": "hhhkl",
                #             "content": "hhhkl",
                #             "img_url": "https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpeg",
                #             "xhs_url": "67c81f10000000002903e864"
                #         }
                #     }
                # },
                # {
                #     "id": "3",
                #     "type": "xhs",
                #     "data": {
                #         "operate_cmd": "3",
                #         "task_json": {
                #             "title": "hhhkl",
                #             "content": "hhhkl",
                #             "img_url": "https://pic1.zhimg.com/v2-abed1a8c04700ba7d72b45195223e0ff_l.jpeg",
                #             "xhs_url": "67c81f10000000002903e864",
                #             "user_id": "6573bf0500000000190138da"
                #         }
                #     }
                # }
            ],
        }
        task_queue.put(config)
    except Exception as e:
        logger.error('scheduler, heartbeat request error, {}'.format(e))


def run_task():
    while True:
        global task_queue
        if task_queue.empty():
            continue
        task_config = task_queue.get()
        logger.info('run task, graph_config: {}'.format(task_config))
        result_Mapping = {}
        MatrixWorkflowRunner(task_config, result_Mapping).run()
        # TODO 调用任务回调接口
        logger.info('run task, result_Mapping: {}'.format(result_Mapping))


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
    logger.info('初始化结束 ...')
    # use_reloader=False 禁用自动重载，防止定时器触发两次
    app.run(host='0.0.0.0', port=9090, debug=True, use_reloader=False)
