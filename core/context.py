# 核心上下文
import os

from libs.logger import logger
from libs.adb_manager import ADBManager
from core.runner import RunnerDog
from core.dogPool_manager import DogPoolManager
from functools import cached_property  #Python 3.8+ 支持

from libs.serial_manager import SerialManager
import  yaml


class TestContext:
    def __init__(self):
        self.logger = logger
        self.data={}
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = self._load_config()

    def _load_config(self):
        config_path = os.path.join(self.root_dir, "config.yaml")
        if not os.path.exists(config_path):
            self.logger.warning("⚠️ 找不到 config.yaml，将使用默认配置！")
            return {}

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
                self.logger.info(f"已加载配置文件: {config_path}")
                return cfg
        except Exception as e:
            self.logger.error(f"配置文件读取失败: {e}")
            return {}


    @cached_property
    def adb(self):
        return ADBManager()

    @cached_property
    def runner(self):
        """
        RunnerDog 初始化需要扫描文件 IO，现在被推迟到了第一次调用 env.run() 时。
        """
        return RunnerDog(self)

    @cached_property
    def dogs(self):
        return DogPoolManager(self)

    @cached_property
    def serials(self):
        pool= {}
        serial_config=self.config.get("serials",{})
        self.logger.info(f"⚡ 正在初始化串口池，共 {len(serial_config)} 个配置...")

        for name,config in serial_config.items():
            try:
                sm=SerialManager(
                    port=config.get("port"),
                    baudrate=config.get("baudrate",9600),
                    timeout=config.get("timeout",1),
                )
                pool[name] = sm
                self.logger.info(f"✅ 串口 [{name}] 就绪")
            except Exception as e:
                self.logger.error(f"串口 [{name}] 初始化失败: {e}")

        return pool

    @cached_property
    def adb_pool(self):
        """
        【升级版】返回一个字典，包含所有手机的控制对象
        用法: env.adb_pool['main_phone'].run_cmd(...)
        """
        pool = {}
        adb_conf = self.config.get("adb_devices", {})

        self.logger.info(f"⚡ 正在初始化ADB设备池...")

        for name, ip_or_serial in adb_conf.items():
            # 创建绑定了具体IP的管理器
            manager = ADBManager(device_id=ip_or_serial)
            # 尝试连接 (如果是网络设备)
            manager.connect()

            pool[name] = manager

        return pool

    @property
    def serial(self):
        if not self.serials: return None
        # 返回字典里的第一个 value
        return next(iter(self.serials.values()))


    def run(self, keyword):
        """
        调用env.run() 实际上调用扫描狗 把自己（整个实例）作为context传入
        :param keyword:
        :return:
        """
        return self.runner.run(keyword)

    def start(self, keyword,**kwargs):
        """
        调用env.start() 实际上调用扫描狗 把自己（整个实例）作为context传入
        :param keyword:
        :return:
        """
        return self.dogs.start(keyword,**kwargs)

    def stop(self, keyword,**kwargs):
        """
        停止线程
        :param keyword:
        :return:
        """
        return self.dogs.stop(keyword)