# 这是一个标准的积木文件
# context 参数就是后面我们要传进来的“百宝箱”，里面有 adb 工具什么的
def run(context,**kwargs):
    print(">>> 正在执行 hello_pupply！")
    logger=context.logger
    logger.info(">>> 正在执行 hello_pupply")

    return "Hello Execution Success"