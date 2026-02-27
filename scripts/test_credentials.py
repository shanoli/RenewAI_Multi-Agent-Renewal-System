import os
import sys

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.rag.chroma_store import get_query_embedding, init_chroma

def test_credentials():
    print("Testing Gemini API key configuration...")
    try:
        embedding = get_query_embedding("This is a test.")
        print(f"Successfully generated embedding (length: {len(embedding)})")
    except Exception as e:
        print(f"Failed to generate embedding: {e}")
        return False

    print("\nTesting ChromaDB initialization...")
    try:
        init_chroma()
        print("Successfully initialized ChromaDB.")
    except Exception as e:
        print(f"Failed to initialize ChromaDB: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_credentials():
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
