import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from log_mw import RequestLoggingMiddleware
from login import login_router
from mysql_client import init_db, close_db
from redis_client import init_redis, close_redis


# 配置日志
log_level = logging.DEBUG if settings.debug else logging.WARNING
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# 定义Lifespan事件
async def lifespan(app: FastAPI):
    """应用生命周期事件"""

    # 启动事件
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")

    # 初始化数据库连接
    await init_db()
    logger.info("数据库连接池已初始化")

    # 初始化 Redis 连接
    await init_redis()
    logger.info("Redis 连接已建立")

    # 启动心跳监控
    #await manager.start_heartbeat_monitor()

    logger.info("应用启动完成")
    
    yield  # 应用运行中
    
    # 关闭事件
    logger.info("应用正在关闭...")

    # 关闭所有 WebSocket 连接
    #for connection_id in list(manager.active_connections.keys()):
    #    await manager.disconnect(connection_id, reason="服务器关闭")

    # 关闭数据库连接
    await close_db()
    logger.info("数据库连接已关闭")

    # 关闭 Redis 连接
    await close_redis()
    logger.info("Redis 连接已关闭")

    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
    )

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加Log中间件
if settings.debug:
    app.add_middleware(RequestLoggingMiddleware)

# 注册路由
app.include_router(login_router, prefix=settings.api_vstr, tags=["JUSI Login Server"])

# 处理根路径请求
@app.get("/")
async def root():
    return {"message": "JUSI Login Server"}


# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.bind_addr,
        port=settings.bind_port,
        reload=settings.debug,
        reload_dirs=["."],
        log_level=log_level,
        )