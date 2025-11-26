import subprocess
import os
import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.process = None  # 1. 初始化进程对象

    def working(self):
        """
        长任务模式：启动 logcat 进程，持续读取流
        """
        keywords = self.kwargs.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]

        # 准备文件路径
        filename = self.kwargs.get("filename", f"monitor_{time.strftime('%H%M%S')}.log")
        log_dir = os.path.join(self.context.root_dir, "outputs", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 2. 【关键】把路径赋值给父类，否则管家拿不到路径
        self.output_file = os.path.join(log_dir, filename)

        device_id = self.context.adb.device_id
        cmd_prefix = f"adb -s {device_id}" if device_id else "adb"
        cmd = f"{cmd_prefix} logcat -v time"

        logger.info(f"🐕 [LogMonitor] 开始监听: {filename}")

        # 3. 启动子进程
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                while True:
                    # 检查停止信号
                    if self.is_stopped():
                        break

                    # 4. 读取一行 (如果 stop() 杀了进程，这里会立刻返回空字符串)
                    line = self.process.stdout.readline()

                    # 进程已死且无数据，退出循环
                    if not line and self.process.poll() is not None:
                        break

                    if line:
                        f.write(line)
                        f.flush()  # 实时写入

                        for kw in keywords:
                            if kw in line:
                                logger.error(f"🚨 [LogMonitor] 捕获异常: {kw}")
                                self.alert(line)

        except Exception as e:
            logger.error(f"🐕 [LogMonitor] 监听崩溃: {e}")
        finally:
            self._kill_process()
            logger.info("🐕 [LogMonitor] 停止工作")

    def _kill_process(self):
        """辅助清理函数"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass

    def stop(self):
        # 1. 先杀进程！这就相当于强制让 readline() 返回
        self._kill_process()

        # 2. 再调用父类 stop 等待线程安全退出 (释放文件锁)
        return super().stop()