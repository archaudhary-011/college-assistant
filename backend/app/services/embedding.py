import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import EMBEDDING_MODEL

_model = SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(texts: list[str]) -> np.ndarray:
    return _model.encode(texts, show_progress_bar=False)


def get_model() -> SentenceTransformer:
    return _model
