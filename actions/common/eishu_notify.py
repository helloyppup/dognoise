def run(context):
    """
    飞书通知积木
    参数来源于 context.data['message']
    """
    # 1. 获取消息内容
    # 优先取 run 传进来的，如果没有就用默认文案
    msg = context.data.get("message")

    if not msg:
        # 如果没有指定内容，自动生成一个简报
        project = context.config.get("project_name", "Dognoise")
        msg = f"【{project}】\n🤖 自动化测试流程已执行完毕。\n请检查测试报告。"

    context.logger.info(">>> 正在发送飞书通知...")

    # 2. 调用底层工具发送
    return context.feishu.send_text(msg)