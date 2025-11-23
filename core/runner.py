import os
import importlib.util
import sys
from libs.logger import logger

class RunnerDog:
    def __init__(self,context,root_path="actions"):
        """
        扫描所有球球
        :param root_path:
        """
        # 找到自己的文件路径，再网上走两层，到根目录下
        project_root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)) )
        # 扫描路径
        self.actions_dir=os.path.join(project_root,root_path)
        self.action_map={}
        self.context=context
        # 模块缓存池，防止重复编译造成资源浪费
        self.module_cache = {}
        #收集ball
        self._scan_actions()

    def _scan_actions(self):
        logger.info(f"正在扫描所有ball:{self.actions_dir}")
        count = 0

        for root,dirs,files in os.walk(self.actions_dir):
            # root 当前遍历到的目录
            # dirs root下所有子目录列表
            # files root下所有文件列表
            for file in files:
                if file.endswith(".py") and file!="__init__.py":
                    keyword = file[:-3]
                    full_path = os.path.join(root,file)

                    self.action_map[keyword]=full_path
                    count += 1
        logger.info(f"scan完成，找到{count}球球🥎")

    def run(self,keyword,reload=False):
        """
        play ball~!
        :param self:
        :param keyword:
        :param context: 传递给ball的上下文数据
        :param reload:如果是True，则强制重新加载文件，一般不建议开启，调试的时候用的
        :return:
        """

        context=self.context
        file_path = self.action_map.get(keyword)
        if not file_path:
            logger.info(f"找不到球{keyword}😿")
            raise Exception(f"球 [{keyword}] 未找到！check 文件名！")

        logger.info(f"开始执行：{keyword} -> {file_path}")

        try:
            # 动态加载 很好的妙妙工具使我旋转🦴🦴🦴🦴🦴🦴

            if keyword in self.module_cache and not reload:
                module = self.module_cache[keyword]

            else:
                # 这里是动态加载操作的球球
                # 模块叫什么 在哪里
                spec = importlib.util.spec_from_file_location(keyword, file_path)
                # 一个空python模块对象，实际上啥也还没定义
                module = importlib.util.module_from_spec(spec)
                # 注册到系统 这一步通过字典存储，如果之后也引入这个名称的模块，后加载的会覆盖，防止重复导入
                sys.modules[keyword] = module
                # 把module丢到容器里
                spec.loader.exec_module(module)

            if hasattr(module,"run"):
                if keyword not in self.module_cache:
                    # 如果符合要求且不在缓存池，直接加入缓存池，后续如果还有就不需要重复加载了
                    self.module_cache[keyword] = module
                return module.run(context)
            else:
                logger.warning(f"{keyword} 未定义run，狗都不看")
                return None

        except Exception as e:
            logger.error(f"{keyword} 执行出错 -- {e}")
            raise e

    def clear_cache(self):
        """
        【新增】手动清空缓存池
        当觉得内存占用过高，或者进行了一次大规模的热更新后，可以调用此方法。
        一般来说不会有问题，但长期挂机建议周期性调用一下
        """
        count = len(self.module_cache)
        self.module_cache.clear()
        logger.info(f"🧹 积木缓存池已清空，释放了 {count} 个积木对象。")