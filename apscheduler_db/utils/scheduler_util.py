import importlib
import asyncio
from functools import wraps
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Tuple, Dict
from apscheduler.job import Job


def import_function(dotted_path: str):
    """
    从字符串路径导入函数，如 'app.tasks.request_amz#send_request_amz'
    """
    if '#' not in dotted_path:
        raise ValueError("路径必须包含 '#'，例如 'module.submodule#function_name'")
    
    module_path, func_name = dotted_path.split('#', 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)

    if not callable(func):
        raise TypeError(f"{func_name} 不是可调用对象")
    
    return func

def run_in_executor_pool(pool: ProcessPoolExecutor | ThreadPoolExecutor):
    """
    将同步函数包装为异步函数，运行在指定的进程池中。
    可用于 APScheduler 中调度 CPU 密集任务。
    """
    def decorator(sync_func):
        @wraps(sync_func)
        async def async_wrapper(*args, **kwargs):
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(pool, sync_func, *args, **kwargs)
        return async_wrapper
    return decorator

def build_sync_executor_pool(pool: ProcessPoolExecutor | ThreadPoolExecutor, sync_func: Any):
    '''
    构建一个在指定进程池中执行的同步任务
    '''
    async def async_wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(pool, sync_func, *args, **kwargs)
    return async_wrapper



def extract_trigger_info(job: Job) -> Tuple[str, Dict]:
    """
    获取 job 的 trigger 类型和参数
    """
    trigger = job.trigger
    trigger_type = trigger.__class__.__name__.replace('Trigger', '').lower()
    trigger_args = trigger.__getstate__()  # 会返回一个 dict
    return trigger_type, trigger_args


def is_trigger_changed(existing_job: Job, new_trigger_type: str, new_trigger_args: Dict) -> bool:
    """
    比较已有任务和新任务的 trigger 类型 + 参数是否有变化
    """
    existing_type, existing_args = extract_trigger_info(existing_job)

    # 类型不同，肯定变了
    if existing_type != new_trigger_type:
        return True

    # 只比较各 trigger 类型支持的关键字段
    trigger_keys_map = {
        'interval': ['weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'end_date', 'timezone', 'jitter'],
        'cron': ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second',
                 'start_date', 'end_date', 'timezone', 'jitter'],
        'date': ['run_date', 'timezone'],
    }

    keys_to_compare = trigger_keys_map.get(new_trigger_type.lower(), [])
    for key in keys_to_compare:
        if existing_args.get(key) != new_trigger_args.get(key):
            return True  # 有字段不同
    return False  # 完全相同