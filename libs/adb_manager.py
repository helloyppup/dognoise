import subprocess
from libs.logger import logger  # 引入刚才写的日志工具


class ADBManager:
    def run_cmd(self, cmd):
        """
        内部函数：专门用来执行 Shell 命令，并获取结果
        """
        logger.info(f"执行命令: {cmd}")  # 记录我们干了什么

        # subprocess 是 Python 用来调用系统命令的模块
        # capture_output=True 表示我们要把命令的输出抓回来，而不是直接丢到屏幕上
        # text=True 表示结果是字符串，不是二进制
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"命令执行失败: {result.stderr}")
            return None

        return result.stdout.strip()

    def connect(self, ip_address):
        """
        连接指定设备的公共方法
        """
        output = self.run_cmd(f"adb connect {ip_address}")
        if output and "connected" in output:
            logger.info(f"成功连接到设备: {ip_address}")
            return True
        else:
            logger.error(f"连接设备失败: {ip_address}")
            return False

    def get_devices(self):
        """
        查看当前连接的设备列表
        """
        output = self.run_cmd("adb devices")
        logger.info(f"当前设备列表:\n{output}")
        return output