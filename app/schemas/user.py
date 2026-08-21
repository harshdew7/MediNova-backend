from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SignupOTPRequest(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    mobile_number: str = Field(
        min_length=7,
        max_length=30,
    )

    password: str = Field(
        min_length=8,
    )


class SignupOTPResendRequest(BaseModel):
    email: EmailStr

    mobile_number: str = Field(
        min_length=7,
        max_length=30,
    )


class SignupOTPVerify(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    mobile_number: str = Field(
        min_length=7,
        max_length=30,
    )

    password: str = Field(
        min_length=8,
    )

    email_otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

    mobile_otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordVerify(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class ResetPasswordRequest(BaseModel):
    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

    new_password: str = Field(
        min_length=8,
    )


class UserResponse(BaseModel):
    id: int

    full_name: str

    email: EmailStr

    mobile_number: str | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None