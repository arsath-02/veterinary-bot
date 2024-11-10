from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

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

embeddings = create_embeddings(data)
