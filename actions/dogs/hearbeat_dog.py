import time
from libs.baseDog import BaseDog
from libs.logger import logger


class Dog(BaseDog):
    def working(self):
        """
        💓 心跳守护狗
        每隔一段时间巡检一次所有设备状态。
        """
        # 1. 获取配置
        # 默认每 5 分钟 (300s) 检查一次，太频繁会抢占 ADB 资源
        interval = self.kwargs.get("interval", 300)
        check_network = self.kwargs.get("check_network", True)

        logger.info(f"💓 [HeartbeatDog] 开始巡检 (间隔 {interval}s)...")

        error_msgs = []

        # --- 2. 巡检 ADB 设备 ---
        if self.context.adb_pool:
            for name, adb in self.context.adb_pool.items():
                # A. 检查连接状态
                state = adb.run_cmd("get-state")
                if state != "device":
                    msg = f"❌ 设备 [{name}] 掉线 (状态: {state})"
                    logger.error(msg)
                    error_msgs.append(msg)

                    # 尝试自愈
                    logger.warning(f"🚑 [HeartbeatDog] 正在尝试抢救设备: {name}...")
                    adb.reconnect()

                # B. 检查网络 (如果还连着)
                elif check_network:
                    # ping 百度，只 ping 1 次以节省时间
                    if not adb.ping_gateway("8.8.8.8", count=1):
                        msg = f"⚠️ 设备 [{name}] 网络不通"
                        logger.warning(msg)
                        error_msgs.append(msg)

        # --- 3. 巡检串口设备 ---
        if hasattr(self.context, "serials"):
            for name, mgr in self.context.serials.items():
                if not mgr.serial or not mgr.serial.is_open:
                    msg = f"❌ 串口 [{name}] 连接已断开"
                    logger.error(msg)
                    error_msgs.append(msg)

        # --- 4. 报警处理 ---
        if error_msgs:
            # 汇总错误信息
            alert_text = "🚨 **环境异常报警** 🚨\n" + "\n".join(error_msgs)

            # 调用父类的 alert (触发截图/标记失败等策略)
            self.alert(alert_text)

            # 如果配置了飞书，直接发飞书 (双重保险)
            if hasattr(self.context, "feishu"):
                self.context.feishu.send_text(alert_text)

        # --- 5. 休息 ---
        # 使用可中断睡眠，保证能随时被 stop 叫停
        logger.info("💤 巡检结束，进入休眠...")
        self.interruptible_sleep(interval)