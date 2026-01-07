from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# 事件名称枚举
class EventName(str, Enum):
    PASSWORD_FREE_LOGIN = "passwordFreeLogin"
    SEND_SMS_CODE = "sendSmsCode"
    SMS_CODE_LOGIN = "smsCodeLogin"
    SET_APP_INFO = "setAppInfo"
    CHANGE_USER_NAME = "changeUserName"

# 通用响应模型
class ResponseModel(BaseModel):
    code: int
    message: str

# 用户信息模型
class UserInfo(BaseModel):
    user_id: str
    user_name: str
    login_token: str
    created_at: int

# 登录响应模型
class LoginReturn(ResponseModel):
    response: UserInfo

# 设置应用信息请求模型
class SetAppInfoRequest(BaseModel):
    login_token: str
    app_id: str
    app_key: str
    volc_ak: str
    volc_sk: str
    account_id: str

# RTS状态响应模型
class RTSState(BaseModel):
    app_id: Optional[str] = None
    rts_token: Optional[str] = None
    server_signature: Optional[str] = None
    server_url: Optional[str] = None

# 设置应用信息响应模型
class SetAppInfoReturn(ResponseModel):
    response: RTSState

# 修改用户名请求模型
class ChangeUserNameRequest(BaseModel):
    user_name: str
    login_token: str

# 通用请求模型
class RequestModel(BaseModel):
    event_name: EventName
    content: str

# 发送验证码请求模型
class SendSmsVerifyCodeRequest(BaseModel):
    phone: str  # 手机号码

# 手机验证码登录请求模型
class SmsVerifyCodeLoginRequest(BaseModel):
    phone: str  # 手机号码
    code: str   # 短信验证码
