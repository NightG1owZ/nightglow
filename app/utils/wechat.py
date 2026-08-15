import asyncio
import json
from typing import Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

WX_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
WX_USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"


def _get_json(url: str) -> Dict:
    """同步 GET 请求并解析 JSON（在 asyncio.to_thread 中调用）"""
    req = Request(url, headers={"User-Agent": "NightGlow/1.0"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def get_access_token(app_id: str, app_secret: str, code: str) -> Dict:
    """用 code 换取 access_token 与 openid"""
    query = urlencode({
        "appid": app_id,
        "secret": app_secret,
        "code": code,
        "grant_type": "authorization_code",
    })
    return await asyncio.to_thread(_get_json, f"{WX_ACCESS_TOKEN_URL}?{query}")


async def get_user_info(access_token: str, openid: str) -> Dict:
    """拉取微信用户信息（昵称、头像、unionid）"""
    query = urlencode({
        "access_token": access_token,
        "openid": openid,
        "lang": "zh_CN",
    })
    return await asyncio.to_thread(_get_json, f"{WX_USERINFO_URL}?{query}")
