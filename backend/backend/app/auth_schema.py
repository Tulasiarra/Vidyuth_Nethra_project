from pydantic import BaseModel,EmailStr, Field

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginSchema(BaseModel):
    email: str
    password: str