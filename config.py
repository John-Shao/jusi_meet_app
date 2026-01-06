from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # RTC配置
    rtc_app_id: str = ""
    rtc_app_key: str = ""
    rtc_access_key_id: str = ""
    rtc_access_key_secret: str = ""
    rtc_account_id: str = ""
    
    # TOS配置
    tos_access_key_id: str = ""
    tos_access_key_secret: str = ""
    tos_account_id: str = ""
    tos_region: str = ""
    tos_endpoint: str = ""
    tos_bucket: str = ""
    
    # 火山引擎SMS服务配置
    volc_ak: str = ""
    volc_sk: str = ""
    sms_signature: str = ""
    sms_template_id: str = ""

    # 其他配置项
    debug: bool = True
    app_name: str = "JUSI RTS"
    app_version: str = "1.0.0"
    bind_addr: str = "0.0.0.0"
    bind_port: int = 8000
    
    # 指定配置文件和相关参数
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

# 创建配置实例
settings = Settings()
