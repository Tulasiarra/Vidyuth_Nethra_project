from pydantic import BaseModel

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str

class VerifyOtpSchema(BaseModel):
    email: str
    otp: str

class ForgotPasswordSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    email: str
    otp: str
    new_password: str

class ResetPasswordDirectSchema(BaseModel):
    new_password: str
