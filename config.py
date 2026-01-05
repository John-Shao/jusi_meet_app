from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 应用配置
APP_CONFIG = {
    "RTC_APP_ID": os.getenv("REACT_APP_RTC_APP_ID"),
    "RTC_APP_KEY": os.getenv("REACT_APP_RTC_APP_KEY"),
    "RTC_ACCESS_KEY_ID": os.getenv("REACT_APP_RTC_ACCESS_KEY_ID"),
    "RTC_ACCESS_KEY_SECRET": os.getenv("REACT_APP_RTC_ACCESS_KEY_SECRET"),
    "RTC_ACCOUNT_ID": os.getenv("REACT_APP_RTC_ACCOUNT_ID"),
    "TOS_ACCESS_KEY_ID": os.getenv("REACT_APP_TOS_ACCESS_KEY_ID"),
    "TOS_ACCESS_KEY_SECRET": os.getenv("REACT_APP_TOS_ACCESS_KEY_SECRET"),
    "TOS_ACCOUNT_ID": os.getenv("REACT_APP_TOS_ACCOUNT_ID"),
    "TOS_REGION": os.getenv("REACT_APP_TOS_REGION"),
    "TOS_ENDPOINT": os.getenv("REACT_APP_TOS_ENDPOINT"),
    "TOS_BUCKET": os.getenv("REACT_APP_TOS_BUCKET"),
    # 火山引擎SMS服务配置
    "VOLC_AK": os.getenv("VOLC_AK"),
    "VOLC_SK": os.getenv("VOLC_SK"),
    "SMS_SIGNATURE": os.getenv("SMS_SIGNATURE"),
    "SMS_TEMPLATE_ID": os.getenv("SMS_TEMPLATE_ID")
}
