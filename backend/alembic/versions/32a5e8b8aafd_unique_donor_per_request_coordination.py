"""Prevent duplicate donor coordination records per request.

Revision ID: 32a5e8b8aafd
Revises: afd9c19a7b34
"""

from typing import Sequence, Union

from alembic import op


revision: str = "32a5e8b8aafd"
down_revision: Union[str, None] = "afd9c19a7b34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_coordination_request_donor",
        "donation_coordination",
        ["request_id", "donor_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_coordination_request_donor",
        "donation_coordination",
        type_="unique",
    )
