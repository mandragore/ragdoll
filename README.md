# 🔍 Application de Recherche Documentaire RAG (Dockerisée)

Application de recherche documentaire utilisant une architecture RAG (Retrieval-Augmented Generation) pour interroger un corpus de documents avec des réponses générées par IA. **Entièrement conteneurisée avec Docker** pour une reproductibilité maximale.

## 🎯 Fonctionnalités

- **Indexation automatique** des documents (PDF, TXT, MD, DOCX)
- **Recherche sémantique** avec embeddings Sentence Transformers
- **Génération de réponses** contextualisées avec Ollama/Mistral
- **Interface utilisateur** moderne avec Streamlit
- **Stockage vectoriel persistant** avec ChromaDB
- **Affichage des sources** utilisées pour chaque réponse
- **Déploiement Docker** en un seul clic

## 🏗️ Architecture Technique

- **LlamaIndex**: Orchestration RAG et gestion du pipeline
- **ChromaDB**: Base de données vectorielle pour le stockage des embeddings
- **Sentence Transformers**: Modèle d'embeddings (`all-MiniLM-L6-v2`)
- **Ollama/Mistral**: Modèle de langage pour la génération de réponses
- **Streamlit**: Interface utilisateur web
- **Docker**: Conteneurisation et orchestration

## 📋 Prérequis

**Uniquement Docker et Docker Compose !**

```bash
# Vérifier Docker
docker --version

# Vérifier Docker Compose
docker-compose --version
```

**Configuration minimale requise :**
- 8 GB RAM
- 10 GB d'espace disque libre
- Connexion Internet (pour télécharger Mistral au premier démarrage)

## 🚀 Démarrage Rapide

### 1. Préparer vos documents
Placez vos documents dans le répertoire `./data`:
```bash
cp /chemin/vers/vos/documents/*.pdf ./data/
```

Formats supportés: `.pdf`, `.txt`, `.md`, `.docx`

### 2. Lancer l'application
```bash
# Construire et démarrer tous les services
docker-compose up -d

# Suivre les logs (optionnel)
docker-compose logs -f
```

> **Note :** Au premier démarrage, le modèle Mistral (~4GB) sera téléchargé automatiquement. Cela peut prendre 2-5 minutes selon votre connexion.

### 3. Accéder à l'application
Ouvrez votre navigateur à l'adresse : **http://localhost:8501**

### 4. Utiliser l'application

1. **Première utilisation**: L'indexation se fera automatiquement au premier lancement
2. **Poser une question**: Entrez votre question dans le champ de texte
3. **Consulter les résultats**: La réponse s'affichera avec les sources utilisées
4. **Ajouter des documents**: 
   - Ajoutez de nouveaux fichiers dans `./data`
   - Cliquez sur "🔄 Réindexer les documents" dans la sidebar

## 📁 Structure du Projet

```
octoscrub/
├── app.py                  # Application Streamlit principale
├── config.py               # Configuration centralisée
├── document_indexer.py     # Module d'indexation des documents
├── query_engine.py         # Module de traitement des requêtes
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Image Docker de l'application
├── docker-compose.yml      # Orchestration des services
├── .dockerignore           # Exclusions Docker
├── .gitignore              # Exclusions Git
├── README.md               # Documentation
├── data/                   # Documents à indexer (volume Docker)
└── chroma_db/              # Base vectorielle (volume Docker)
```

## 🐳 Gestion Docker

### Commandes utiles

```bash
# Démarrer les services
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f app
docker-compose logs -f ollama

# Redémarrer un service
docker-compose restart app

# Reconstruire l'image
docker-compose build --no-cache

# Voir l'état des services
docker-compose ps

# Nettoyer tout (ATTENTION : supprime les volumes !)
docker-compose down -v
```

### Services

L'application utilise 2 services Docker :

1. **ollama** : Serveur Ollama avec le modèle Mistral
   - Port interne : 11434
   - Volume : `ollama_data` (modèles persistants)

2. **app** : Application Streamlit avec RAG
   - Port : 8501
   - Volumes : `./data`, `./chroma_db`

## 🔧 Configuration

### Variables d'environnement

Vous pouvez personnaliser la configuration dans `docker-compose.yml` :

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434
```

### Paramètres de l'application

Modifiez `config.py` pour ajuster :

```python
# Modèle d'embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Modèle LLM
OLLAMA_MODEL = "mistral"

# Nombre de sources à récupérer
SIMILARITY_TOP_K = 5

# Taille des chunks de texte
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200
```

Après modification, redémarrez :
```bash
docker-compose restart app
```

## 🐛 Dépannage

### Le service Ollama ne démarre pas
```bash
# Vérifier les logs
docker-compose logs ollama

# Redémarrer le service
docker-compose restart ollama
```

### L'application ne trouve pas Ollama
Vérifiez que les 2 services sont UP :
```bash
docker-compose ps
```

Les deux doivent afficher "Up" et "healthy".

### Erreur de mémoire
Augmentez la RAM allouée à Docker dans les paramètres Docker Desktop (minimum 8GB recommandé).

### Le modèle Mistral n'est pas téléchargé
```bash
# Télécharger manuellement
docker-compose exec ollama ollama pull mistral

# Vérifier les modèles installés
docker-compose exec ollama ollama list
```

### Nettoyer et redémarrer
```bash
# Arrêter tout
docker-compose down

# Supprimer les volumes (ATTENTION : perd les données)
docker volume rm octoscrub_ollama_data

# Redémarrer
docker-compose up -d
```

## 📝 Exemples de Questions

- "De quoi parlent les documents ?"
- "Quelles sont les informations principales ?"
- "Résume le contenu des documents"
- "Explique [concept spécifique] mentionné dans les documents"

## 🔒 Confidentialité

- Tous les traitements sont effectués **localement** dans vos conteneurs Docker
- Aucune donnée n'est envoyée à des services externes
- Les embeddings et l'index sont stockés localement dans `./chroma_db`
- Le modèle Mistral tourne localement via Ollama

## 📊 Volumes et Persistance

Les données suivantes sont persistantes entre les redémarrages :

- **./data** : Vos documents (monté depuis l'hôte)
- **./chroma_db** : Base vectorielle ChromaDB (monté depuis l'hôte)
- **ollama_data** : Modèles Ollama (volume Docker nommé)

Pour sauvegarder vos données :
```bash
# Sauvegarde de la base vectorielle
tar -czf chroma_db_backup.tar.gz chroma_db/

# Restauration
tar -xzf chroma_db_backup.tar.gz
```

## 🚢 Déploiement en Production

### Avec port mapping personnalisé
```yaml
# Dans docker-compose.yml
services:
  app:
    ports:
      - "8080:8501"  # Accès via http://localhost:8080
```

### Derrière un reverse proxy (nginx/traefik)
L'application écoute sur `0.0.0.0:8501` et est prête pour un reverse proxy.

## 📄 Licence

Ce projet est fourni à des fins éducatives et de démonstration.

## 🤝 Contribution

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue.

---

**Développé avec ❤️ en utilisant LlamaIndex, ChromaDB, Sentence Transformers, Ollama/Mistral, Streamlit et Docker**
