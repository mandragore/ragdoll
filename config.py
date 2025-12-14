"""
Configuration centralisée pour l'application de recherche documentaire
"""
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# Configuration des embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384  # Dimension pour all-MiniLM-L6-v2

# Configuration Ollama/Llama3.2
OLLAMA_MODEL = "llama3.2:1b"  # Modèle léger (1.3GB) avec excellent support français
# Dans Docker, on utilise le nom du service comme hostname
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_REQUEST_TIMEOUT = 120.0

# Configuration ChromaDB
CHROMA_COLLECTION_NAME = "documents"

# Configuration de recherche
SIMILARITY_TOP_K = 5  # Nombre de chunks pertinents à récupérer
CHUNK_SIZE = 1024  # Taille des chunks de texte
CHUNK_OVERLAP = 200  # Chevauchement entre chunks

# Configuration Streamlit
APP_TITLE = "RAG Doll"
APP_ICON = "🪆"
