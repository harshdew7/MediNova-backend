from sqlalchemy.orm import Session

from app.models.otp_verification import OTPVerification
from app.models.user import User
from app.services.otp_service import (
    generate_otp,
    get_expiry_time,
    hash_otp,
    is_expired,
    verify_otp,
)
from app.utils.security import hash_password


MAX_RESET_ATTEMPTS = 5


def create_password_reset_otp(
    db: Session,
    user: User,
) -> tuple[OTPVerification, str]:
    """Create a password-reset OTP."""

    otp = generate_otp()

    verification = OTPVerification(
        email=user.email,
        mobile_number=user.mobile_number or "",
        purpose="password_reset",
        email_otp_hash=hash_otp(otp),
        mobile_otp_hash=hash_otp(otp),
        email_verified=False,
        mobile_verified=False,
        attempts=0,
        expires_at=get_expiry_time(),
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return verification, otp


def get_latest_password_reset_otp(
    db: Session,
    email: str,
) -> OTPVerification | None:
    """Get the latest password-reset OTP for an email."""

    return (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == "password_reset",
        )
        .order_by(
            OTPVerification.created_at.desc()
        )
        .first()
    )


def verify_password_reset_otp(
    verification: OTPVerification,
    otp: str,
) -> bool:
    """Verify a password-reset OTP."""

    return verify_otp(
        otp,
        verification.email_otp_hash,
    )


def increment_reset_attempts(
    db: Session,
    verification: OTPVerification,
) -> None:
    """Increase failed password-reset attempts."""

    verification.attempts += 1

    db.add(verification)
    db.commit()
    db.refresh(verification)


def reset_user_password(
    db: Session,
    user: User,
    new_password: str,
) -> User:
    """Hash and update the user's password."""

    user.hashed_password = hash_password(
        new_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user