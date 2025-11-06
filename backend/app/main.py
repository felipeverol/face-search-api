from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image
from tqdm import tqdm
import numpy as np
import os
import io

from backend.utils.config import DIR_PATH
from backend.utils.database import add_to_chroma, query_chroma, remove_image
from backend.utils.models import generate_embeddings

# Inicializa o app FastAPI
app = FastAPI()

# Configura o middleware CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend e do banco de imagens
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/db", StaticFiles(directory="db"), name="db")

# Endpoint para retornar a página inicial
@app.get("/")
async def frontend():
    return FileResponse("frontend/index.html")

@app.post("/search")
async def search(imagem: UploadFile = File(...), threshold: float = Form(0.6)):
    # Valida o tipo do arquivo enviado
    if not imagem.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail="O arquivo enviado não é uma imagem válida."
        )
    
    # Valida o valor do threshold
    if threshold < 0.0 or threshold > 1.0:
        raise HTTPException(
            status_code=400,
            detail="Threshold deve estar entre 0.0 e 1.0."
        )
   
    # Lê a imagem enviada e gera seus embeddings
    img = await imagem.read()
    img_embeddings = generate_embeddings(img_source=img)
    
    # Se nenhum rosto for identificado, retorna erro 400
    if img_embeddings is None:
        raise HTTPException(
            status_code=400,
            detail="Nenhum rosto identificado na imagem enviada."
        )

    # Consulta o ChromaDB por rostos similares e retorna os resultados
    similar_faces = query_chroma(img_embeddings, threshold)

    return JSONResponse(content={"similar_faces": similar_faces})

@app.post("/upload")
async def upload(imagem: UploadFile = File(...)):
    # Valida o tipo do arquivo enviado
    if not imagem.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail="O arquivo enviado não é uma imagem válida."
        )
    
    # Lê a imagem enviada, salva no diretório e gera seus embeddings
    img = await imagem.read()
    img_embeddings = generate_embeddings(img_source=img)

    # Se nenhum rosto for identificado, retorna erro 400
    if img_embeddings is None:
        raise HTTPException(
            status_code=400,
            detail="Nenhum rosto identificado na imagem enviada."
    )
    
    # Salva a imagem no diretório
    img = Image.open(io.BytesIO(img)).convert('RGB')
    img_path = os.path.join(DIR_PATH, imagem.filename)
    img.save(img_path)
    
    # Adiciona os embeddings ao ChromaDB 
    add_to_chroma(img_path, img_embeddings)

    return JSONResponse(content={"mensagem": "Embeddings adicionados ao ChromaDB com sucesso!"})

@app.post("/create-db")
def create_db():
    # Itera sobre todas as imagens no diretório
    for filename in tqdm(os.listdir(DIR_PATH)):
        # Gera embeddings para cada imagem e adiciona ao ChromaDB
        img_path = os.path.join(DIR_PATH, filename)
        img_embeddings = generate_embeddings(img_path=img_path)

        # Se nenhum rosto for identificado, pula a imagem
        if img_embeddings is None:
            continue
        
        # Adiciona os embeddings ao ChromaDB
        add_to_chroma(img_path, img_embeddings)

    return JSONResponse(content={"mensagem": "Banco ChromaDB criado com sucesso!"})

@app.post("/remove-image")
def remove(id: str = Form(...)):
    # Remove a imagem do ChromaDB pelo ID
    img_path = remove_image(id)

    # Remove o arquivo de imagem do diretório
    if os.path.exists(img_path):
        os.remove(img_path)

    return JSONResponse(content={"mensagem": "Imagem removida com sucesso!"})