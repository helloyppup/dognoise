import subprocess
import os
import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    # 1. 🔥【新增】初始化方法，注册 self.process
    def __init__(self, context, *args, **kwargs):
        super().__init__(context, *args, **kwargs)
        self.process = None  # 先占个位

    def working(self):
        # ... 参数获取 ...
        keywords = self.kwargs.get("keywords", [])
        if isinstance(keywords, str): keywords = [keywords]

        filename = self.kwargs.get("filename", f"monitor_{time.strftime('%H%M%S')}.log")
        log_dir = os.path.join(self.context.root_dir, "outputs", "logs")
        if not os.path.exists(log_dir): os.makedirs(log_dir)

        # 🔥【关键】必须把路径给父类，否则 Allure 找不到文件！
        self.output_file = os.path.join(log_dir, filename)

        device_id = self.context.adb.device_id
        cmd_prefix = f"adb -s {device_id}" if device_id else "adb"
        cmd = f"{cmd_prefix} logcat -v time"

        logger.info(f"🐕 [LogMonitor] 开始: {filename}")

        # 2. 🔥【修改】把 process 变成 self.process
        self.process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', errors='ignore'
        )

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                while True:
                    if self.is_stopped(): break

                    # 3. 🔥【修改】这里也要用 self.process
                    line = self.process.stdout.readline()

                    if not line and self.process.poll() is not None:
                        break

                    if line:
                        f.write(line)
                        f.flush()

                        # 关键字监控逻辑
                        for kw in keywords:
                            if kw in line:
                                logger.error(f"🚨 发现异常: {kw}")
                                self.alert(line)

        except Exception as e:
            logger.error(f"🐕 [Monitor] Error: {e}")
        finally:
            self._kill_process()
            logger.info("🐕 [Monitor] 停止")

    def _kill_process(self):
        """辅助清理函数"""
        # 4. 🔥【修改】这里访问 self.process 就不报错了
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass

    def stop(self):
        # 必须先杀进程 (拔网线)
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass
        # 再调用父类 stop (等待线程结束 + 关闭文件)
        return super().stop()