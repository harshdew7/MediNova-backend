from datetime import datetime, timedelta, timezone
from secrets import randbelow

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.models.otp_verification import OTPVerification


otp_hash = PasswordHash.recommended()

OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    return f"{randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    """Hash an OTP before storing it."""
    return otp_hash.hash(otp)


def verify_otp(
    otp: str,
    hashed_otp: str,
) -> bool:
    """Verify an entered OTP against its hash."""
    return otp_hash.verify(
        otp,
        hashed_otp,
    )


def get_expiry_time() -> datetime:
    """Return the UTC expiry time for a new OTP."""
    return (
        datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )


def create_signup_verification(
    db: Session,
    email: str,
    mobile_number: str,
) -> tuple[OTPVerification, str, str]:
    """
    Create a signup OTP verification record.

    Returns:
        verification record,
        email OTP,
        mobile OTP
    """

    email_otp = generate_otp()
    mobile_otp = generate_otp()

    verification = OTPVerification(
        email=email,
        mobile_number=mobile_number,
        purpose="signup",
        email_otp_hash=hash_otp(email_otp),
        mobile_otp_hash=hash_otp(mobile_otp),
        email_verified=False,
        mobile_verified=False,
        attempts=0,
        expires_at=get_expiry_time(),
    )

    db.add(verification)
    db.commit()
    db.refresh(verification)

    return (
        verification,
        email_otp,
        mobile_otp,
    )


def get_active_verification(
    db: Session,
    email: str,
) -> OTPVerification | None:
    """
    Get the latest active signup OTP
    for an email.
    """

    return (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == "signup",
        )
        .order_by(
            OTPVerification.created_at.desc()
        )
        .first()
    )


def is_expired(
    verification: OTPVerification,
) -> bool:
    """Check whether an OTP has expired."""

    now = datetime.now(timezone.utc)

    expires_at = verification.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return now >= expires_at


def increment_attempts(
    db: Session,
    verification: OTPVerification,
) -> None:
    """Increase failed OTP attempts."""

    verification.attempts += 1

    db.add(verification)
    db.commit()
    db.refresh(verification)


def mark_email_verified(
    db: Session,
    verification: OTPVerification,
) -> None:
    """Mark email OTP as verified."""

    verification.email_verified = True

    db.add(verification)
    db.commit()
    db.refresh(verification)


def mark_mobile_verified(
    db: Session,
    verification: OTPVerification,
) -> None:
    """Mark mobile OTP as verified."""

    verification.mobile_verified = True

    db.add(verification)
    db.commit()
    db.refresh(verification)


def get_resend_cooldown_seconds(
    verification: OTPVerification,
) -> int:
    """
    Return remaining resend cooldown seconds.

    A new OTP can be requested 60 seconds after
    the previous verification record was created.
    """

    created_at = verification.created_at

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    elapsed = (
        datetime.now(timezone.utc)
        - created_at
    ).total_seconds()

    remaining = (
        RESEND_COOLDOWN_SECONDS
        - int(elapsed)
    )

    return max(0, remaining)