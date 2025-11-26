from libs.logger import logger


def run(context, **kwargs):
    """
    Airtest 通用积木：运行指定的 .air 脚本
    """
    # 【防御策略 2：自动补位】
    # 优先看有没有显式传参（env.run("run_air", air_scripts="login")）
    # 如果没传，再去 context 百宝箱里捞（适用于积木串联场景）
    target_script = kwargs.get("air_scripts") or context.data.get("air_scripts")

    # 【防御策略 1：卫语句拦截】
    if not target_script:
        return {
            "status": False,
            "data": None,
            "msg": "❌ 失败：未指定 'air_scripts' 参数 (请通过参数或 Context 传入)"
        }

    try:
        # 委托给引擎跑
        # 注意：这里我们把 kwargs 也透传进去
        raw_result = context.air.run(target_script, **kwargs)

        # 【防御策略 3：输出标准化】
        # AirRunner 如果失败通常返回 False (根据你的 core/air_runner.py 逻辑)
        if raw_result is False:
             return {
                "status": False,
                "data": None,
                "msg": f"❌ Airtest 脚本 [{target_script}] 执行失败 (脚本不存在或运行报错)"
            }

        # 如果成功，把脚本原本的返回值 (__retval__) 放在 data 里透传出去
        return {
            "status": True,
            "data": raw_result,
            "msg": f"Airtest [{target_script}] 执行完毕"
        }

    except Exception as e:
        # 兜底异常
        return {
            "status": False,
            "data": str(e),
            "msg": f"❌ 调用 AirRunner 发生异常: {e}"
        }