import time
from libs.logger import logger

"""舵机控制封装"""
class ServoKit:
    def __init__(self, serial_manager):
        """
        :param serial_manager: 传入一个已经连接好的 SerialManager 对象
        """
        self.serial = serial_manager

    def move(self, servo_id, angle):
        """基础移动"""
        if not self.serial:
            logger.warning("串口未连接，无法控制舵机")
            return

        # 组装协议：ID:ANGLE
        cmd = f"{servo_id}:{angle}"
        self.serial.send(cmd)
        logger.info(f"[舵机{servo_id}] 移动 -> {angle}°")

    def click(self, servo_id, press_angle=45, idle_angle=0, duration=0.2):
        """
        封装【点击】动作：按下 -> 保持 -> 抬起
        """
        logger.info(f"point_up_2: [舵机{servo_id}] 点击 (按压{duration}s)")
        self.move(servo_id, press_angle)  # 按下
        time.sleep(duration)  # 保持
        self.move(servo_id, idle_angle)  # 抬起

    def long_press(self, servo_id, press_angle=45, idle_angle=0, duration=2.0):
        """
        封装【长按】动作
        """
        logger.info(f"timer: [舵机{servo_id}] 长按 {duration}s")
        self.click(servo_id, press_angle, idle_angle, duration)

    def sequence(self, servo_id, angles, interval=0.5):
        """
        封装【连续动作】：传入一串角度，依次执行
        :param angles: 例如 [0, 90, 180, 0]
        """
        logger.info(f"🔄 [舵机{servo_id}] 执行序列动作: {angles}")
        for ang in angles:
            self.move(servo_id, ang)
            time.sleep(interval)