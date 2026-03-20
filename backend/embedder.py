import httpx
import numpy as np
import faiss

OLLAMA_URL = "http://localhost:11434"
MODEL = "nomic-embed-text"
DIM = 768

def embed(text: str) -> np.ndarray:
    text = text.replace("\n", " ").strip()[:4000]
    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": MODEL, "prompt": text},
            timeout=120        # increased timeout
        )
        vec = np.array(r.json()["embedding"], dtype="float32")
        faiss.normalize_L2(vec.reshape(1, -1))
        return vec
    except Exception as e:
        print(f"Embedding error: {e}")
        # Return a zero vector instead of crashing
        vec = np.zeros(DIM, dtype="float32")
        return vec

def build_index(vectors: list[np.ndarray]) -> faiss.IndexFlatIP:
    index = faiss.IndexFlatIP(DIM)
    matrix = np.vstack(vectors).astype("float32")
    index.add(matrix)
    return index

def search(index: faiss.IndexFlatIP, query_vec: np.ndarray, k: int):
    k = min(k, index.ntotal)
    scores, indices = index.search(query_vec.reshape(1, -1), k)
    return indices[0], scores[0]