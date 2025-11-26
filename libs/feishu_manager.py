import requests
import time
import hmac
import hashlib
import base64
from libs.logger import logger


class FeishuManager:
    def __init__(self, webhook, secret=None):
        self.webhook = webhook
        self.secret = secret

    def _gen_sign(self, timestamp):
        """
        生成飞书安全签名 (HMAC-SHA256)
        """
        if not self.secret:
            return None

        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def send_text(self, content):
        """
        发送纯文本消息
        """
        if not self.webhook:
            logger.warning("⚠️ 飞书 Webhook 未配置，跳过发送")
            return False

        # 1. 构造基础 Payload
        timestamp = int(time.time())
        payload = {
            "msg_type": "text",
            "content": {"text": content}
        }

        # 2. 如果有密钥，注入签名
        if self.secret:
            payload["timestamp"] = str(timestamp)
            payload["sign"] = self._gen_sign(timestamp)

        # 3. 发送请求
        try:
            response = requests.post(self.webhook, json=payload)
            res_json = response.json()

            # 飞书返回 code=0 表示成功
            if res_json.get("code") == 0:
                logger.info(f"📢 飞书通知发送成功: {content[:20]}...")
                return True
            else:
                logger.error(f"❌ 飞书发送失败: {res_json}")
                return False

        except Exception as e:
            logger.error(f"❌ 网络请求异常: {e}")
            return False