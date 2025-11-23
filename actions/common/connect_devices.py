def run(context):
    # 1. 从背包里拿出 log 和 adb
    log = context.logger
    adb = context.adb

    log.info("---球球run：检查设备连接 ---")

    # 2. 调用 adb 工具
    # 假设我们先尝试连接一个模拟器或者真机
    # (如果你有真机插着，可以不调用 connect，直接 get_devices)

    # 这里为了演示，我们直接检查当前列表
    # output = adb.get_devices()
    #
    # # 3. 简单的业务逻辑判断
    # if "device" in output and "List of devices attached" in output:
    #     # 统计有几行设备（这只是个粗略的判断逻辑）
    #     lines = output.strip().split('\n')
    #     device_count = len(lines) - 1  # 减去标题行
    #
    #     if device_count > 0:
    #         log.info(f"检测到 {device_count} 台设备在线！")
    #         return True
    #     else:
    #         log.warning("ADB服务正常，但没有连接任何设备！")
    #         return False
    # else:
    #     log.error("ADB服务异常！")
    #     return False
    return