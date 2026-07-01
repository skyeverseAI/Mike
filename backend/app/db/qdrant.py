from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.core.config import settings


client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

def init_qdrant():
    if not client.collection_exists('documents'):
        client.create_collection(
            collection_name='documents',
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )