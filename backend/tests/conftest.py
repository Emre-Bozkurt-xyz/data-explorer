# tests/conftest.py
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make sure backend root (where app/ lives) is on sys.path
ROOT = Path(__file__).resolve().parents[1]  # backend/
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app as fastapi_app
from app.db.base import Base, get_db
import app.db.models  # noqa: F401  # ensure all models are registered


# --- Postgres test DB configuration ---

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    # default assumes tests run inside a container on the same network as `test_db`
    "postgresql+psycopg://dataexplorer:dataexplorer@test_db:5432/dataexplorer_test",
)

engine = create_engine(TEST_DATABASE_URL, future=True)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

# Create a clean schema for the test run
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override FastAPI dependency to use the test DB
fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client() -> TestClient:
    return TestClient(fastapi_app)