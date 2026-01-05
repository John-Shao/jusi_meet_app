from pydantic import BaseModel, Field
from typing import Optional, List

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
    scenes_name: str

# RTS应用设置模型
class AppSet(BaseModel):
    app_id: str
    rts_token: str
    scenes_name: str

# RTS状态响应模型
class RTSState(BaseModel):
    app_id: Optional[str] = None
    rts_token: Optional[str] = None
    server_signature: Optional[str] = None
    server_url: Optional[str] = None
    app_set: Optional[List[AppSet]] = None

# 设置应用信息响应模型
class SetAppInfoReturn(ResponseModel):
    response: RTSState

# 修改用户名请求模型
class ChangeUserNameRequest(BaseModel):
    user_name: str
    login_token: str

# 通用请求模型
class RequestModel(BaseModel):
    event_name: str
    content: str

# 手机验证码登录请求模型
class SMSVerificationCodeRequest(BaseModel):
    phone_number: str
    verification_code: str

# 用户名+密码登录请求模型
class UsernamePasswordRequest(BaseModel):
    username: str
    password: str
