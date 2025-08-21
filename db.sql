CREATE TABLE `scheduler_jobs` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `func_id` varchar(100) NOT NULL COMMENT '任务ID，唯一',
    `func` varchar(255) NOT NULL COMMENT '调度任务执行的函数: app.tasks.request_amz#send_request_amz',
    `name` varchar(100) DEFAULT NULL COMMENT '任务名称',
    `trigger` varchar(20) NOT NULL DEFAULT 'date' COMMENT '任务触发方式: date/cron/interval',
    `trigger_args` json DEFAULT NULL COMMENT '任务触发参数',
    `args` json DEFAULT NULL COMMENT '数组形式的参数',
    `kwargs` json DEFAULT NULL COMMENT '字典形式的参数',
    `coalesce` tinyint(1) NOT NULL DEFAULT '1' COMMENT '合并错过的任务',
    `executor` varchar(50) NOT NULL DEFAULT 'default' COMMENT '执行器：default/thread/process，默认使用线程池执行',
    `replace_existing` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否允许替换存在的任务',
    `misfire_grace_time` int NOT NULL DEFAULT '3600' COMMENT '任务延迟容忍度，默认1小时，单位秒',
    `max_instances` int NOT NULL DEFAULT '1' COMMENT '最大实例数',
    `timezone` varchar(50) NOT NULL DEFAULT 'Asia/Shanghai' COMMENT '调度任务执行时区',
    `user_id` int DEFAULT NULL COMMENT '用户ID',
    `valid` int NOT NULL DEFAULT '0' COMMENT '是否有效',
    `unique_key` varchar(100) DEFAULT NULL COMMENT '计算任务参数的唯一标识',
    `log_storage_days` int NOT NULL DEFAULT '3' COMMENT '保留日志周期，默认7天，最长30天',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `func_id` (`func_id`)
) COMMENT = '调度任务配置表';

CREATE TABLE scheduler_jobs_logger (
    `id` BIGINT NOT NULL COMMENT '主键ID' AUTO_INCREMENT,
    `job_id` VARCHAR(100) NOT NULL COMMENT '任务ID',
    `event` VARCHAR(20) NOT NULL COMMENT '事件类型: job_executed/job_error/log_[info|error|waring|success]',
    `scheduled_run_time` TIMESTAMP NOT NULL COMMENT '调度时间' DEFAULT CURRENT_TIMESTAMP,
    `execution_time` FLOAT COMMENT '任务执行耗时（秒）',
    `message` TEXT NULL COMMENT '日志消息',
    `created_at` TIMESTAMP NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX idx_job_id_created_at (job_id, created_at)
) COMMENT = '调度日志表';