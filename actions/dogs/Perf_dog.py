import os
import time
import csv
import re
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def working(self):
        """
        性能监控狗：持续采集 CPU 和 内存数据，存入 CSV。
        """
        # 1. 获取配置参数
        package_name = self.kwargs.get("package_name")
        if not package_name:
            logger.error("❌ [PerfDog] 必须指定 package_name 参数！")
            return

        interval = self.kwargs.get("interval", 3)  # 默认 3秒采一次
        filename = self.kwargs.get("filename", f"perf_{package_name}_{time.strftime('%H%M%S')}.csv")

        # 内存报警阈值 (MB)，默认 500MB
        mem_limit = self.kwargs.get("mem_limit", 500)
        on_alert = self.kwargs.get("on_alert")  # 报警回调

        # 准备文件路径
        log_dir = os.path.join(self.context.root_dir, "outputs", "perf_data")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.output_file = os.path.join(log_dir, filename)

        logger.info(f"🐕 [PerfDog] 开始监控: {package_name} (间隔 {interval}s)")
        logger.info(f"💾 数据保存至: {self.output_file}")

        # 2. 长任务循环：打开 CSV 文件准备写入
        try:
            with open(self.output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Time", "CPU(%)", "Memory_PSS(MB)"])  # 表头

                while True:
                    # 检查停止信号
                    if self.is_stopped():
                        logger.info("🐕 [PerfDog] 停止监控")
                        break

                    start_time = time.time()
                    timestamp = time.strftime("%H:%M:%S")

                    # --- 采集数据 (核心逻辑) ---
                    cpu = self._get_cpu(package_name)
                    mem = self._get_mem(package_name)

                    # --- 写入文件 ---
                    if cpu is not None and mem is not None:
                        writer.writerow([int(time.time()), timestamp, cpu, mem])
                        f.flush()  # 立即存盘，防止丢数据

                        # --- 报警检查 ---
                        if mem > mem_limit:
                            logger.warning(f"⚠️ [PerfDog] 内存超标: {mem}MB > {mem_limit}MB")
                            if on_alert:
                                try:
                                    on_alert(f"Memory Leak: {mem}MB")
                                except:
                                    pass

                    # --- 智能等待 ---
                    # 扣除采集消耗的时间，保证间隔准确
                    cost = time.time() - start_time
                    wait_time = max(0, interval - cost)

                    # 使用 wait 代替 sleep，响应更灵敏
                    if self._stop_event.wait(wait_time):
                        break

        except Exception as e:
            logger.error(f"🐕 [PerfDog] 监控崩溃: {e}")

    def _get_cpu(self, pkg):
        """
        获取 CPU 使用率
        【优化】改用 dumpsys cpuinfo，兼容性更好
        """
        try:
            # dumpsys cpuinfo 输出格式通常包含：
            # 0.5% 12345/com.package.name: 0.3% user + 0.1% kernel
            cmd = f"dumpsys cpuinfo | grep {pkg}"
            output = self.context.adb.shell(cmd)

            if output:
                output = output.strip()
                # 策略：找到包含包名的那一行，提取最前面的百分比
                for line in output.split('\n'):
                    if pkg in line:
                        # 移除空格，方便正则提取
                        # 例子: "0.5%12345/com.pkg..."
                        line = line.strip()
                        match = re.search(r'^(\d+(\.\d+)?)%', line)
                        if match:
                            return float(match.group(1))
            return 0.0
        except Exception as e:
            # 调试的时候打开，平时可以静默
            # logger.warning(f"CPU获取失败: {e}")
            return 0.0

    def _get_mem(self, pkg):
        """获取 Total PSS 内存 (MB)"""
        try:
            cmd = f"dumpsys meminfo {pkg} | grep 'TOTAL'"
            output = self.context.adb.run_cmd(cmd)
            # 输出通常是:     TOTAL    123456    ...
            if output:
                # 提取第一串数字
                match = re.search(r'(\d+)', output)
                if match:
                    kb = int(match.group(1))
                    return round(kb / 1024, 2)  # 转为 MB
            return 0
        except:
            return 0