"""initial baseline migration

Revision ID: 0001_initial_baseline
Revises:
Create Date: 2026-11-17 22:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline migration for infrastructure and scaffolding.
    # Concrete domain tables will be added in Milestones 1 through 5.
    pass


def downgrade() -> None:
    pass
