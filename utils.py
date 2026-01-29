import uuid
import json
import time
from typing import Dict, Any
from config import settings
from access_token import AccessToken, PrivSubscribeStream, PrivPublishStream


def generate_user_id() -> str:
    """生成唯一用户ID"""
    return str(uuid.uuid4()).replace("-", "")

def generate_login_token() -> str:
    """生成登录令牌"""
    return str(uuid.uuid4()).replace("-", "")

def generate_wildcard_token(user_id: str) -> str:
    """生成RTS令牌"""
    room_id = "*"  # 将 roomId 置为"*"，表示对所有房间都有权限，详情：https://www.volcengine.com/docs/6348/70121?lang=zh
    atobj = AccessToken(settings.rtc_app_id, settings.rtc_app_key, room_id, user_id)
    atobj.add_privilege(PrivSubscribeStream, 0)
    atobj.add_privilege(PrivPublishStream, int(time.time()) + settings.rtc_token_expire_ts)
    atobj.expire_time(int(time.time()) + settings.rtc_token_expire_ts)  # TODO: 复用优化，将token放在redis中，设定过期时间
    return atobj.serialize()

def parse_content(content: str) -> Dict[str, Any]:
    """解析请求内容"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}

def current_timestamp() -> int:
    """获取当前时间戳"""
    return int(time.time())


if __name__ == "__main__":
    # 测试生成函数
    rts_token = generate_wildcard_token("user_02")
    print(f"RTS Token: {rts_token}")
