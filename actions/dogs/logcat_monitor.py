import subprocess
import os
import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def working(self):
        """
        长任务模式：启动 logcat 进程，持续读取流
        """
        # 准备参数
        # 想要监听的关键字列表，例如 ["FATAL", "ANR", "CRASH"]
        on_alert_callback = self.kwargs.get("on_alert")


        keywords = self.kwargs.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [keywords]


        # 保存的文件名
        filename = self.kwargs.get("filename", f"monitor_{time.strftime('%H%M%S')}.log")
        log_dir = os.path.join(self.context.root_dir, "outputs", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.output_file = os.path.join(log_dir, filename)

        # 启动 Logcat 子进程 (非阻塞)
        # -v time: 带时间戳
        device_id = self.context.adb.device_id
        cmd_prefix = f"adb -s {device_id}" if device_id else "adb"
        cmd = f"{cmd_prefix} logcat -v time"

        logger.info(f"🐕 [LogMonitor] 开始监听，全量日志存入: {filename}")
        if keywords:
            logger.info(f"🐕 [LogMonitor] 正在警惕关键字: {keywords}")

        # 使用 Popen 而不是 run，要流式读取，不能等它结束
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'  # 忽略乱码
        )

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                # 死循环读取流
                while True:
                    # 长流程开发 必须手动检查停止信号 不然死循环把狗累死了
                    if self.is_stopped():
                        logger.info("🐕 [LogMonitor] 收到停止信号，正在退下...")
                        break

                    # 读一行
                    line = process.stdout.readline()

                    # 如果流断了（比如拔线了）且没数据了，就退出
                    if not line and process.poll() is not None:
                        logger.warning("🐕 [LogMonitor] Logcat 进程意外结束")
                        break

                    if line:
                        # --- 动作 A: Dump (存盘) ---
                        f.write(line)

                        # --- 动作 B: Find (监控) ---
                        for kw in keywords:
                            if kw in line:
                                # 发现猎物！
                                logger.error(f"🚨 [LogMonitor] 捕获到关键异常: {kw} \n>>> {line.strip()}")
                                self.alert(line)

                        # 稍微让出一点 CPU，防止死循环空转太快
                        time.sleep(0.001)

        except Exception as e:
            logger.error(f"🐕 [LogMonitor] 监听崩溃: {e}")
        finally:
            # 4. 确保杀掉子进程，防止僵尸进程
            if process.poll() is None:
                process.terminate()
                process.kill()
            logger.info("🐕 [LogMonitor] 停止工作")