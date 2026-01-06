import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求体（对于可能验证失败的情况特别重要）
        request_body = await self._get_request_body(request)
        
        # 记录请求信息
        logger.info(f"请求开始: {request.method} {request.url}")
        logger.info(f"请求头: {dict(request.headers)}")
        logger.info(f"查询参数: {dict(request.query_params)}")
        logger.info(f"路径参数: {request.path_params}")
        
        if request_body:
            logger.info(f"请求体: {request_body}")
        
        # 存储请求体到 state 以便后续使用
        request.state.request_body = request_body
        
        try:
            # 继续处理请求
            response = await call_next(request)
        except Exception as e:
            # 处理异常
            logger.error(f"请求处理异常: {str(e)}")
            logger.error(f"请求URL: {request.url}")
            if hasattr(request.state, 'request_body'):
                logger.error(f"请求体: {request.state.request_body}")
            raise
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(f"请求结束: {request.method} {request.url} - 状态码: {response.status_code} - 耗时: {process_time:.4f}s")
        
        return response
    
    async def _get_request_body(self, request: Request):
        """安全地获取请求体"""
        try:
            # 对于JSON请求
            if request.headers.get("content-type", "").startswith("application/json"):
                body = await request.body()
                if body:
                    try:
                        return json.loads(body.decode("utf-8"))
                    except json.JSONDecodeError:
                        return body.decode("utf-8")
            
            # 对于表单数据
            elif request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
                form_data = await request.form()
                return dict(form_data)
            
            # 对于 multipart/form-data
            elif request.headers.get("content-type", "").startswith("multipart/form-data"):
                # 注意：对于文件上传，不要读取整个文件到内存
                form_data = await request.form()
                result = {}
                for key, value in form_data.items():
                    if hasattr(value, 'filename'):  # 文件字段
                        result[key] = f"<文件: {value.filename}, 大小: {value.size}字节>"
                    else:
                        result[key] = value
                return result
            
            # 其他类型的请求体
            else:
                body = await request.body()
                if body:
                    return body.decode("utf-8", errors="ignore")
                
        except Exception as e:
            logger.warning(f"获取请求体失败: {e}")
        
        return None
