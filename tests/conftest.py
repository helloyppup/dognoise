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