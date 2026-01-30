'''
Redis 客户端模块
用于管理 login_token 的存储和验证
'''
import logging
import redis.asyncio as redis
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 客户端管理类"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """连接到 Redis"""
        try:
            self.client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True
            )
            # 测试连接
            await self.client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def close(self):
        """关闭 Redis 连接"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")


# 全局 Redis 客户端实例
redis_client = RedisClient()


async def init_redis():
    """初始化 Redis 连接"""
    await redis_client.connect()


async def close_redis():
    """关闭 Redis 连接"""
    await redis_client.close()


# Login Token 操作函数

async def set_login_token(login_token: str, user_id: str) -> bool:
    """
    存储 login_token，并设置过期时间

    Args:
        login_token: 登录令牌
        user_id: 用户ID

    Returns:
        bool: 存储是否成功
    """
    try:
        if not redis_client.client:
            logger.error("Redis client not initialized")
            return False

        # 使用 login_token 作为 key，user_id 作为 value
        # 设置过期时间为配置的天数
        expire_seconds = settings.login_token_expire_days * 24 * 60 * 60

        await redis_client.client.setex(
            name=f"login:token:{login_token}",
            time=expire_seconds,
            value=user_id
        )

        logger.info(f"Login token stored: token={login_token[:8]}..., user_id={user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store login token: {str(e)}")
        return False


async def get_user_id_by_token(login_token: str) -> Optional[str]:
    """
    根据 login_token 获取 user_id

    Args:
        login_token: 登录令牌

    Returns:
        Optional[str]: 用户ID，如果 token 不存在或已过期则返回 None
    """
    try:
        if not redis_client.client:
            logger.error("Redis client not initialized")
            return None

        user_id = await redis_client.client.get(f"login:token:{login_token}")
        return user_id
    except Exception as e:
        logger.error(f"Failed to get user_id by token: {str(e)}")
        return None


async def delete_login_token(login_token: str) -> bool:
    """
    删除 login_token（用于登出）

    Args:
        login_token: 登录令牌

    Returns:
        bool: 删除是否成功
    """
    try:
        if not redis_client.client:
            logger.error("Redis client not initialized")
            return False

        result = await redis_client.client.delete(f"login:token:{login_token}")
        if result > 0:
            logger.info(f"Login token deleted: token={login_token[:8]}...")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete login token: {str(e)}")
        return False


async def token_exists(login_token: str) -> bool:
    """
    检查 login_token 是否存在且未过期

    Args:
        login_token: 登录令牌

    Returns:
        bool: token 是否存在
    """
    try:
        if not redis_client.client:
            logger.error("Redis client not initialized")
            return False

        result = await redis_client.client.exists(f"login:token:{login_token}")
        return result > 0
    except Exception as e:
        logger.error(f"Failed to check token existence: {str(e)}")
        return False


async def refresh_token_expiry(login_token: str) -> bool:
    """
    刷新 login_token 的过期时间（可选功能）

    Args:
        login_token: 登录令牌

    Returns:
        bool: 刷新是否成功
    """
    try:
        if not redis_client.client:
            logger.error("Redis client not initialized")
            return False

        expire_seconds = settings.login_token_expire_days * 24 * 60 * 60
        result = await redis_client.client.expire(
            name=f"login:token:{login_token}",
            time=expire_seconds
        )

        if result:
            logger.info(f"Token expiry refreshed: token={login_token[:8]}...")
        return result
    except Exception as e:
        logger.error(f"Failed to refresh token expiry: {str(e)}")
        return False
