from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import BusinessException
from app.core.response import Response
from app.models.user import User
from app.schemas.login import LoginRequest, LoginResponse
from app.schemas.user import UserResponse
from app.services import auth_service
from app.utils.password_hasher import check_password
from app.utils.security import create_token

router = APIRouter(prefix="/api", tags=["登录接口"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    result = auth_service.login(db, data)

    return Response.success(
        data=LoginResponse(token=result.token, user=UserResponse.model_validate(result.user))
    )


