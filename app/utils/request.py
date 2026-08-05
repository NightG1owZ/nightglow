from typing import Optional

from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    """从请求中获取客户端真实 IP（优先取反向代理头）"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    """获取 User-Agent"""
    return request.headers.get("user-agent")
