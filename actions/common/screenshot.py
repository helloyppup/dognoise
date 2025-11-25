import os
import time
import allure


def run(context, filename=None, device_name=None, **kwargs):
    """
    通用截图球
    :param filename: 保存的文件名（可选，不传则自动生成时间戳）
    :param device_name: 指定设备（可选，支持多机）
    :return: 截图的绝对路径 or False
    """
    logger = context.logger

    # 确定操作哪台设备 (逻辑和 logcat_ops 一致)
    if device_name:
        adb = context.adb_pool.get(device_name)
        if not adb:
            logger.error(f"❌ 截图失败：找不到设备 [{device_name}]")
            return False
    else:
        adb = context.adb

    # 准备保存路径
    # 统一存放在项目根目录下的 outputs/screenshots 文件夹
    save_dir = os.path.join(context.root_dir, "outputs", "screenshots")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 如果没传文件名，就用 "screenshot_时间戳.png"
    if not filename:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{timestamp}.png"

    # 确保文件名以 .png 结尾
    if not filename.endswith(".png"):
        filename += ".png"

    local_path = os.path.join(save_dir, filename)

    # Android 端的临时路径
    remote_tmp_path = "/sdcard/tmp_screenshot.png"

    logger.info(f"正在截图... 设备: {adb.device_id or 'Default'}")

    try:
        # 执行截图流程 (分三步走，最稳健)

        # 步骤 A: 在手机上截图存到 /sdcard
        # 使用 -p 参数保存为 png 格式
        adb.shell(f"screencap -p {remote_tmp_path}")

        # 步骤 B: 把图片从手机拉取(Pull)到电脑
        # 注意：pull 是 adb 命令，不是 shell 命令，所以用 run_cmd 直接调
        pull_cmd = f"pull {remote_tmp_path} {local_path}"
        adb.run_cmd(pull_cmd)

        # 步骤 C: 清理手机上的临时文件 (不占手机空间)
        adb.shell(f"rm {remote_tmp_path}")

        # 4. 验证结果 & 挂载报告
        if os.path.exists(local_path):
            logger.info(f"✅ 截图已保存: {local_path}")

            # 【Allure 集成】自动把截图贴到测试报告里
            # 这样你打开网页报告就能直接看到图，不用去文件夹找
            allure.attach.file(
                local_path,
                name=f"截图_{filename}",
                attachment_type=allure.attachment_type.PNG
            )
            return local_path
        else:
            logger.error("❌ 截图文件未生成，可能是 ADB 连接问题或存储空间不足")
            return False

    except Exception as e:
        logger.error(f"❌ 截图过程发生异常: {e}")
        return False