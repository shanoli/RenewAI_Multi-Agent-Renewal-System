"""
Pytest configuration — sets up test SQLite DB.
"""
import pytest
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session-scoped async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def setup_test_db():
    """Initialize test database before all tests."""
    os.environ["SQLITE_DB_PATH"] = "./data/renewai_test.db"
    os.environ["CHROMA_DB_PATH"] = "./data/chroma_test"
    os.makedirs("data", exist_ok=True)
    
    from app.db.database import init_db
    await init_db()
    yield
    
    # Cleanup test DB
    test_db = "./data/renewai_test.db"
    if os.path.exists(test_db):
        os.remove(test_db)
