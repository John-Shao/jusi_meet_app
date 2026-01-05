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
    AppSet,
    SMSVerificationCodeRequest,
    UsernamePasswordRequest
)
from utils import generate_user_id, generate_login_token, parse_content, current_timestamp
from config import APP_CONFIG
from volcengine.sms.SmsService import SmsService

# 创建FastAPI应用
app = FastAPI(title="Meeting API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟用户存储
users_db = {}
# 模拟用户密码存储（实际项目中应该加密存储）
user_passwords_db = {}

# 登录路由
@app.post("/vertc_demo_me_os/login", tags=["login"])
async def login(request: RequestModel):
    event_name = request.event_name
    content = parse_content(request.content)
    
    if event_name == "passwordFreeLogin":
        # 免密登录
        user_name = content.get("user_name")
        if not user_name:
            raise HTTPException(status_code=400, detail="Missing user_name")
        
        # 生成用户信息
        user_id = generate_user_id()
        login_token = generate_login_token()
        created_at = current_timestamp()
        
        # 存储用户信息
        user_info = UserInfo(
            user_id=user_id,
            user_name=user_name,
            login_token=login_token,
            created_at=created_at
        )
        users_db[login_token] = user_info
        
        return LoginReturn(
            code=200,
            message="ok",
            response=user_info
        )
    
    elif event_name == "smsVerificationCode":
        # 手机验证码登录
        try:
            sms_login_data = SMSVerificationCodeRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证验证码（这里应该调用火山引擎SMS服务进行验证）
        try:
            # 初始化火山引擎SMS服务
            sms_service = SmsService()
            sms_service.set_ak(APP_CONFIG.get("VOLC_AK"))
            sms_service.set_sk(APP_CONFIG.get("VOLC_SK"))
            
            # 验证验证码
            # 注意：具体的验证接口需要根据火山引擎SMS服务的实际API进行调整
            # 这里只是一个示例
            verify_params = {
                "PhoneNumber": sms_login_data.phone_number,
                "Code": sms_login_data.verification_code,
                "Signature": APP_CONFIG.get("SMS_SIGNATURE"),
                "TemplateID": APP_CONFIG.get("SMS_TEMPLATE_ID")
            }
            
            # 调用验证接口
            # response = sms_service.verify_sms_code(verify_params)
            # 由于是示例，这里我们假设验证总是成功
            # 实际项目中需要替换为真实的API调用
            
            # 验证通过后，生成用户信息
            user_id = generate_user_id()
            login_token = generate_login_token()
            created_at = current_timestamp()
            
            # 使用手机号作为用户名
            user_name = sms_login_data.phone_number
            
            # 存储用户信息
            user_info = UserInfo(
                user_id=user_id,
                user_name=user_name,
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
            raise HTTPException(status_code=500, detail=f"SMS verification failed: {str(e)}")
    
    elif event_name == "usernamePassword":
        # 用户名+密码登录
        try:
            username_password_data = UsernamePasswordRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证用户名和密码
        if username_password_data.username not in user_passwords_db:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if user_passwords_db[username_password_data.username] != username_password_data.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # 生成用户信息
        user_id = generate_user_id()
        login_token = generate_login_token()
        created_at = current_timestamp()
        
        # 存储用户信息
        user_info = UserInfo(
            user_id=user_id,
            user_name=username_password_data.username,
            login_token=login_token,
            created_at=created_at
        )
        users_db[login_token] = user_info
        
        return LoginReturn(
            code=200,
            message="ok",
            response=user_info
        )
    
    elif event_name == "setAppInfo":
        # 设置应用信息
        try:
            set_app_info_data = SetAppInfoRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证登录令牌
        if set_app_info_data.login_token not in users_db:
            raise HTTPException(status_code=401, detail="Invalid login_token")
        
        # 生成RTS状态信息
        rts_token = generate_login_token()
        app_set = AppSet(
            app_id=set_app_info_data.app_id,
            rts_token=rts_token,
            scenes_name=set_app_info_data.scenes_name
        )
        
        rts_state = RTSState(
            app_id=set_app_info_data.app_id,
            rts_token=rts_token,
            server_signature="demo_server_signature",
            server_url="wss://demo.rts.volcvideo.com",
            app_set=[app_set]
        )
        
        return SetAppInfoReturn(
            code=200,
            message="ok",
            response=rts_state
        )
    
    elif event_name == "changeUserName":
        # 修改用户名
        try:
            change_name_data = ChangeUserNameRequest(**content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
        
        # 验证登录令牌
        if change_name_data.login_token not in users_db:
            raise HTTPException(status_code=401, detail="Invalid login_token")
        
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
