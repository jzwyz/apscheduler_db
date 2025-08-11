# apscheduler-db

一个通用的apscheduler数据库配置服务

环境变量配置示例

```env
# 调度服务的名称
scheduler_app_name=DefaultAppTask
# 调度服务数据库链接
scheduler_mysqldb_url=mysql+asyncmy://root:xxxxx@localhost:3306/spider
# 调度服务的缓存数据库链接
scheduler_redisdb_url=redis://:xxxxx@localhost:6379/0
# 允许这次任务延迟执行的最大时间（单位：秒），默认配置，可选
scheduler_default_misfire_grace_time=3600
# 合并任务，默认配置，可选
scheduler_default_coalesce=true
# 替换已存在任务，默认配置，可选
scheduler_default_replace_existing=false
# 时区，默认配置，可选
scheduler_default_timezone="Asia/Shanghai"
# 最大实例数，默认配置，可选
scheduler_default_max_instances=1
# 线程数，默认配置，可选
scheduler_default_thread=30
# 进程数，默认配置，可选
scheduler_default_process=10
```
