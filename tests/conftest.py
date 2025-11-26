import os

import pytest
from core.context import TestContext
from libs.logger import logger


@pytest.fixture(scope="session")
def env():
    """
    这是一个 Fixture（夹具）。
    scope="session" 表示整个测试过程只创建一次 Context，
    所有测试用例共享这个环境（不用每次都重新连ADB，省时间）。
    """
    logger.info(">>> [Fixture] 初始化测试环境 (Context) ...")

    # 1. 创建背包
    context = TestContext()

    # 2. 把背包交给测试用例 (Yield)
    yield context

    # 3. 测试结束后的清理工作 (Teardown)
    logger.info(">>> [Fixture] 测试结束，环境清理 ...")
    if hasattr(context, "dogs"):
        context.dogs.stop_all()
    # 这里以后可以写：断开ADB连接、生成最终报告等


@pytest.fixture(scope="function", autouse=True)
def auto_cleanup_dogs(env):
    """
    【自动清场】
    每个测试用例开始前：什么都不做
    每个测试用例结束后：强制把所有狗收回来！
    """
    yield  # 这里是测试用例执行的时间

    # --- 用例执行完后 ---
    if hasattr(env, "dogs"):
        # 停止所有狗，并自动上传附件到当前测试用例报告中
        env.dogs.stop_all()


def pytest_sessionfinish(session, exitstatus):
    """
    当整个测试会话结束（所有用例跑完）时，自动调用此钩子。
    我们在这里执行 allure generate 命令。
    """
    logger.info("正在生成 Allure HTML 报告快照...")

    # 1. 定义源数据目录 (和你 pytest.ini 里配置的一致)
    source_dir = "./outputs/allure_results"

    # 2. 定义快照存放目录 (每次运行都会覆盖这个文件夹)
    report_dir = "./outputs/allure_report"

    # 3. 调用系统命令生成报告
    # --clean 表示生成前清空 report_dir，保证是最新快照
    exit_code = os.system(f"allure generate {source_dir} -o {report_dir} --clean")

    if exit_code == 0:
        logger.info(f"✨ 报告快照已生成！请打开: {report_dir}/index.html")
    else:
        logger.error("❌ 报告生成失败，请检查是否安装了 Allure 命令行工具。")