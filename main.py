import logging
import json
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from models import (
    RequestModel,
    LoginReturn,
    SetAppInfoReturn,
    ResponseModel,
    SetAppInfoRequest,
    ChangeUserNameRequest,
    UserInfo,
    RTSState,
    SendSmsVerifyCodeRequest,
    SmsVerifyCodeLoginRequest,
    EventName
)
from utils import (
    generate_user_id,
    generate_login_token,
    generate_rts_token,
    parse_content,
    current_timestamp
    )
from config import settings
from volcengine.sms.SmsService import SmsService
from log_mw import RequestLoggingMiddleware


# 配置日志
log_level = logging.DEBUG if settings.debug else logging.WARNING
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# 定义Lifespan事件
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期事件"""

    # 启动事件
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    
    # 连接 Redis
    # await manager.connect_redis()
    
    # 启动心跳监控
    #await manager.start_heartbeat_monitor()
    
    logger.info("应用启动完成")
    
    yield  # 应用运行中
    
    # 关闭事件
    logger.info("应用正在关闭...")
    
    # 关闭所有 WebSocket 连接
    #for connection_id in list(manager.active_connections.keys()):
    #    await manager.disconnect(connection_id, reason="服务器关闭")
    
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
app.add_middleware(RequestLoggingMiddleware)

# 模拟用户存储
users_db = {}

# 登录路由
@app.post("/vertc_demo_me_os/login", tags=["login"])
async def login(request: RequestModel):
    event_name = request.event_name
    content = parse_content(request.content)

    # 发送短信验证码
    if event_name == EventName.SEND_SMS_CODE:
        try:
            send_sms_data = SendSmsVerifyCodeRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 调用火山引擎SendSmsVerifyCode接口
        try:
            # 初始化火山引擎SMS服务
            sms_service = SmsService()
            sms_service.set_ak(settings.volc_ak)
            sms_service.set_sk(settings.volc_sk)
            
            # 准备发送验证码的参数
            send_params = {
                "SmsAccount": settings.sms_account,       # 消息组ID（验码主键之一）
                "Sign": settings.sms_signature,           # 短信签名，巨思人工智能
                "TemplateID": settings.sms_template_id,   # 验证码模板ID
                "PhoneNumber": send_sms_data.phone,       # 接收手机号，不支持批量发送（验码主键之一）
                "Scene": settings.sms_scene,              # 验证码使用场景（验码主键之一）
                "ExpireTime": settings.sms_expire_time,   # 验证码有效时间，单位秒
                "TryCount": settings.sms_try_count,       # 验证码可以尝试验证次数
                "Tag": ""                                 # 透传字段
            }
            '''
            # 调用火山引擎发送验证码接口
            response = sms_service.send_sms_verify_code(json.dumps(send_params))
            
            # 检查发送响应
            if response.get("ResponseMetadata", {}).get("Error"):
                error_code = response["ResponseMetadata"]["Error"].get("Code", "未知错误")
                error_msg = response["ResponseMetadata"]["Error"].get("Message", "验证码发送失败")
                error_info = f"{error_code}: {error_msg}"
                raise HTTPException(status_code=400, detail=f"SMS send failed: {error_info}")
            '''
            return ResponseModel(
                code=200,
                message="验证码发送成功"
            )
            
        except Exception as e:
            logger.error(f"发送验证码失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SMS send failed: {str(e)}")
    
    # 手机验证码登录
    elif event_name == EventName.SMS_CODE_LOGIN:
        try:
            sms_login_data = SmsVerifyCodeLoginRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证验证码（这里应该调用火山引擎SMS服务进行验证）
        try:
            # 初始化火山引擎SMS服务
            sms_service = SmsService()
            sms_service.set_ak(settings.volc_ak)
            sms_service.set_sk(settings.volc_sk)
            
            # 验证验证码
            verify_params = {
                "SmsAccount": settings.sms_account,   # 消息组ID（验码主键之一）
                "PhoneNumber": sms_login_data.phone,  # 接收手机号（验码主键之一）
                "Scene": settings.sms_scene,          # 验证码使用场景（验码主键之一）
                "Code": sms_login_data.code           # 待校验验证码
            }
            '''
            # 调用验证接口
            response = sms_service.check_sms_verify_code(json.dumps(verify_params))
            
            # 检查验证响应
            if response.get("ResponseMetadata", {}).get("Error"):
                error_code = response["ResponseMetadata"]["Error"].get("Code", "未知错误")
                error_msg = response["ResponseMetadata"]["Error"].get("Message", "验证码验证失败")
                error_info = f"{error_code}: {error_msg}"
                raise HTTPException(status_code=400, detail=f"SMS verify failed: {error_info}")
            
            # 检查校验结果
            if response.get("Result") == "1":
                raise HTTPException(status_code=411, detail="验证码错误")
            elif response.get("Result") == "2":
                raise HTTPException(status_code=412, detail="验证码过期")
            '''
            # 验证通过后，生成用户信息
            user_id = generate_user_id()
            login_token = generate_login_token()
            created_at = current_timestamp()
            
            # 存储用户信息
            user_info = UserInfo(
                user_id=user_id,
                user_name=sms_login_data.phone,  # 使用手机号作为用户名
                login_token=login_token,
                created_at=created_at
            )
            users_db[login_token] = user_info
            
            return LoginReturn(
                code=200,
                message="ok",
                response=user_info
            )
            
        except Exception as e:
            logger.error(f"验证码验证失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"SMS verification failed: {str(e)}")
    
    # 设置应用信息
    elif event_name == EventName.SET_APP_INFO:
        try:
            set_app_info_data = SetAppInfoRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证登录令牌
        if set_app_info_data.login_token not in users_db:
            raise HTTPException(status_code=450, detail="Invalid login_token")
        
        # 获取用户信息
        user_info = users_db[set_app_info_data.login_token]
        
        # 生成RTS状态信息
        rts_token = generate_rts_token(user_id=user_info.user_id)
        
        # 构建RTS状态响应
        rts_state = RTSState(
            app_id=set_app_info_data.app_id,
            rts_token=rts_token,
            server_signature="temp_server_signature",  # 业务服务器签名，业务服务器暂时不校验签名
            server_url="http://113.108.122.183:9000/api/v1/rts/message",  # 业务服务器地址，113.108.122.183为贾沛办公电脑的公网IP
        )
        
        return SetAppInfoReturn(
            code=200,
            message="ok",
            response=rts_state 
        )
    
    # 修改用户名
    elif event_name == EventName.CHANGE_USER_NAME:
        try:
            change_name_data = ChangeUserNameRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证登录令牌
        if change_name_data.login_token not in users_db:
            raise HTTPException(status_code=450, detail="Invalid login_token")
        
        # 更新用户名
        user_info = users_db[change_name_data.login_token]
        user_info.user_name = change_name_data.user_name
        
        return ResponseModel(
            code=200,
            message="ok"
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown event_name: {event_name}")

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
