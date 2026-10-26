from datetime import datetime, timedelta, timezone
import jwt

from app.core.config import settings


def create_token(user_id: str) -> str:
    """
    生成 JWT 访问令牌 (Access Token)

    :param user_id: 用户唯一标识 ID (字符串格式)
    :return: 编码后的 JWT 字符串
    """
    # 必须指定关键字参数 hours=，否则会被当成 days= (天)
    # 使用带 UTC 时区的当前时间，避免部署到服务器后因时区差异导致 Token 失效
    expire: datetime = datetime.now(timezone.utc) + timedelta(hours=settings.token_expire_hours)

    payload: dict = {"user_id": user_id, "exp": expire}

    # 类型提示：jwt.encode 返回的是 str
    token: str = jwt.encode(payload, settings.token_secret, algorithm=settings.token_algorithm)

    return token


def decode_token(token: str) -> dict:
    """
    解析并验证 JWT 访问令牌

    :param token: 前端传过来的 JWT 字符串
    :return: 解析后的 payload 字典 (包含 user_id 等信息)
    :raises jwt.PyJWTError: 如果 token 过期或被篡改，会抛出此异常
    """
    # jwt.decode 返回的 payload 是一个字典
    payload: dict = jwt.decode(
        token,
        settings.token_secret,
        algorithms=[settings.token_algorithm]  # 注意这里必须传列表
    )

    return payload