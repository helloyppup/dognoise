# 核心上下文
import os

from libs.logger import logger
from libs.adb_manager import ADBManager
from core.runner import RunnerDog
from core.dogPool_manager import DogPoolManager
from functools import cached_property  #Python 3.8+ 支持

class TestContext:
    def __init__(self):
        self.logger = logger
        self.data={}
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.adb = ADBManager()
        self.runner=RunnerDog(self)

        self.dogs = DogPoolManager(self)

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