''' Geração de embeddings faciais usando MTCNN e InceptionResnetV1. '''

from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import io

# Inicializa MTCNN e InceptionResnetV1
mtcnn = MTCNN(image_size=160, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def generate_embeddings(img_path=None, img_source=None):
    # Gera embeddings faciais a partir do caminho da imagem ou do conteúdo da imagem
    if img_path is not None:
        img = Image.open(img_path).convert('RGB')
    elif img_source is not None:
        img = Image.open(io.BytesIO(img_source)).convert('RGB')
    
    img_cropped = mtcnn(img)

    # Se nenhum rosto for detectado, retorna None
    if img_cropped is None:
        return None

    # Gera e retorna os embeddings faciais
    return  resnet(img_cropped.unsqueeze(0)).tolist()[0] 