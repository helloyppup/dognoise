import glob
import logging
import os
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT_DIR, 'outputs',"logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def cleanup_old_logs(max_keep=5):
    """
        清理旧日志的函数
        """
    # 1. 找到目录下所有的 test_*.log 文件
    # glob.glob 会返回一个列表，包含所有匹配的文件路径
    pattern = os.path.join(LOG_DIR, "test_*.log")
    all_logs = glob.glob(pattern)

    # 2. 如果文件数量没有超标，直接返回
    # 我们保留 max_keep - 1 个，因为马上就要创建一个新的了
    if len(all_logs) < max_keep:
        return

    # 3. 按文件的修改时间排序 (从小到大，最旧的在前面)
    # key=os.path.getmtime 表示获取文件的最后修改时间
    all_logs.sort(key=os.path.getmtime)

    # 4. 计算需要删除多少个
    # 比如现在有55个，要保留50个，那就删掉 (55 - 50 + 1) = 6个
    num_to_delete = len(all_logs) - max_keep + 1

    for i in range(num_to_delete):
        file_to_remove = all_logs[i]
        try:
            os.remove(file_to_remove)
            # print(f"已清理旧日志: {file_to_remove}") # 如果嫌控制台太吵，可以注释掉这行
        except Exception as e:
            print(f"清理日志失败: {file_to_remove}, 错误: {e}")

def get_logger(name="LegoFramework"):

    cleanup_old_logs()
    # 1. 创建一个日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # 设置默认级别：只记录INFO及以上的信息

    # 防止重复打印（如果不加这个判断，pytest有时候会打印两遍）
    if not logger.handlers:
        # 2. 定义日志格式：[时间] [级别] [文件名:行号] 信息
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        #  处理器A：输出到控制台（屏幕）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 先执行清理工作
        cleanup_old_logs(max_keep=50)

        # 生成精确到秒的时间戳
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        log_filename = f'test_{timestamp}.log'
        file_path = os.path.join(LOG_DIR, log_filename)

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = get_logger()