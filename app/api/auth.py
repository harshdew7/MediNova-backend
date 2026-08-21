from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.exceptions import MediNovaException
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ForgotPasswordVerify,
    ResetPasswordRequest,
    SignupOTPRequest,
    SignupOTPResendRequest,
    SignupOTPVerify,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.otp_service import (
    MAX_OTP_ATTEMPTS,
    OTP_EXPIRY_MINUTES,
    create_signup_verification,
    generate_otp,
    get_active_verification,
    get_expiry_time,
    get_resend_cooldown_seconds,
    hash_otp,
    increment_attempts,
    is_expired,
    mark_email_verified,
    mark_mobile_verified,
    verify_otp,
)
from app.services.password_reset_service import (
    MAX_RESET_ATTEMPTS,
    create_password_reset_otp,
    get_latest_password_reset_otp,
    increment_reset_attempts,
    reset_user_password,
    verify_password_reset_otp,
)
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
)
from app.utils.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# SIGNUP - REQUEST OTP
# ============================================================

@router.post(
    "/signup/request-otp",
    status_code=status.HTTP_200_OK,
)
def request_signup_otp(
    signup_data: SignupOTPRequest,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        signup_data.email,
    )

    if existing_user:
        raise MediNovaException(
            message="Email already registered",
            status_code=400,
        )

    existing_mobile = (
        db.query(User)
        .filter(
            User.mobile_number
            == signup_data.mobile_number
        )
        .first()
    )

    if existing_mobile:
        raise MediNovaException(
            message="Mobile number already registered",
            status_code=400,
        )

    verification, email_otp, mobile_otp = (
        create_signup_verification(
            db,
            signup_data.email,
            signup_data.mobile_number,
        )
    )

    print("\n" + "=" * 60)
    print("MEDINOVA DEVELOPMENT OTP")
    print("=" * 60)
    print(f"Email:        {signup_data.email}")
    print(f"Mobile:       {signup_data.mobile_number}")
    print(f"Email OTP:    {email_otp}")
    print(f"Mobile OTP:   {mobile_otp}")
    print(f"Expires:      {verification.expires_at}")
    print("=" * 60 + "\n")

    return {
        "message": "OTP verification codes generated.",
        "expires_in_seconds": OTP_EXPIRY_MINUTES * 60,
    }


# ============================================================
# SIGNUP - RESEND OTP
# ============================================================

@router.post(
    "/signup/resend-otp",
    status_code=status.HTTP_200_OK,
)
def resend_signup_otp(
    signup_data: SignupOTPResendRequest,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        signup_data.email,
    )

    if existing_user:
        raise MediNovaException(
            message="Email already registered",
            status_code=400,
        )

    existing_mobile = (
        db.query(User)
        .filter(
            User.mobile_number
            == signup_data.mobile_number
        )
        .first()
    )

    if existing_mobile:
        raise MediNovaException(
            message="Mobile number already registered",
            status_code=400,
        )

    verification = get_active_verification(
        db,
        signup_data.email,
    )

    if verification is None:
        raise MediNovaException(
            message=(
                "No active OTP verification found. "
                "Please start registration again."
            ),
            status_code=400,
        )

    if (
        verification.mobile_number
        != signup_data.mobile_number
    ):
        raise MediNovaException(
            message=(
                "Mobile number does not match "
                "the OTP request."
            ),
            status_code=400,
        )

    cooldown = get_resend_cooldown_seconds(
        verification
    )

    if cooldown > 0:
        raise MediNovaException(
            message=(
                f"Please wait {cooldown} seconds "
                "before requesting new OTPs."
            ),
            status_code=429,
        )

    email_otp = generate_otp()
    mobile_otp = generate_otp()

    verification.email_otp_hash = hash_otp(
        email_otp
    )

    verification.mobile_otp_hash = hash_otp(
        mobile_otp
    )

    verification.email_verified = False
    verification.mobile_verified = False
    verification.attempts = 0
    verification.expires_at = get_expiry_time()

    db.add(verification)
    db.commit()
    db.refresh(verification)

    print("\n" + "=" * 60)
    print("MEDINOVA DEVELOPMENT OTP — RESEND")
    print("=" * 60)
    print(f"Email:        {signup_data.email}")
    print(f"Mobile:       {signup_data.mobile_number}")
    print(f"Email OTP:    {email_otp}")
    print(f"Mobile OTP:   {mobile_otp}")
    print(f"Expires:      {verification.expires_at}")
    print("=" * 60 + "\n")

    return {
        "message": (
            "New OTP verification codes generated."
        ),
        "expires_in_seconds": OTP_EXPIRY_MINUTES * 60,
        "resend_cooldown_seconds": 60,
    }


# ============================================================
# SIGNUP - VERIFY OTP
# ============================================================

