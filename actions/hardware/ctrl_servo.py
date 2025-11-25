from libs.servo_kit import ServoKit

def run(context,serials_name='nano'):
    svr=context.serials.get(serials_name)

    if not svr:
        context.logger.error(f"❌ 找不到 {serials_name} 串口，请检查 config.yaml")
        return False

    bot=ServoKit(svr)

    context.logger.info(">>> 开始执行舵机控制")

    # --- 场景 1：简单的点击电源键 (舵机0) ---
    # press_angle=30 是按下角度，idle_angle=0 是抬起角度
    bot.click(servo_id=0, press_angle=90, idle_angle=0)
    #
    # # --- 场景 2：长按音量键 (舵机1) ---
    # bot.long_press(servo_id=1, duration=3.0)
    #
    # # --- 场景 3：来回扫动测试 (舵机0) ---
    # bot.sequence(servo_id=0, angles=[0, 45, 90, 45, 0], interval=0.2)

    return True



