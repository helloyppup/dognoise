import threading
import time
from libs.logger import logger

# 继承threading.Thread
class BaseDog(threading.Thread):
    def __init__(self, context, *args, **kwargs):
        super().__init__()
        self.context = context
        self.args = args
        self.kwargs = kwargs

        # 控制线程停止的信号
        self._stop_event = threading.Event()

        # 结果文件路径 (让子类去赋值)
        self.output_file = None

    def run(self):
        """
        线程启动后自动运行这里
        """
        logger.info(f"🐕‍🦺🐕‍🦺 [dog出动] {self.__class__.__name__} 已启动...")
        while not self._stop_event.is_set():
            try:
                self.working()  # 调用子类的动作
            except Exception as e:
                logger.error(f"🐕‍🦺🐕‍🦺 [dog出错] {e}")
                time.sleep(1)  # 出错休息一下防止刷屏
        logger.info(f"🐕‍🦺🐕‍🦺 [收狗] {self.__class__.__name__} 循环结束。")

    def stop(self):
        """
        外部调用这个方法来停止线程
        """
        self._stop_event.set()
        self.join(timeout=2)  # 等待线程安全结束 这2s等待事件 最多两秒
        return self.output_file

    def is_stopped(self):

        return self._stop_event.is_set()

    def working(self):

        raise NotImplementedError("必须在子类实现 working 方法")