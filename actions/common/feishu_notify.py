def run(context,**kwargs):
    """
    飞书通知球
    """
    # 1. 获取消息内容
    # 优先从直接传参里拿 (kwargs)，如果没传，再从上下文数据里拿 (context.data)
    msg = kwargs.get("message") or context.data.get("message")

    if not msg:
        project = context.config.get("project_name", "Dognoise")
        msg = f"【{project}】\n🤖 自动化测试流程已执行完毕。\n请检查测试报告。"

    context.logger.info(">>> 正在发送飞书通知...")

    # 2. 调用底层工具发送
    # 注意：这里要用 context.feishu (确保 context.py 里加了 feishu 属性)
    if hasattr(context, "feishu"):
        return context.feishu.send_text(msg)
    else:
        context.logger.error("❌ Context 中未找到 feishu 模块，请检查 core/context.py")
        return False