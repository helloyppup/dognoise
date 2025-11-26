# 这是一个标准的积木文件
# context 参数就是后面我们要传进来的“百宝箱”
def run(context, **kwargs):
    logger = context.logger
    logger.info(">>> 正在执行 hello_pupply")

    # 模拟一些业务逻辑
    print(">>> 正在执行 hello_pupply！")

    # 【核心优化】统一返回结构
    # 以后写断言，闭着眼都知道要查 status
    return {
        "status": True,
        "data": "Hello Execution Success",
        "msg": "执行成功，狗狗很开心"
    }