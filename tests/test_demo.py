# tests/test_demo.py
from tornado.gen import sleep

from libs.adb_manager import ADBManager
from libs.logger import logger

import pytest
from core.runner import RunnerDog
from time import sleep
from libs.logger import logger


def test_workflow(env):
    logger.info("=== 开始执行业务流测试 ===")
    # 启动烦人狗
    env.dogs.start("chaos_dog", interval=0.5)

    # 1. 调用：连接设备
    # 我们不需要知道 connect_device.py 在哪个文件夹，只要喊名字
    result = env.run("connect_devices")
    sleep(10)

    env.dogs.stop("chaos_dog")

    # 2. 根据积木的返回值做断言
    if result:
        logger.info("设备检查通过，准备进行下一步...")
    else:
        logger.warning("设备检查未通过，但在演示模式下我们继续...")

    # 3. 你还可以继续调用之前的 hello_world
    env.run("hello_pupply")

    logger.info("=== 业务流测试结束 ===")

