import uuid
import json
import time
from typing import Dict, Any

def generate_user_id() -> str:
    """生成唯一用户ID"""
    return str(uuid.uuid4()).replace("-", "")

def generate_login_token() -> str:
    """生成登录令牌"""
    return str(uuid.uuid4()).replace("-", "")

def parse_content(content: str) -> Dict[str, Any]:
    """解析请求内容"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}

def current_timestamp() -> int:
    """获取当前时间戳"""
    return int(time.time())
