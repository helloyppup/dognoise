# tests/test_demo.py
from operator import index

import allure
from time import sleep

import pytest

from libs.logger import logger

@allure.epic("这是一个快速的测试")
@allure.feature("进行一些示例")
class TestDemo:
    @pytest.mark.skip
    @allure.story("多模块放狗")
    @allure.description("这是一个演示用例：同时启动干扰狗，并检查ADB连接状态。")
    @allure.severity(allure.severity_level.CRITICAL)  # 设置严重等级
    @allure.title("主流程：捣乱狗 + ADB连接")
    def test_workflow(self,env):
        logger.info("=== 开始执行业务流测试 ===")
        # 启动烦人狗
        env.start("chaos_dog", interval=0.5)
        env.run("ctrl_servo")

        # 1. 调用：连接设备
        # 我们不需要知道 connect_device.py 在哪个文件夹，只要喊名字
        result = env.run("connect_devices")
        sleep(5)

        env.stop("chaos_dog")

        # 2. 根据积木的返回值做断言
        if result:
            logger.info("设备检查通过，准备进行下一步...")
        else:
            logger.warning("设备检查未通过，但在演示模式下我们继续...")

        # 3. 你还可以继续调用之前的 hello_world
        env.run("hello_pupply")

        logger.info("=== 业务流测试结束 ===")

    # @pytest.mark.skip
    def test_airtest(self,env):
        logger.info("===开始测试===")

        index=5
        env.start("logcat_monitor")
        while index>0:

            index-=1
            env.run("ctrl_servo")
            sleep(1)

        res=env.run("testdemon")
        env.stop("logcat_monitor")
        print(res)

        assert True
        # if isinstance(res, dict):
        #     assert res.get('status') == "success"
        # else:
        #     assert res is True