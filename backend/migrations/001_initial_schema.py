"""Initial migration script"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Create database schema"""
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='Active'),
        sa.Column('duration_months', sa.Integer(), nullable=True),
        sa.Column('expected_budget', sa.Float(), nullable=True),
        sa.Column('actual_budget', sa.Float(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('ix_projects_name', 'projects', ['name'])
    
    # Risk assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('assessor_id', sa.Integer(), nullable=False),
        sa.Column('probability', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(50), nullable=False),
        sa.Column('assessment_method', sa.String(50), nullable=False),
        sa.Column('schedule_impact', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_impact', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('resource_impact', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('complexity_impact', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('advanced_impact', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('input_parameters', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['assessor_id'], ['users.id']),
    )
    
    # URL scan results table
    op.create_table(
        'url_scan_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('url', sa.String(2048), nullable=False),
        sa.Column('repository_type', sa.String(50), nullable=True),
        sa.Column('project_category', sa.String(50), nullable=True),
        sa.Column('documentation_quality', sa.String(50), nullable=True),
        sa.Column('update_frequency', sa.String(50), nullable=True),
        sa.Column('maturity_stage', sa.String(50), nullable=True),
        sa.Column('code_complexity', sa.String(50), nullable=True),
        sa.Column('calculated_risk', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.92'),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
    )

def downgrade():
    """Drop all tables"""
    op.drop_table('url_scan_results')
    op.drop_table('risk_assessments')
    op.drop_table('projects')
    op.drop_table('users')
