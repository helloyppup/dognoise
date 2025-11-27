import subprocess
import os
import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.process = None
        self.file_handle = None  # 手动管理文件句柄
        self.current_date = None  # 记录当前日志文件的日期

    def _get_new_filepath(self):
        """
        辅助方法：生成带当前时间戳的新文件名
        """
        # 获取用户定义的前缀，默认是 monitor
        prefix = self.kwargs.get("filename_prefix", "monitor")

        # 生成文件名：monitor_20231127_120000.log
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.log"

        log_dir = os.path.join(self.context.root_dir, "outputs", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return os.path.join(log_dir, filename)

    def _rotate_log(self):
        """
        执行日志切分动作：关旧的 -> 开新的
        """
        # 1. 关闭旧文件
        if self.file_handle:
            try:
                self.file_handle.flush()
                self.file_handle.close()
            except Exception as e:
                logger.error(f"关闭旧日志失败: {e}")

        # 2. 生成新路径
        new_path = self._get_new_filepath()

        # 3. 更新父类属性 (这样 stop() 的时候只会上传这最后一个文件，避免上传几十个)
        self.output_file = new_path
        self.current_date = time.strftime("%Y%m%d")  # 更新当前日期标记

        # 4. 打开新文件
        self.file_handle = open(new_path, "w", encoding="utf-8")
        logger.info(f"🔄 [LogMonitor] 日志已切分 -> {os.path.basename(new_path)}")

    def working(self):
        """
        长任务模式：启动 logcat 进程，持续读取流，并按天切分
        """
        keywords = self.kwargs.get("keywords", [])
        if isinstance(keywords, str): keywords = [keywords]

        device_id = self.context.adb.device_id
        cmd_prefix = f"adb -s {device_id}" if device_id else "adb"

        # 1. 先清空缓冲区
        subprocess.run(f"{cmd_prefix} logcat -c", shell=True)

        # 2. 启动进程
        cmd = f"{cmd_prefix} logcat -v time"
        self.process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='ignore'
        )

        logger.info("🐕 [LogMonitor] 开始监听 (支持自动切分)")

        # 3. 初始化第一个日志文件
        self._rotate_log()

        # 性能优化：不需要每毫秒都检查时间，每写 100 行或者每隔几秒检查一次即可
        # 这里简单处理：每次循环检查一次，因为 Python 的 time.strftime 开销还可以接受

        try:
            while True:
                if self.is_stopped(): break

                # --- 📅 切分检查逻辑 ---
                # 只有日期变了（跨天）才切分
                now_date = time.strftime("%Y%m%d")
                if now_date != self.current_date:
                    self._rotate_log()
                # ---------------------

                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break

                if line:
                    self.file_handle.write(line)
                    self.file_handle.flush()  # 实时写入

                    for kw in keywords:
                        if kw in line:
                            # 发现异常，不仅打印，还可以把异常写入一个单独的 error.log
                            logger.error(f"🚨 [LogMonitor] 捕获异常: {kw}")
                            self.alert(line)

        except Exception as e:
            logger.error(f"🐕 [LogMonitor] 监听崩溃: {e}")
        finally:
            # 4. 清理工作：关文件、杀进程
            if self.file_handle:
                self.file_handle.close()
            self._kill_process()
            logger.info("🐕 [LogMonitor] 停止工作")

    def _kill_process(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass

    def stop(self):
        self._kill_process()
        return super().stop()