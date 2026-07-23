"""Initial baseline schema

Revision ID: 537284997112
Revises: 
Create Date: 2026-07-16 01:37:31.083525

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '537284997112'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # --- job_listings ---
    op.create_table('job_listings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('job_id_raw', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('work_place_type', sa.String(length=50), nullable=True),
        sa.Column('job_type', sa.String(length=50), server_default='Full-Time', nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('description_raw', sa.Text(), nullable=False),
        sa.Column('description_clean', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('salary_currency', sa.String(length=10), nullable=True),
        sa.Column('salary_raw', sa.Text(), nullable=True),
        sa.Column('is_starred', sa.Boolean(), nullable=False),
        sa.Column('is_suspicious', sa.Boolean(), nullable=False),
        sa.Column('date_posted', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_scraped', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_listings_company_name'), 'job_listings', ['company_name'], unique=False)
    op.create_index(op.f('ix_job_listings_job_id_raw'), 'job_listings', ['job_id_raw'], unique=True)
    op.create_index(op.f('ix_job_listings_title'), 'job_listings', ['title'], unique=False)
    op.create_index(op.f('ix_job_listings_user_id'), 'job_listings', ['user_id'], unique=False)

    # --- ai_analyses ---
    op.create_table('ai_analyses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('fit_summary', sa.Text(), nullable=False),
        sa.Column('keywords_matched', sa.Text(), nullable=False),
        sa.Column('keywords_missing', sa.Text(), nullable=False),
        sa.Column('suggested_resume_path', sa.String(length=500), nullable=True),
        sa.Column('suggested_cover_letter_path', sa.String(length=500), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job_listings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )

    # --- job_applications ---
    op.create_table('job_applications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('job_url', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('WISHLIST', 'APPLIED', 'INTERVIEWING', 'OFFERED', 'REJECTED', 'ARCHIVED', name='applicationstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recruiter_name', sa.String(length=255), nullable=True),
        sa.Column('recruiter_email', sa.String(length=255), nullable=True),
        sa.Column('applied_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('final_res_used', sa.String(length=500), nullable=True),
        sa.Column('final_cover_used', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_listings.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )
    op.create_index(op.f('ix_job_applications_company_name'), 'job_applications', ['company_name'], unique=False)

    # --- user_profiles ---
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('total_experience_years', sa.Float(), nullable=True),
        sa.Column('education', sa.JSON(), nullable=True),
        sa.Column('key_skills', sa.JSON(), nullable=True),
        sa.Column('recommended_search_queries', sa.JSON(), nullable=True),
        sa.Column('experience_highlights', sa.JSON(), nullable=True),
        sa.Column('raw_resume_text', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('user_profiles')
    op.drop_table('job_applications')
    op.drop_table('ai_analyses')
    op.drop_table('job_listings')
