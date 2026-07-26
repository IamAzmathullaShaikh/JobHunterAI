"""v1 schema recovery

Revision ID: 8a286fd41f58
Revises: 7c286fd41f57
Create Date: 2026-07-26 01:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8a286fd41f58'
down_revision: Union[str, Sequence[str], None] = '7c286fd41f57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # --- 1. job_listings ---
    if not column_exists('job_listings', 'required_skills'):
        op.add_column('job_listings', sa.Column('required_skills', sa.JSON(), nullable=True))
    if not column_exists('job_listings', 'seniority'):
        op.add_column('job_listings', sa.Column('seniority', sa.String(length=50), nullable=True))
    if not column_exists('job_listings', 'technologies'):
        op.add_column('job_listings', sa.Column('technologies', sa.JSON(), nullable=True))
    if not column_exists('job_listings', 'benefits'):
        op.add_column('job_listings', sa.Column('benefits', sa.JSON(), nullable=True))

    # --- 2. job_applications ---
    if not column_exists('job_applications', 'priority'):
        op.add_column('job_applications', sa.Column('priority', sa.Integer(), nullable=True, server_default='1'))
    if not column_exists('job_applications', 'tags'):
        op.add_column('job_applications', sa.Column('tags', sa.JSON(), nullable=True))

    # --- 3. ai_analyses ---
    for col in ['readability_score', 'action_verb_score', 'formatting_score', 'quantification_score']:
        if not column_exists('ai_analyses', col):
            op.add_column('ai_analyses', sa.Column(col, sa.Float(), nullable=True, server_default='0.0'))

    if not column_exists('ai_analyses', 'detailed_recommendations'):
        op.add_column('ai_analyses', sa.Column('detailed_recommendations', sa.JSON(), nullable=True))

    # Safely convert types
    try:
        op.execute('ALTER TABLE ai_analyses ALTER COLUMN keywords_matched TYPE JSON USING keywords_matched::json')
    except:
        pass
    try:
        op.execute('ALTER TABLE ai_analyses ALTER COLUMN keywords_missing TYPE JSON USING keywords_missing::json')
    except:
        pass

    # --- 4. match_history ---
    for col in ['readability_score', 'action_verb_score', 'formatting_score', 'quantification_score']:
        if not column_exists('match_history', col):
            op.add_column('match_history', sa.Column(col, sa.Float(), nullable=True, server_default='0.0'))

    # --- 5. resume_master_profiles ---
    for col in ['projects', 'languages', 'achievements', 'awards', 'publications', 'volunteer', 'interests', 'references']:
        if not column_exists('resume_master_profiles', col):
            op.add_column('resume_master_profiles', sa.Column(col, sa.JSON(), nullable=True))

    # --- 6. recruiter_contacts ---
    if not column_exists('recruiter_contacts', 'match_explanation'):
        op.add_column('recruiter_contacts', sa.Column('match_explanation', sa.Text(), nullable=True))

    # --- 7. Cleanup ---
    op.execute('DROP TABLE IF EXISTS recruiter_leads CASCADE')


def downgrade() -> None:
    pass
