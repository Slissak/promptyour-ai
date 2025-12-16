"""
Alembic environment configuration
"""
import sys
import os
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
# from sqlalchemy.ext.asyncio import create_async_engine # Not needed for Alembic's env.py
from alembic import context

# Import your models' Base
from backend.app.db.base_class import Base
# from app.core.config import settings # Not directly used for URL in Alembic
import backend.app.db.models  # Import models to ensure they are registered with Base.metadata
import backend.app.models.user  # Import User model explicitly
import shared_python.db.models.usage  # Import UserUsage model

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Get DATABASE_URL from environment, convert to sync for Alembic
database_url = os.environ.get("DATABASE_URL")
print(f"DEBUG (env.py): Raw DATABASE_URL from os.environ: {database_url}")
if database_url:
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    print(f"DEBUG (env.py): Sync DATABASE_URL for Alembic: {sync_database_url}")
    config.set_main_option("sqlalchemy.url", sync_database_url)
else:
    raise ValueError("DATABASE_URL environment variable not set.")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = config.attributes.get("connection", None)
    if connectable is None:
        # only create an engine if we don't have a connection
        # this allows us to run migrations with a database connection
        # that's already established (e.g. for testing)
        from sqlalchemy import create_engine
        connectable = create_engine(
            config.get_main_option("sqlalchemy.url"),
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
