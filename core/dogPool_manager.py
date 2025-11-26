import os
import importlib.util
import allure
from libs.logger import logger

class DogPoolManager:
    def __init__(self, context):
        self.context = context
        self.root_dir = context.root_dir
        self.active_dog={}

    def start(self,dog_name,**kwargs):
        if dog_name  in self.active_dog:
            logger.warning(f"dog {dog_name} 已出动，勿重复调用")
            return

        # 动态加载文件
        file_path = os.path.join(self.root_dir,"actions" ,"dogs",f"{dog_name}.py")
        if not os.path.exists(file_path):
            logger.warning(f"找不到狗{file_path}")
            return

        try:
            spec = importlib.util.spec_from_file_location(dog_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "Dog"):
                dog_instance = module.Dog(self.context, **kwargs)
                dog_instance.start()

                self.active_dog[dog_name] = dog_instance
            else:
                logger.warning(f"<没找到>{dog_name} <中的dog类>")

        except Exception as e:
            logger.error(f"<<启动狗失败>>{dog_name}---{e}")

    def stop(self, dog_name):
        dog = self.active_dog.get(dog_name)
        if not dog:
            logger.warning(f"<<dog不存在>>{dog_name} <无法停止运行>")
            return

        # 1. 停止狗 (触发 kill process)
        file_path = dog.stop()
        del self.active_dog[dog_name]

        # 2. 处理产物
        if file_path and os.path.exists(file_path):
            logger.info(f"{dog_name}<狗叼回来一些东西...>{file_path}")

            # 智能推断类型
            att_type = self._infer_attachment_type(file_path)

            # 🔥【核心修复】策略分流
            # 只有图片才读内存，Log文件只贴路径！

            # 📷 场景 A: 图片 -> 读取并上传原图
            if att_type in [allure.attachment_type.PNG, allure.attachment_type.JPG]:
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    allure.attach(content, name=f"{dog_name}_截图", attachment_type=att_type)
                except Exception as e:
                    logger.error(f"图片上传失败: {e}")

            # 📝 场景 B: 日志/其他 -> 只上传路径字符串 (彻底解决 OOM 问题)
            else:
                # 获取绝对路径，方便复制
                abs_path = os.path.abspath(file_path)
                # 构造一段提示文本
                note = f"📂 文件过大，为防止报告崩溃，未直接展示。\n\n请在本地查看:\n{abs_path}"

                # ⚠️ 注意：这里上传的是 note 变量，不是文件内容！
                allure.attach(
                    note,
                    name=f"🔗 路径_{dog_name}",
                    attachment_type=allure.attachment_type.TEXT
                )


    def stop_all(self):
        # 收狗
        for name in list(self.active_dog.keys()):
            self.stop(name)

    def _infer_attachment_type(self, file_path):
        """
        内部方法：根据文件后缀名，决定 Allure 的附件类型
        """
        # 获取后缀名 (如 .log, .png)
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # 🗺️ 映射表：把后缀名映射到 Allure 类型
        mapping = {
            ".png": allure.attachment_type.PNG,
            ".jpg": allure.attachment_type.JPG,
            ".jpeg": allure.attachment_type.JPG,
            ".txt": allure.attachment_type.TEXT,
            ".log": allure.attachment_type.TEXT,
            ".json": allure.attachment_type.JSON,
            ".xml": allure.attachment_type.XML,
            ".html": allure.attachment_type.HTML,
            ".csv": allure.attachment_type.CSV,
            ".mp4": allure.attachment_type.MP4,
        }

        # 如果找不到，默认用 TEXT (因为 TEXT 最安全，ANY 容易被忽略)
        # 或者你可以把默认值改回 ANY，看你喜好
        return mapping.get(ext, allure.attachment_type.TEXT)
