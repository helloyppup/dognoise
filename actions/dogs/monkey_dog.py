import subprocess
import os
import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def working(self):
        """
        Monkey 压测狗：执行 Monkey 命令，并为每一行日志添加时间戳
        """
        # --- 1. 获取参数 ---
        package_name = self.kwargs.get("package_name")
        if not package_name:
            logger.error("❌ [MonkeyDog] 必须指定 package_name")
            return

        # 事件数量，默认 100万次 (尽可能跑得久)
        count = self.kwargs.get("count", 1000000)
        # 事件间隔，默认 300ms
        throttle = self.kwargs.get("throttle", 300)
        # 种子值，用于复现
        seed = self.kwargs.get("seed", int(time.time()))

        # --- 2. 准备日志文件 ---
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"monkey_{package_name}_{timestamp}.log"

        log_dir = os.path.join(self.context.root_dir, "outputs", "monkey_logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.output_file = os.path.join(log_dir, filename)

        # --- 3. 组装 Monkey 命令 ---
        # --ignore-crashes --ignore-timeouts: 即使崩溃也不停止 Monkey 进程 (由我们自己监控)
        # -v -v -v: 最详细日志
        device_id = self.context.adb.device_id
        prefix = f"adb -s {device_id}" if device_id else "adb"

        cmd = (
            f"{prefix} shell monkey "
            f"-p {package_name} "
            f"--throttle {throttle} "
            f"-s {seed} "
            f"--ignore-crashes --ignore-timeouts --ignore-security-exceptions "
            f"-v -v -v {count}"
        )

        logger.info(f"🐒 [MonkeyDog] 开始压测: {package_name}")
        logger.info(f"📜 命令: {cmd}")
        logger.info(f"💾 日志(带时间戳): {self.output_file}")

        # --- 4. 执行并实时处理日志 ---
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 把错误流也合并进来
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                # 写入头部信息
                f.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Command: {cmd}\n")
                f.write("-" * 50 + "\n")

                while True:
                    # 1. 检查是否被叫停
                    if self.is_stopped():
                        logger.info("🐒 [MonkeyDog] 收到停止信号，正在终止 Monkey...")
                        break

                    # 2. 读取一行输出
                    line = process.stdout.readline()

                    # 3. 判断进程是否结束
                    if not line and process.poll() is not None:
                        logger.info("🐒 [MonkeyDog] Monkey 任务自然结束")
                        break

                    if line:
                        # 【核心黑魔法】 添加时间戳
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        timestamped_line = f"[{current_time}] {line}"

                        # 写入文件
                        f.write(timestamped_line)

                        # 实时报警检测 (可选)
                        # 如果 Monkey 输出里包含 Crash 信息，直接调用父类的 alert
                        if "// CRASH:" in line or "// NOT RESPONDING:" in line:
                            logger.error(f"🐒 [MonkeyDog] 发现异常: {line.strip()}")
                            self.alert(line)

        except Exception as e:
            logger.error(f"🐒 [MonkeyDog] 执行出错: {e}")
        finally:
            # 5. 确保杀掉 Monkey 进程
            # 注意：简单 kill Popen 对象只能杀掉 adb 客户端，杀不掉手机里的 com.android.commands.monkey
            # 所以我们需要发送 shell 命令去杀手机里的进程
            self._kill_remote_monkey()

            if process.poll() is None:
                process.terminate()
            logger.info("🐒 [MonkeyDog] 停止工作")

    def _kill_remote_monkey(self):
        """辅助方法：杀掉手机里的 monkey 进程"""
        try:
            logger.info("正在清理手机端的 monkey 进程...")
            # 获取 monkey 的 pid
            # 不同安卓版本 ps 命令格式可能不同，这里用比较通用的 grep
            check_cmd = "ps -ef | grep com.android.commands.monkey"
            output = self.context.adb.shell(check_cmd)

            if output:
                # 简单的 split 提取 pid (通常在第二列)
                # 这是一个粗略的实现，生产环境可能需要更严谨的正则
                parts = output.split()
                if len(parts) > 1:
                    pid = parts[1]
                    self.context.adb.shell(f"kill {pid}")
                    logger.info(f"已 Kill 远程 Monkey PID: {pid}")
        except Exception as e:
            logger.warning(f"清理远程 Monkey 失败 (可能已自动退出): {e}")