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
        error_count = 0
        while not self._stop_event.is_set():
            try:
                self.working()  # 调用子类的动作
                error_count =0
            except Exception as e:
                error_count += 1
                wait_time=min(60,1*(2**(error_count-1)))
                logger.error(f"🐕‍🦺🐕‍🦺 [Dog出错，第{error_count}次重试，等待 {wait_time}s: {e}")
                self.interruptible_sleep(wait_time)  # 出错休息一下防止刷屏
        logger.info(f"🐕‍🦺🐕‍🦺 [收狗] {self.__class__.__name__} 循环结束。")

    def interruptible_sleep(self, seconds):
        """
        可中断的睡眠：如果在睡眠期间收到 stop 信号，会立即醒来。
        返回 True 表示是因为收到信号而醒来（被叫醒），False 表示睡够了自然醒。
        """
        return self._stop_event.wait(timeout=seconds)


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

    def alert(self, msg):
        """
         统一报警接口
        子类只需调用 self.alert("发现异常xxx")，父类负责根据配置决定怎么做。
        """
        # 优先执行：用户传入的自定义回调 (最高优先级)
        # env.start("xxx", on_alert=lambda x: ...)
        callback = self.kwargs.get("on_alert")
        if callback and callable(callback):
            try:
                callback(msg)
            except Exception as e:
                logger.error(f"⚠️ [Dog] 回调执行失败: {e}")

        # 兜底执行：配置化策略
        # env.start("xxx", hook_strategy="stop")
        strategy = self.kwargs.get("hook_strategy")
        if strategy:
            self._apply_strategy(strategy, msg)

    def _apply_strategy(self, strategy, msg):
        """内置的常见策略，免去写回调的麻烦"""

        # 策略 A: 停车 (标记 has_crash)
        if strategy == "stop":
            self.context.data['has_crash'] = True
            logger.error(f"🛑 [策略触发] 致命错误！已标记 has_crash。原因: {msg.strip()}")

        # 策略 B: 截图 (调用 screenshot 积木)
        elif strategy == "screenshot":
            logger.warning(f"[策略触发] 正在截图留证... 原因: {msg.strip()}")
            # screenshot
            # 注意：积木文件名需确保存在，否则会报错
            try:
                self.context.run("screenshot", filename=f"alert_{int(time.time())}.png")
            except Exception as e:
                logger.error(f"截图积木调用失败: {e}")

        # 策略 C: 仅标记 (Soft Failure)
        elif strategy == "mark":
            self.context.data['has_failure'] = True
            logger.warning(f"🚩 [策略触发] 已标记 has_failure: {msg.strip()}")

    def working(self):
        raise NotImplementedError("必须在子类实现 working 方法")