'''
数据库操作模块
'''
import logging
import aiomysql
from typing import Optional
from contextlib import asynccontextmanager
from models import UserInfo
from config import settings

logger = logging.getLogger(__name__)


class Database:
    """数据库连接池管理类"""

    def __init__(self):
        self.pool = None

    async def connect(self):
        """创建数据库连接池"""
        try:
            self.pool = await aiomysql.create_pool(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                db=settings.db_name,
                charset='utf8mb4',
                autocommit=True,
                minsize=1,
                maxsize=10
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {str(e)}")
            raise

    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        async with self.pool.acquire() as conn:
            yield conn


# 全局数据库实例
db = Database()


async def init_db():
    """初始化数据库连接"""
    await db.connect()


async def close_db():
    """关闭数据库连接"""
    await db.close()


# 用户数据库操作函数
async def create_user(user_info: UserInfo) -> bool:
    """
    创建新用户

    Args:
        user_info: 用户信息对象

    Returns:
        bool: 创建是否成功
    """
    try:
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                sql = """
                    INSERT INTO tb_user (user_id, user_name, phone, created_at, updated_at, last_login_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # 使用 UserInfo 对象中的 phone 字段
                phone = user_info.phone

                await cursor.execute(sql, (
                    user_info.user_id,
                    user_info.user_name,
                    phone,
                    user_info.created_at,
                    user_info.created_at,  # updated_at 初始值与 created_at 相同
                    user_info.created_at   # last_login_at 初始值与 created_at 相同
                ))
                logger.info(f"User created successfully: user_id={user_info.user_id}")
                return True
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        return False


async def get_user_info(user_id: str) -> Optional[UserInfo]:
    """
    根据 user_id 获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        Optional[UserInfo]: 用户信息对象，如果不存在则返回 None
    """
    try:
        async with db.get_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = """
                    SELECT user_id, user_name, phone, created_at
                    FROM tb_user
                    WHERE user_id = %s AND is_active = 1
                """
                await cursor.execute(sql, (user_id,))
                result = await cursor.fetchone()

                if result:
                    return UserInfo(**result)
                return None
    except Exception as e:
        logger.error(f"Failed to get user by user_id: {str(e)}")
        return None


async def update_user_name(user_id: str, user_name: str) -> bool:
    """
    更新用户名

    Args:
        user_id: 用户ID
        user_name: 新的用户名

    Returns:
        bool: 更新是否成功
    """
    try:
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                from utils import current_timestamp
                updated_at = current_timestamp()

                sql = """
                    UPDATE tb_user
                    SET user_name = %s, updated_at = %s
                    WHERE user_id = %s AND is_active = 1
                """
                await cursor.execute(sql, (user_name, updated_at, user_id))

                if cursor.rowcount > 0:
                    logger.info(f"User name updated successfully: user_id={user_id}")
                    return True
                return False
    except Exception as e:
        logger.error(f"Failed to update user name: {str(e)}")
        return False


async def get_user_by_phone(phone: str) -> Optional[UserInfo]:
    """
    根据手机号获取用户信息

    Args:
        phone: 手机号

    Returns:
        Optional[UserInfo]: 用户信息对象，如果不存在则返回 None
    """
    try:
        async with db.get_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                sql = """
                    SELECT user_id, user_name, phone, created_at
                    FROM tb_user
                    WHERE phone = %s AND is_active = 1
                """
                await cursor.execute(sql, (phone,))
                result = await cursor.fetchone()

                if result:
                    return UserInfo(**result)
                return None
    except Exception as e:
        logger.error(f"Failed to get user by phone: {str(e)}")
        return None


async def update_login_time(user_id: str) -> bool:
    """
    更新用户最后登录时间

    Args:
        user_id: 用户ID

    Returns:
        bool: 更新是否成功
    """
    try:
        async with db.get_connection() as conn:
            async with conn.cursor() as cursor:
                from utils import current_timestamp
                now = current_timestamp()

                sql = """
                    UPDATE tb_user
                    SET last_login_at = %s, updated_at = %s
                    WHERE user_id = %s AND is_active = 1
                """
                await cursor.execute(sql, (now, now, user_id))

                if cursor.rowcount > 0:
                    logger.info(f"User login time updated successfully: user_id={user_id}")
                    return True
                return False
    except Exception as e:
        logger.error(f"Failed to update user login time: {str(e)}")
        return False
