import threading
import time
import random
from time import sleep

from libs.baseDog import BaseDog
from libs.logger import logger

class Dog(BaseDog):


    def working(self):
        logger.info("狗狗跑过来🐩🐩🐩")
        logger.info("🐕️🐕️🐕️狗狗跑过去")
        print("🐕️🐕️🐕️")
        interval = self.kwargs.get("interval", 1.0)
        sleep(interval)

