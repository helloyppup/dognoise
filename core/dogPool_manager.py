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

    def stop(self,dog_name):
        dog=self.active_dog.get(dog_name)
        if not dog:
            logger.warning(f"<<dog不存在>>{dog_name} <无法停止运行>")
            return

        file_path = dog.stop()

        del self.active_dog[dog_name]

        if file_path and os.path.exists(file_path):
            logger.info(f"{dog_name}<狗叼回来一些东西...>{file_path}")
            allure.attach.file(file_path, name=f"{dog_name}_log", attachment_type=allure.attachment_type.ANY)


    def stop_all(self):
        # 收狗
        for name in list(self.active_dog.keys()):
            self.stop(name)


