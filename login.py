'''
与火山veRTC Meeting Demo配套的登录服务器
'''
import logging
import json
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    generate_wildcard_token,
    parse_content,
    current_timestamp
    )
from config import settings
from volcengine.sms.SmsService import SmsService
from mysql_client import (
    create_user,
    get_user_info,
    update_user_name,
    get_user_by_phone,
    update_login_time
)
from redis_client import (
    set_login_token,
    get_user_id_by_token
)


logger = logging.getLogger(__name__)

login_router = APIRouter()


# 登录路由
@login_router.post("/login", tags=["login"])
async def login(request: RequestModel):
    event_name = request.event_name
    content = parse_content(request.content)

    # 发送短信验证码
    if event_name == EventName.SEND_SMS_CODE:
        try:
            send_sms_data = SendSmsVerifyCodeRequest(**content)
        except Exception as e:
            logger.error(f"Invalid request data: {str(e)}")
            return ResponseModel(
                code=400,
                message="Invalid request data: " + str(e)
            )
        
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
            
            # 调用火山引擎发送验证码接口
            response = sms_service.send_sms_verify_code(json.dumps(send_params))
            
            # 检查发送响应
            if response.get("ResponseMetadata", {}).get("Error"):
                error_code = response["ResponseMetadata"]["Error"].get("Code", "未知错误")
                error_msg = response["ResponseMetadata"]["Error"].get("Message", "验证码发送失败")
                error_info = f"{error_code}: {error_msg}"
                raise HTTPException(status_code=500, detail=f"SMS send failed: {error_info}")
            
            return ResponseModel(
                code=200,
                message="验证码发送成功"
            )
            
        except Exception as e:
            logger.error(f"发送验证码失败: {str(e)}")
            return ResponseModel(
                code=500,
                message="验证码发送失败：" + str(e)
            )
    
    # 手机验证码登录
    elif event_name == EventName.SMS_CODE_LOGIN:
        try:
            sms_login_data = SmsVerifyCodeLoginRequest(**content)
        except Exception as e:
            logger.error(f"Invalid request data: {str(e)}")
            return ResponseModel(
                code=400,
                message="Invalid request data: " + str(e)
            )
        
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
            
            # 调用验证接口
            response = sms_service.check_sms_verify_code(json.dumps(verify_params))
            
            # 检查验证响应
            if response.get("ResponseMetadata", {}).get("Error"):
                error_code = response["ResponseMetadata"]["Error"].get("Code", "未知错误")
                error_msg = response["ResponseMetadata"]["Error"].get("Message", "验证码验证失败")
                error_info = f"{error_code}: {error_msg}"
                raise HTTPException(status_code=500, detail=f"SMS verify failed: {error_info}")
            
            # 检查校验结果
            if response.get("Result") == "1":
                return ResponseModel(
                    code=441,
                    message="验证码不正确，请重新输入验证码"
                )
            elif response.get("Result") == "2":
                return ResponseModel(
                    code=440,
                    message="验证码过期，请重新发送验证码"
                )

            # 验证通过后，先通过手机号查询用户
            user_info = await get_user_by_phone(sms_login_data.phone)

            login_token = generate_login_token()

            if user_info:
                # 老用户：更新最后登录时间
                update_success = await update_login_time(user_info.user_id)
                if not update_success:
                    logger.warning(f"Failed to update login time for user: {user_info.user_id}")
            else:
                # 新用户：创建用户记录
                new_user_id = generate_user_id()
                created_at = current_timestamp()

                # 创建用户信息对象（不包含 login_token）
                user_info = UserInfo(
                    user_id=new_user_id,
                    user_name=sms_login_data.phone,  # 使用手机号作为用户名
                    phone=sms_login_data.phone,      # 设置手机号
                    created_at=created_at
                )

                # 将用户信息存储到数据库
                db_success = await create_user(user_info)
                if not db_success:
                    return ResponseModel(
                        code=500,
                        message="用户信息存储失败"
                    )

            # 将 login_token 存储到 Redis，设置 15 天过期
            redis_success = await set_login_token(login_token, user_info.user_id)
            if not redis_success:
                return ResponseModel(
                    code=500,
                    message="登录令牌缓存失败"
                )

            # 返回用户信息时附加 login_token
            user_info.login_token = login_token

            return LoginReturn(
                code=200,
                message="ok",
                response=user_info
            )
            
        except Exception as e:
            logger.error(f"验证码验证失败: {str(e)}")
            return ResponseModel(
                code=500,
                message="验证码验证失败：" + str(e)
            )
    
    # 设置应用信息
    elif event_name == EventName.SET_APP_INFO:
        try:
            set_app_info_data = SetAppInfoRequest(**content)
        except Exception as e:
            logger.error(f"Invalid request data: {str(e)}")
            return ResponseModel(
                code=400,
                message="Invalid request data: " + str(e)
            )
        
        # 从 Redis 验证登录令牌并获取 user_id
        user_id = await get_user_id_by_token(set_app_info_data.login_token)
        if user_id is None:
            return ResponseModel(
                code=450,
                message="Invalid login_token"
            )
        
        # 生成RTS状态信息
        rts_token = generate_wildcard_token(user_id=user_id)
        
        # 构建RTS状态响应
        rts_state = RTSState(
            app_id=set_app_info_data.app_id,
            rts_token=rts_token,
            server_signature="temp_server_signature",  # 业务服务器签名，业务服务器暂时不校验签名
            server_url=settings.rts_server_url,
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
            logger.error(f"Invalid request data: {str(e)}")
            return ResponseModel(
                code=400,
                message="Invalid request data: " + str(e)
            )
        
        # 从 Redis 验证登录令牌并获取 user_id
        user_id = await get_user_id_by_token(change_name_data.login_token)
        if user_id is None:
            return ResponseModel(
                code=450,
                message="Invalid login_token"
            )

        # 更新用户名
        success = await update_user_name(user_id, change_name_data.user_name)
        if not success:
            return ResponseModel(
                code=500,
                message="Failed to update user name"
            )

        return ResponseModel()
    
    else:
        logger.error(f"Unknown event_name: {event_name}")
        return ResponseModel(
            code=400,
            message="Unknown event_name: " + event_name
        )
