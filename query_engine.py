"""
Module de traitement des requêtes avec LlamaIndex et Ollama/Mistral
"""
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

from document_indexer import DocumentIndexer
from config import SIMILARITY_TOP_K


class QueryEngine:
    """Classe pour traiter les requêtes utilisateur"""
    
    def __init__(self):
        """Initialise le moteur de requêtes"""
        self.indexer = DocumentIndexer()
        self.index = None
        self.query_engine = None
    
    def initialize(self):
        """Initialise l'index et le moteur de requêtes"""
        print("🔧 Initialisation du moteur de requêtes...")
        
        # Récupérer ou créer l'index
        self.index = self.indexer.get_index()
        
        # Créer le retriever
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=SIMILARITY_TOP_K,
        )
        
        # Créer le query engine
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
        )
        
        print("✅ Moteur de requêtes initialisé")
    
    def query(self, question: str):
        """
        Traite une requête utilisateur
        
        Args:
            question: La question de l'utilisateur
            
        Returns:
            Response object contenant la réponse et les sources
        """
        if self.query_engine is None:
            self.initialize()
        
        print(f"\n❓ Question: {question}")
        print("🔍 Recherche en cours...")
        
        # Exécuter la requête
        response = self.query_engine.query(question)
        
        return response
    
    def get_response_with_sources(self, question: str) -> dict:
        """
        Traite une requête et retourne la réponse avec les sources
        
        Args:
            question: La question de l'utilisateur
            
        Returns:
            Dict contenant 'answer' et 'sources'
        """
        response = self.query(question)
        
        # Extraire les sources
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                source_info = {
                    'text': node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text,
                    'score': node.score,
                }
                
                # Ajouter le nom du fichier si disponible
                if hasattr(node.node, 'metadata') and 'file_name' in node.node.metadata:
                    source_info['file_name'] = node.node.metadata['file_name']
                
                sources.append(source_info)
        
        return {
            'answer': str(response),
            'sources': sources,
            'response_object': response
        }
    
    def reindex_documents(self):
        """Réindexe tous les documents"""
        print("🔄 Réindexation des documents...")
        self.index = self.indexer.index_documents()
        
        # Recréer le query engine avec le nouvel index
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=SIMILARITY_TOP_K,
        )
        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
        )
        
        print("✅ Réindexation terminée")


if __name__ == "__main__":
    # Test du moteur de requêtes
    engine = QueryEngine()
    engine.initialize()
    
    # Test avec une question
    test_question = "De quoi parlent les documents ?"
    result = engine.get_response_with_sources(test_question)
    
    print(f"\n💡 Réponse: {result['answer']}")
    print(f"\n📚 Sources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"\n{i}. Score: {source['score']:.3f}")
        if 'file_name' in source:
            print(f"   Fichier: {source['file_name']}")
        print(f"   Extrait: {source['text']}")
