from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from app.auth_schema import RegisterSchema, LoginSchema
from app.service import register_user, login_user

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Hello"}

@router.post("/register")
def register(data: RegisterSchema):
    return register_user(data)

@router.post("/login")
def login(data: LoginSchema):
    return login_user(data)

@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):

    from app.auth_schema import LoginSchema

    data = LoginSchema(
        email=form_data.username,
        password=form_data.password
    )

    result = login_user(data)

    if not result.get("success"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail=result["message"]
        )

    return {
        "access_token": result["token"],
        "token_type": "bearer"
    }