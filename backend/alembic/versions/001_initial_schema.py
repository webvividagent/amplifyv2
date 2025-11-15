"""Initial schema with users, repositories, sessions, messages, and code blocks

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('subscription_tier', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table(
        'repositories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('git_url', sa.String(), nullable=True),
        sa.Column('local_path', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('indexed', sa.Boolean(), nullable=False),
        sa.Column('index_version', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_synced', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_repositories_name'), 'repositories', ['name'], unique=False)

    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('context', postgresql.JSON(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('files_referenced', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('tools_used', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'code_blocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('repository_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('start_line', sa.Integer(), nullable=False),
        sa.Column('end_line', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_name', sa.String(), nullable=True),
        sa.Column('dependencies', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('imports', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('docstring', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_code_blocks_file_path'), 'code_blocks', ['file_path'], unique=False)
    op.create_index(op.f('ix_code_blocks_entity_name'), 'code_blocks', ['entity_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_code_blocks_entity_name'), table_name='code_blocks')
    op.drop_index(op.f('ix_code_blocks_file_path'), table_name='code_blocks')
    op.drop_table('code_blocks')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_repositories_name'), table_name='repositories')
    op.drop_table('repositories')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
