"""add otp purpose

Revision ID: e1f62fb3617e
Revises: 9cbf77de34bc
Create Date: 2026-08-20 23:12:31.327373

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f62fb3617e"
down_revision: Union[str, Sequence[str], None] = "9cbf77de34bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the column with a temporary default so
    # existing OTP records receive the signup purpose.
    op.add_column(
        "otp_verifications",
        sa.Column(
            "purpose",
            sa.String(length=30),
            nullable=False,
            server_default="signup",
        ),
    )

    # Remove the database-level default after
    # existing records have been populated.
    op.alter_column(
        "otp_verifications",
        "purpose",
        server_default=None,
    )

    op.create_index(
        op.f("ix_otp_verifications_purpose"),
        "otp_verifications",
        ["purpose"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_otp_verifications_purpose"),
        table_name="otp_verifications",
    )

    op.drop_column(
        "otp_verifications",
        "purpose",
    )