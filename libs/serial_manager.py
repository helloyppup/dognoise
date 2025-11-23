import serial
import time
import threading
from libs.logger import logger


class SerialManager:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self._lock = threading.Lock()  # 加个锁，防止多线程同时写串口打架
        self.connect()

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # 等待设备复位
            logger.info(f"🔌 [串口] 已连接: {self.port} ({self.baudrate})")
        except Exception as e:
            logger.error(f"❌ [串口] 连接失败: {e}")

    def send(self, data: str):
        """
        通用发送方法：只负责发字符串
        """
        if not self.serial or not self.serial.is_open:
            logger.warning("⚠️ 串口未打开，发送失败")
            return

        with self._lock:
            try:
                # 自动补全换行符（如果协议需要的话，或者在外面补也行）
                if not data.endswith('\n'):
                    data += '\n'
                self.serial.write(data.encode('utf-8'))
                # logger.debug(f"📤 [串口发送] {data.strip()}")
            except Exception as e:
                logger.error(f"❌ 发送异常: {e}")

    def read_line(self):
        """
        通用读取方法：读取一行数据
        """
        if not self.serial or not self.serial.is_open:
            return None

        try:
            # readline 会阻塞直到超时，或者读到 \n
            raw = self.serial.readline()
            if raw:
                return raw.decode('utf-8', errors='ignore').strip()
            return None
        except Exception as e:
            logger.error(f"❌ 读取异常: {e}")
            return None

    def close(self):
        if self.serial:
            self.serial.close()