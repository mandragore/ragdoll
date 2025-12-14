"""
Module d'indexation des documents avec LlamaIndex et ChromaDB
"""
import os
from typing import List
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
import chromadb

from config import (
    DATA_DIR,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_REQUEST_TIMEOUT,
    CHROMA_COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


class DocumentIndexer:
    """Classe pour indexer les documents avec LlamaIndex et ChromaDB"""
    
    def __init__(self):
        """Initialise l'indexeur avec la configuration"""
        # Configuration des embeddings
        self.embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL
        )
        
        # Configuration du LLM
        self.llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            request_timeout=OLLAMA_REQUEST_TIMEOUT,
        )
        
        # Configuration globale de LlamaIndex
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        Settings.chunk_size = CHUNK_SIZE
        Settings.chunk_overlap = CHUNK_OVERLAP
        
        # Initialisation de ChromaDB avec configuration
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_DB_DIR,
            settings=chromadb.config.Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME
        )
        
        # Configuration du vector store
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        self.index = None
    
    def load_documents(self) -> List:
        """Charge les documents depuis le répertoire data"""
        if not os.path.exists(DATA_DIR):
            raise FileNotFoundError(f"Le répertoire {DATA_DIR} n'existe pas")
        
        # Vérifier s'il y a des fichiers
        files = os.listdir(DATA_DIR)
        if not files:
            raise ValueError(f"Aucun document trouvé dans {DATA_DIR}")
        
        print(f"📂 Chargement des documents depuis {DATA_DIR}...")
        reader = SimpleDirectoryReader(
            input_dir=DATA_DIR,
            recursive=True,
            required_exts=[".pdf", ".txt", ".md", ".docx"]
        )
        documents = reader.load_data()
        print(f"✅ {len(documents)} documents chargés")
        return documents
    
    def index_documents(self) -> VectorStoreIndex:
        """Indexe les documents et crée l'index vectoriel"""
        print("🔄 Indexation des documents en cours...")
        
        # Charger les documents
        documents = self.load_documents()
        
        # Créer l'index
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            show_progress=True,
        )
        
        print("✅ Indexation terminée avec succès!")
        return self.index
    
    def load_existing_index(self) -> VectorStoreIndex:
        """Charge un index existant depuis ChromaDB"""
        print("📥 Chargement de l'index existant...")
        
        # Vérifier si la collection existe et contient des données
        if self.chroma_collection.count() == 0:
            print("⚠️  Aucun index existant trouvé, création d'un nouvel index...")
            return self.index_documents()
        
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
        )
        
        print(f"✅ Index chargé ({self.chroma_collection.count()} vecteurs)")
        return self.index
    
    def get_index(self) -> VectorStoreIndex:
        """Récupère l'index (charge l'existant ou en crée un nouveau)"""
        if self.index is None:
            try:
                self.index = self.load_existing_index()
            except Exception as e:
                print(f"⚠️  Erreur lors du chargement de l'index: {e}")
                print("🔄 Création d'un nouvel index...")
                self.index = self.index_documents()
        
        return self.index
    
    def get_document_count(self) -> int:
        """Retourne le nombre de vecteurs dans l'index"""
        return self.chroma_collection.count()


if __name__ == "__main__":
    # Test de l'indexeur
    indexer = DocumentIndexer()
    index = indexer.index_documents()
    print(f"\n📊 Nombre de vecteurs dans l'index: {indexer.get_document_count()}")
