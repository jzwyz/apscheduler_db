import time, math, datetime

from apscheduler_db.core.loggin import logger

def demo_io_task():
    '''
    线程任务 demo
    app.tasks.manage_task#demo_io_task
    '''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("[线程任务] Start task (sleep 2s)... {}", now)
    time.sleep(10)
    logger.info("[线程任务] End task {}", now)

def demo_cpu_task():
    '''
    进程任务 demo
    app.tasks.manage_task#demo_cpu_task
    '''
    logger.info(f"[进程任务] Start CPU-intensive task")
    total = sum(math.sqrt(i) for i in range(10_000_000))
    logger.info(f"[进程任务] Done: total = {total}")