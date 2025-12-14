"""
Application Streamlit pour la recherche documentaire avec RAG
"""
import streamlit as st
import os
from query_engine import QueryEngine
from document_indexer import DocumentIndexer
from config import APP_TITLE, APP_ICON, DATA_DIR

# Configuration de la page
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #2ecc71;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_query_engine():
    """Initialise et met en cache le moteur de requêtes"""
    engine = QueryEngine()
    engine.initialize()
    return engine


def main():
    """Fonction principale de l'application"""
    
    # En-tête
    st.markdown(f'<div class="main-header">{APP_ICON} Recherche Documentaire RAG</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Informations sur l'index
        st.subheader("📊 Statistiques")
        try:
            indexer = DocumentIndexer()
            doc_count = indexer.get_document_count()
            st.metric("Vecteurs indexés", doc_count)
            
            # Compter les fichiers dans data
            if os.path.exists(DATA_DIR):
                files = [f for f in os.listdir(DATA_DIR) 
                        if os.path.isfile(os.path.join(DATA_DIR, f))]
                st.metric("Fichiers dans ./data", len(files))
            
        except Exception as e:
            st.warning(f"Impossible de charger les statistiques: {e}")
        
        st.divider()
        
        # Bouton de réindexation
        st.subheader("🔄 Gestion de l'index")
        st.info("Utilisez ce bouton après avoir ajouté de nouveaux documents dans ./data")
        
        if st.button("🔄 Réindexer les documents", type="primary"):
            with st.spinner("Réindexation en cours..."):
                try:
                    # Invalider le cache et réindexer
                    st.cache_resource.clear()
                    engine = QueryEngine()
                    engine.reindex_documents()
                    st.success("✅ Réindexation terminée avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de la réindexation: {e}")
        
        st.divider()
        
        # Informations
        st.subheader("ℹ️ À propos")
        st.markdown("""
        Cette application utilise:
        - **LlamaIndex** pour l'orchestration
        - **ChromaDB** pour le stockage vectoriel
        - **Sentence Transformers** pour les embeddings
        - **Ollama/Mistral** pour la génération
        """)
        
        st.divider()
        
        # Instructions
        with st.expander("📖 Instructions"):
            st.markdown("""
            1. Placez vos documents dans le dossier `./data`
            2. Cliquez sur "Réindexer" si vous avez ajouté de nouveaux documents
            3. Posez vos questions dans le champ de texte
            4. Consultez les réponses et les sources
            
            **Formats supportés:** PDF, TXT, MD, DOCX
            """)
    
    # Zone principale
    st.header("💬 Posez votre question")
    
    # Champ de saisie de la question
    question = st.text_area(
        "Entrez votre question sur les documents:",
        height=100,
        placeholder="Exemple: De quoi parlent les documents ? Quelles sont les informations principales ?"
    )
    
    # Bouton de recherche
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔍 Rechercher", type="primary", use_container_width=True)
    
    # Traitement de la requête
    if search_button and question:
        with st.spinner("🤔 Recherche de la réponse..."):
            try:
                # Obtenir le moteur de requêtes
                engine = get_query_engine()
                
                # Exécuter la requête
                result = engine.get_response_with_sources(question)
                
                # Afficher la réponse
                st.header("💡 Réponse")
                st.markdown(f'<div class="answer-box">{result["answer"]}</div>', 
                           unsafe_allow_html=True)
                
                # Afficher les sources
                if result['sources']:
                    st.header("📚 Sources")
                    st.caption(f"{len(result['sources'])} sources utilisées pour générer cette réponse")
                    
                    for i, source in enumerate(result['sources'], 1):
                        with st.expander(f"📄 Source {i} - Score: {source['score']:.3f}"):
                            if 'file_name' in source:
                                st.markdown(f"**Fichier:** `{source['file_name']}`")
                            st.markdown("**Extrait:**")
                            st.markdown(f'<div class="source-box">{source["text"]}</div>', 
                                      unsafe_allow_html=True)
                else:
                    st.info("Aucune source spécifique n'a été utilisée pour cette réponse.")
                
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de la requête: {e}")
                st.exception(e)
    
    elif search_button and not question:
        st.warning("⚠️ Veuillez entrer une question avant de rechercher.")
    
    # Message d'accueil si aucune question n'a été posée
    if not search_button:
        st.info("👆 Entrez votre question ci-dessus et cliquez sur 'Rechercher' pour commencer.")
        
        # Exemples de questions
        st.subheader("💡 Exemples de questions")
        examples = [
            "De quoi parlent les documents ?",
            "Quelles sont les informations principales ?",
            "Résume le contenu des documents",
            "Quels sont les points clés abordés ?"
        ]
        
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                st.markdown(f"- {example}")


if __name__ == "__main__":
    main()
