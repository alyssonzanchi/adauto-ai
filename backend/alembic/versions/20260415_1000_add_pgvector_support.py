"""Add pgvector support for semantic search

Revision ID: 20260415_1000
Revises: 351b165a4db9
Create Date: 2026-04-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260415_1000'
down_revision = '351b165a4db9'
branch_labels = None
depends_on = None


def upgrade():
    """Add pgvector extension and vector columns to vehicles table."""

    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Add vector columns for embeddings (1536 dimensions for OpenAI text-embedding-3-small)
    # Using raw SQL to create vector columns since SQLAlchemy doesn't have native support
    op.execute("""
        ALTER TABLE vehicles
        ADD COLUMN IF NOT EXISTS description_embedding vector(1536),
        ADD COLUMN IF NOT EXISTS features_embedding vector(1536)
    """)

    # Note: HNSW indexes will be created after embeddings are populated
    # They require columns to have data with NOT NULL constraint



def downgrade():
    """Remove pgvector support."""

    # Drop vector columns
    op.execute("""
        ALTER TABLE vehicles
        DROP COLUMN IF EXISTS features_embedding,
        DROP COLUMN IF EXISTS description_embedding
    """)

    # Drop pgvector extension (optional - keep it if used elsewhere)
    # op.execute('DROP EXTENSION IF EXISTS vector')
