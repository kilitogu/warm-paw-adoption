from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:

    """JWT token 鉴权验证合法性"""

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效，请重新登录"
        )



    # 获取到用户ID
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的登录凭证"
        )

    # 从数据库根据用户ID查询用户信息
    user = db.query(User).filter(User.id == user_id).first()

    # Token 有效不代表账号仍存在，查不到用户时拒绝本次访问。
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在，请重新登录",
        )

    if int(user.status) != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户被禁用"
        )

    return user