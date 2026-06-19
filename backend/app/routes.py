from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from auth_schema import RegisterSchema, LoginSchema, VerifyOtpSchema, ForgotPasswordSchema, ResetPasswordSchema, ResetPasswordDirectSchema
from service import register_user, login_user, forgot_password_flow, reset_password_direct_flow, verify_email_flow
from fastapi import Request, HTTPException

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Hello"}

@router.post("/register")
def register(data: RegisterSchema):
    return register_user(data)

@router.get("/verify-email")
def verify_email(token: str):
    return verify_email_flow(token)

@router.post("/login")
def login(data: LoginSchema):
    return login_user(data)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema):
    return forgot_password_flow(data.email)

@router.post("/reset-password-direct")
def reset_password_direct(data: ResetPasswordDirectSchema, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]
    return reset_password_direct_flow(token, data.new_password)


# ✅ ADD THIS — Swagger OAuth2 form hits this route
@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    from auth_schema import LoginSchema
    # Map 'username' field → 'email' field
    data = LoginSchema(email=form_data.username, password=form_data.password)
    result = login_user(data)
    if not result.get("success"):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail=result["message"])
    return {"access_token": result["token"], "token_type": "bearer"}
