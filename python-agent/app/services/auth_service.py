from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException
from app.models import User
from app.schemas.login import LoginRequest, LoginResponse
from app.schemas.register import RegisterRequest
from app.schemas.user import UserResponse
from app.utils.password_hasher import check_password, hash_password
from app.utils.security import create_token


def login(db: Session, data: LoginRequest) -> LoginResponse:
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not check_password(data.password, user.password):
        raise BusinessException(message="账号或密码错误")

    if int(user.status) != 1:
        raise BusinessException(message="账号被禁用")

    token = create_token(user.id)
    return LoginResponse(
        token=token,
        user=UserResponse.model_validate(user),
    )

def register(db: Session, data: RegisterRequest) -> None:
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise BusinessException(message="账号已存在")

    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name or data.username,
        role="user",
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)