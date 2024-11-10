# utils/embedding_utils.py
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

# Initialize tokenizer and model once at the module level
tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-large")
model = AutoModel.from_pretrained("intfloat/e5-large")

def create_embeddings(data):
    embeddings = {}
    for species, texts in data.items():
        embeddings[species] = []
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                embedding = model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()
            embeddings[species].append(embedding)
    return embeddings

def create_faiss_index(embeddings):
    index = faiss.IndexFlatL2(768)  # 768 matches the embedding dimension of E5-large
    for species, vectors in embeddings.items():
        np_vectors = np.array(vectors).astype("float32")
        index.add(np_vectors)
    return index
