# -*- encoding=utf8 -*-
#
from libs.logger import logger

__author__ = "pupply"

from airtest.core.api import *

auto_setup(__file__)
touch(Template(r"tpl1763902077543.png", record_pos=(-0.002, -0.143), resolution=(1260, 2800)))

logger.info("===执行完毕===")

text="这是一个返回值"
__retval__ = {
    "status": "success",
    "order_id": text
}