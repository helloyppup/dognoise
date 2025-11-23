from libs.logger import logger


def run(context):
    """
    Airtest 通用积木：从 data 中读取名字并运行
    """
    # 1. 获取要跑的脚本名字 (从 context.data 中拿)
    target_script = context.data.get("air_script")

    if not target_script:
        logger.error("未指定 air_script 参数")
        return False


    # 2. 委托给 AirRunner 引擎去跑
    # 引擎会自动处理 路径查找、using、import、reload
    return context.air.run(target_script)