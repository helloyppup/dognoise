import os
import time


def run(context, action="find", keyword=None, filename=None, device_name=None, **kwargs):
    """
    安卓 Logcat 日志操作积木
    :param action: 操作类型 ["clear", "dump", "find"]
    :param keyword: 搜索关键字 (find 模式用)
    :param filename: 保存文件名 (dump 模式用)
    :param device_name: 指定操作哪台手机 (如果不传，默认用 context.adb)
    """
    logger = context.logger

    # 获取指定的 ADB 设备对象 (支持多设备)
    if device_name:
        adb = context.adb_pool.get(device_name)
        if not adb:
            logger.error(f"❌ 找不到设备 [{device_name}]")
            return False
    else:
        adb = context.adb  # 默认设备

    logger.info(f"[Logcat] 对设备执行操作: {action}")

    # --- 场景 A: 清空日志 (Clear) ---
    if action == "clear":
        adb.run_cmd("logcat -c")
        logger.info("🧹 日志缓冲区已清空")
        return True

    # --- 场景 B: 抓取并保存日志 (Dump) ---
    elif action == "dump":
        if not filename:
            # 如果没传文件名，自动生成一个带时间戳的
            timestamp = time.strftime('%H%M%S')
            filename = f"logcat_{timestamp}.txt"

        # 存到 outputs/logs 目录下
        log_dir = os.path.join(context.root_dir, "outputs", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_path = os.path.join(log_dir, filename)

        # 调用 adb_manager 里的现成方法
        result = adb.get_logcat(file_path)
        if result:
            logger.info(f"日志已保存: {file_path}")
            return file_path  # 返回路径供后续使用
        return False

    # --- 场景 C: 查找关键字 (Find/Assert) ---
    elif action == "find":
        if not keyword:
            logger.error("find 模式必须传入 keyword 参数")
            return False

        # 抓取当前所有日志内容（不存文件，直接读内存）
        # logcat -d 表示 dump 当前缓冲区后退出
        content = adb.run_cmd("logcat -d")

        if content and keyword in content:
            logger.info(f"✅ 在日志中找到了: '{keyword}'")
            return {
                "status": True,
                "data": None,
                "msg": ""
            }
        else:
            logger.warning(f"日志中未发现: '{keyword}'")
            return {
                "status": False,
                "data": None,
                "msg": ""
            }

    else:
        logger.error(f"不支持的操作: {action}")
        return {
            "status": False,
            "data": None,
            "msg": ""
        }