@router.post(
    "/signup/verify-otp",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def verify_signup_otp(
    signup_data: SignupOTPVerify,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        signup_data.email,
    )

    if existing_user:
        raise MediNovaException(
            message="Email already registered",
            status_code=400,
        )

    existing_mobile = (
        db.query(User)
        .filter(
            User.mobile_number
            == signup_data.mobile_number
        )
        .first()
    )

    if existing_mobile:
        raise MediNovaException(
            message="Mobile number already registered",
            status_code=400,
        )

    verification = get_active_verification(
        db,
        signup_data.email,
    )

    if verification is None:
        raise MediNovaException(
            message=(
                "No active OTP verification found. "
                "Please request new OTPs."
            ),
            status_code=400,
        )

    if (
        verification.mobile_number
        != signup_data.mobile_number
    ):
        raise MediNovaException(
            message=(
                "Mobile number does not match "
                "the OTP request."
            ),
            status_code=400,
        )

    if is_expired(verification):
        raise MediNovaException(
            message=(
                "OTP has expired. "
                "Please request new OTPs."
            ),
            status_code=400,
        )

    if verification.attempts >= MAX_OTP_ATTEMPTS:
        raise MediNovaException(
            message=(
                "Too many incorrect OTP attempts. "
                "Please request new OTPs."
            ),
            status_code=400,
        )

    email_valid = verify_otp(
        signup_data.email_otp,
        verification.email_otp_hash,
    )

    mobile_valid = verify_otp(
        signup_data.mobile_otp,
        verification.mobile_otp_hash,
    )

    if not email_valid or not mobile_valid:
        increment_attempts(
            db,
            verification,
        )

        raise MediNovaException(
            message="Invalid email or mobile OTP.",
            status_code=400,
        )

    mark_email_verified(
        db,
        verification,
    )

    mark_mobile_verified(
        db,
        verification,
    )

    user = create_user(
        db,
        UserCreate(
            full_name=signup_data.full_name,
            email=signup_data.email,
            password=signup_data.password,
        ),
        mobile_number=signup_data.mobile_number,
    )

    return user


# ============================================================
# FORGOT PASSWORD - REQUEST OTP
# ============================================================

@router.post(
    "/forgot-password/request-otp",
    status_code=status.HTTP_200_OK,
)
def request_password_reset_otp(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise MediNovaException(
            message="No account found with this email address.",
            status_code=404,
        )

    verification, otp = (
        create_password_reset_otp(
            db,
            user,
        )
    )

    # Development mode only.
    print("\n" + "=" * 60)
    print("MEDINOVA PASSWORD RESET OTP")
    print("=" * 60)
    print(f"Email:        {user.email}")
    print(f"Reset OTP:    {otp}")
    print(f"Expires:      {verification.expires_at}")
    print("=" * 60 + "\n")

    return {
        "message": (
            "Password reset OTP generated."
        ),
        "expires_in_seconds": OTP_EXPIRY_MINUTES * 60,
    }


# ============================================================
# FORGOT PASSWORD - VERIFY OTP
# ============================================================

@router.post(
    "/forgot-password/verify-otp",
    status_code=status.HTTP_200_OK,
)
def verify_password_reset(
    request: ForgotPasswordVerify,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise MediNovaException(
            message="No account found with this email address.",
            status_code=404,
        )

    verification = (
        get_latest_password_reset_otp(
            db,
            request.email,
        )
    )

    if verification is None:
        raise MediNovaException(
            message=(
                "No password reset OTP found. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    if is_expired(verification):
        raise MediNovaException(
            message=(
                "Password reset OTP has expired. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    if verification.attempts >= MAX_RESET_ATTEMPTS:
        raise MediNovaException(
            message=(
                "Too many incorrect OTP attempts. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    valid = verify_password_reset_otp(
        verification,
        request.otp,
    )

    if not valid:
        increment_reset_attempts(
            db,
            verification,
        )

        raise MediNovaException(
            message="Invalid password reset OTP.",
            status_code=400,
        )

    return {
        "message": "OTP verified successfully.",
        "verified": True,
    }


# ============================================================
# FORGOT PASSWORD - RESET PASSWORD
# ============================================================

@router.post(
    "/forgot-password/reset",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise MediNovaException(
            message="No account found with this email address.",
            status_code=404,
        )

    verification = (
        get_latest_password_reset_otp(
            db,
            request.email,
        )
    )

    if verification is None:
        raise MediNovaException(
            message=(
                "No password reset OTP found. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    if is_expired(verification):
        raise MediNovaException(
            message=(
                "Password reset OTP has expired. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    if verification.attempts >= MAX_RESET_ATTEMPTS:
        raise MediNovaException(
            message=(
                "Too many incorrect OTP attempts. "
                "Please request a new OTP."
            ),
            status_code=400,
        )

    valid = verify_password_reset_otp(
        verification,
        request.otp,
    )

    if not valid:
        increment_reset_attempts(
            db,
            verification,
        )

        raise MediNovaException(
            message="Invalid password reset OTP.",
            status_code=400,
        )

    reset_user_password(
        db,
        user,
        request.new_password,
    )

    # Invalidate this OTP after successful reset.
    verification.email_verified = True
    verification.mobile_verified = True

    db.add(verification)
    db.commit()

    return {
        "message": (
            "Password reset successfully. "
            "You can now log in with your new password."
        ),
    }


# ============================================================
# LEGACY SIGNUP
# ============================================================

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise MediNovaException(
            message="Email already registered",
            status_code=400,
        )

    return create_user(
        db,
        user,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    authenticated_user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if authenticated_user is None:
        raise MediNovaException(
            message="Invalid email or password",
            status_code=401,
        )

    access_token = create_access_token(
        data={
            "sub": authenticated_user.email,
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )