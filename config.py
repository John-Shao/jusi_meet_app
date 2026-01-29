from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AK/SK配置
    volc_ak: str
    volc_sk: str

    # RTC配置
    rtc_app_id: str
    rtc_app_key: str
    rtc_token_expire_ts: int = 86400  # RTC token有效期（秒）

    # 火山引擎SMS服务配置
    sms_account: str = "8880e180"
    sms_scene: str = "注册验证码"
    sms_signature: str = "巨思人工智能"
    sms_template_id: str = "S1T_1y2p1bc526ebm"
    sms_expire_time: int = 600  # 验证码有效时间，单位秒
    sms_try_count: int = 5  # 验证码可以尝试验证次数

    # MySQL数据库配置
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "jusi"
    db_password: str
    db_name: str = "jusi_db"

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str

    # Token配置
    login_token_expire_days: int = 15  # login_token有效期（天）

    # 其他配置项
    api_vstr: str = "/api/v1"
    app_name: str = "JUSI RTS"
    app_version: str = "1.0.0"
    bind_addr: str = "0.0.0.0"
    bind_port: int = 8000
    rts_server_url: str = "http://service.jusiai.com:9000/api/v1/rts/message"
    debug: bool = False
    
    # 指定配置文件和相关参数
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

# 创建配置实例
settings = Settings()
