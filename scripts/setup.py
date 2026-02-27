"""
One-shot setup script: initialize DB + push all sample data + RAG.
Run: python scripts/setup.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    print("=" * 60)
    print("  RenewAI Setup Script")
    print("=" * 60)
    
    # Step 1: Initialize DB
    print("\n[1/3] Initializing SQLite database...")
    from app.db.database import init_db
    await init_db()
    
    # Step 2: Populate SQLite with sample data
    print("\n[2/3] Populating SQLite with sample data...")
    from scripts.populate_data import populate
    await populate()
    
    # Step 3: Populate RAG (Chroma)
    print("\n[3/3] Populating Chroma RAG collections...")
    from scripts.populate_rag import populate_rag
    populate_rag()
    
    print("\n" + "=" * 60)
    print("  ✅ Setup Complete!")
    print("  Start the server: uvicorn app.main:app --reload")
    print("  Open Swagger UI: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
