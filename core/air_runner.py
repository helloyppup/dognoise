import os
import sys
import importlib
from airtest.core.api import auto_setup, using
from libs.logger import logger


class AirRunner:
    def __init__(self, context, root_path="air_scripts"):
        self.context = context
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.scripts_dir = os.path.join(project_root, root_path)

        self.script_map = {}  # 路径缓存 { "login": "D:/.../login.air" }
        self.module_cache = {}  # 模块缓存 { "login": <module object> }

        self._scan_scripts()

    def _scan_scripts(self):
        """扫描所有 .air 脚本文件夹"""
        logger.info(f"正在扫描 Airtest 脚本: {self.scripts_dir}")
        count = 0

        # 检查目录是否存在
        if not os.path.exists(self.scripts_dir):
            logger.warning(f"⚠️Airtest 脚本目录不存在: {self.scripts_dir}")
            return

        for root, dirs, files in os.walk(self.scripts_dir):
            for dir_name in dirs:
                if dir_name.endswith(".air"):
                    # 关键字是文件名去掉后缀，例如 "login.air" -> "login"
                    keyword = dir_name.replace(".air", "")
                    full_path = os.path.join(root, dir_name)

                    self.script_map[keyword] = full_path
                    count += 1

        logger.info(f"✅ 扫描完成，找到 {count} 个 Airtest 脚本")

    def run(self, keyword):
        """
        执行指定的 Airtest 脚本
        """
        script_path = self.script_map.get(keyword)
        if not script_path:
            logger.error(f"找不到 Airtest 脚本: {keyword}")
            return False

        logger.info(f"执行 Airtest: {keyword} -> {script_path}")

        try:
            # 环境初始化 (连接设备)
            # 触发懒加载，进行adb连接
            _ = self.context.adb_pool
            self.context.adb_pool['main_phone'].connect()
            # 从 config 读取主设备，如果没有就默认本地
            dev_id = self.context.config.get("adb_devices", {}).get("main_phone", "")
            connect_str = f"Android:///{dev_id}" if dev_id else "Android:///"

            # basedir 设置为脚本所在目录，方便脚本里引用图片
            auto_setup(__file__, devices=[connect_str], logdir=True, project_root=self.scripts_dir)

            # 2. 加载路径 (using)
            using(script_path)

            # 3. 导入/重载模块
            # Airtest 脚本本质是 Python 模块，名字就是文件夹名去掉 .air
            module_name = keyword

            if module_name in sys.modules:
                # 如果之前跑过，必须 reload 才能再次触发脚本里的代码执行
                # 因为 Airtest 脚本通常没有 entry point，import 就会执行
                air_module = importlib.reload(sys.modules[module_name])
            else:
                air_module = importlib.import_module(module_name)

            # 更新缓存（虽然对 reload 来说不需要，但保持一致性）
            self.module_cache[keyword] = air_module

            logger.info(f"✅ Airtest 脚本 [{keyword}] 执行完毕")
            return True

        except Exception as e:
            logger.error(f"Airtest 脚本 [{keyword}] 执行崩溃: {e}")
            return False