# 核心上下文
import os

from libs.logger import logger
from libs.adb_manager import ADBManager
from core.runner import RunnerDog
from core.dogPool_manager import DogPoolManager

class TestContext:
    def __init__(self):
        self.logger = logger
        self.adb = ADBManager()
        self.data={}
        self.runner=RunnerDog()
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dogs = DogPoolManager(self)


    def run(self, keyword):
        """
        调用env.run() 实际上调用扫描狗 把自己（整个实例）作为context传入
        :param keyword:
        :return:
        """
        return self.runner.run(keyword,context=self)

