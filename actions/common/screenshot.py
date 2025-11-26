import os
import time
import subprocess
import allure


def run(context, filename=None, device_name=None, **kwargs):
    """
    【优化版】通用截图球：直接流式传输，不占手机空间
    """
    logger = context.logger

    # 1. 确定设备
    if device_name:
        adb = context.adb_pool.get(device_name)
        if not adb:
            logger.error(f"❌ 截图失败：找不到设备 [{device_name}]")
            return False
    else:
        adb = context.adb

    # 2. 准备路径
    save_dir = os.path.join(context.root_dir, "outputs", "screenshots")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if not filename:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.png"
    if not filename.endswith(".png"):
        filename += ".png"

    local_path = os.path.join(save_dir, filename)

    # 3. 【核心优化】直接流式截图
    # exec-out screencap -p 可以直接把图片二进制数据输出到 stdout
    device_id = adb.device_id
    cmd_prefix = f"adb -s {device_id}" if device_id else "adb"
    # 注意：这里我们使用 exec-out (比 shell 更适合传输二进制)
    full_cmd = f"{cmd_prefix} exec-out screencap -p"

    logger.info(f"📸 正在截图(流式): {filename}")

    try:
        with open(local_path, "wb") as f:
            # 直接把命令的标准输出(stdout)写入文件
            process = subprocess.run(full_cmd, shell=True, stdout=f)

        if process.returncode == 0 and os.path.getsize(local_path) > 0:
            logger.info(f"✅ 截图成功: {local_path}")

            # 挂载到报告
            allure.attach.file(
                local_path,
                name=f"截图_{filename}",
                attachment_type=allure.attachment_type.PNG
            )
            return local_path
        else:
            logger.error("❌ 截图失败：文件为空或命令出错")
            return False

    except Exception as e:
        logger.error(f"❌ 截图异常: {e}")
        return False