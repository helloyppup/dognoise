import subprocess
import time
import os
from libs.logger import logger


class ADBManager:
    def __init__(self, device_id=None):
        """
        :param device_id: 设备序列号或IP (例如 "192.168.1.101" 或 "emulator-5554")
        """
        self.device_id = device_id
        # 如果是IP设备，记录下来以便断线重连 非无线的无法重连
        self.is_network_device = "." in device_id if device_id else False

    def run_cmd(self, cmd, retry=1):
        """
        执行 ADB 命令（带重试机制）
        :param cmd: 要执行的命令 (不含 'adb', 例如 'shell ls')
        :param retry: 失败重试次数，默认 1 次
        """
        # -s 指定某个设备
        prefix = f"adb -s {self.device_id}" if self.device_id else "adb"
        full_cmd = f"{prefix} {cmd}"

        for i in range(retry + 1):
            try:
                logger.info(f"执行: {full_cmd}")
                # 使用 subprocess 执行
                result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

                # 检查结果
                if result.returncode == 0:
                    return result.stdout.strip()

                # 错误处理与重连判定
                error_msg = result.stderr.lower()
                if "device not found" in error_msg or "offline" in error_msg:
                    logger.warning(f"⚠️ 设备连接异常 ({error_msg})，尝试重连...")
                    self.reconnect()
                else:
                    logger.error(f"命令失败: {result.stderr.strip()}")
                    # 非连接错误，直接返回，不重试
                    return None

            except Exception as e:
                logger.error(f" 执行异常: {e}")

            # 如果是最后一次循环还没成功，就不用 sleep 了
            if i < retry:
                time.sleep(2)

        return None

    def reconnect(self):
        """
        尝试恢复连接：重启 Server -> 重连网络设备
        """
        logger.info("执行 ADB 重连流程...")

        # 暴力重启 ADB Server ⚠️⚠️  此处会影响所有设备，需要优化
        subprocess.run("adb kill-server", shell=True)
        time.sleep(1)
        subprocess.run("adb start-server", shell=True)
        time.sleep(2)

        # 如果是网络设备，重新 connect
        if self.is_network_device and self.device_id:
            logger.info(f"正在重新连接网络设备: {self.device_id}")
            # 这里调用原生 adb connect，不走 self.run_cmd 避免死循环
            subprocess.run(f"adb connect {self.device_id}", shell=True)
            time.sleep(2)  # 等待连接建立

    # ================= 常用快捷指令 =================

    def shell(self, cmd):
        """
        执行 shell 命令 (自动添加 'shell' 前缀)
        用法: env.adb.shell("ls /sdcard")
        """
        return self.run_cmd(f"shell {cmd}")

    def get_logcat(self, output_path, grep=None):
        """
        输出logcat 直接将流重定向到文件，不占用内存
        """
        # -d “Dump the log and exit”（倒出当前缓冲区的内容然后退出）
        cmd = "logcat -d"
        if grep:
            cmd += f" | grep '{grep}'"

        # 手动组装带前缀的完整命令
        prefix = f"adb -s {self.device_id}" if self.device_id else "adb"
        full_cmd = f"{prefix} {cmd}"

        try:
            logger.info(f"正在抓取 Logcat 到文件: {output_path}")

            # 打开文件句柄，作为 stdout 的接收端
            with open(output_path, "w", encoding="utf-8", errors="ignore") as f:
                # 执行命令，stdout=f 表示直接写进文件
                result = subprocess.run(full_cmd, shell=True, stdout=f, stderr=subprocess.PIPE)
            # 检查结果
            if result.returncode == 0:
                logger.info(f"✅ Logcat 已保存: {output_path}")
                return True
            else:
                logger.error(f" Logcat 保存失败")
                return False

        except Exception as e:
            logger.error(f"Logcat 执行异常: {e}")
            return False

    def ping_gateway(self, target="8.8.8.8", count=4):
        """
        让手机 ping 外部地址
        """
        logger.info(f"🌏 正在 Ping {target}...")
        # Android 的 ping 默认是不停的，必须加 -c 限制次数
        output = self.shell(f"ping -c {count} {target}")

        if output and "0% packet loss" in output:
            logger.info("✅ 网络通畅")
            return True
        else:
            logger.warning("❌ 网络不通或有丢包")
            return False

    def connect(self):
        """手动连接 (初始化用)"""
        if self.is_network_device:
            self.run_cmd(f"connect {self.device_id}")