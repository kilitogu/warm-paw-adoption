from fastapi import Depends
from fastapi.routing import APIRoute, APIRouter
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import Response
from app.schemas.register import RegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/api", tags=["权限验证"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    auth_service.register(db, data)
    return Response.success(message="注册成功")