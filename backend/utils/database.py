''' Configurações e operações do banco de dados vetorial ChromaDB. '''

import numpy as np
import chromadb
import uuid

from backend.utils.config import CHROMA_PATH

# Configuração do ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="faces")

def add_to_chroma(img_path, img_embeddings):
    # Adiciona os embeddings e o caminho da imagem ao ChromaDB
    try:
        id = str(uuid.uuid4())
        collection.add(
            embeddings=[img_embeddings],
            documents=[img_path],
            ids=[id],  
        )
    except Exception as e:
        print(f"Erro ao adicionar {img_path} ao ChromaDB: {e}")

def query_chroma(img_embeddings, threshold):
    # Retorna todos os embeddings no ChromaDB 
    total_items = collection.count()    
    results = collection.query(
        query_embeddings=[img_embeddings],
        n_results=total_items,
        include=["documents", "embeddings"]
    )
    
    # Filtra resultados com similaridade acima do limiar (threshold)
    similar_faces = []
    for id, doc, db_embedding in zip(results["ids"][0], results["documents"][0], results["embeddings"][0]):
        similarity = np.dot(img_embeddings, db_embedding) / (np.linalg.norm(img_embeddings) * np.linalg.norm(db_embedding))
        if similarity > threshold:
            similar_faces.append({"id": id, "img_path": doc, "similarity": float(similarity)})

    return similar_faces

def remove_image(id):
    # Obtém o caminho da imagem antes de removê-la
    results = collection.get(ids=[id])
    img_path = results['documents'][0]
    
    # Remove uma imagem do ChromaDB pelo ID
    try:
        collection.delete(ids=[id])
    except Exception as e:
        print(f"Erro ao remover {id} do ChromaDB: {e}")

    return img_path