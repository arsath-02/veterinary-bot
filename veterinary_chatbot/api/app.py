from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import faiss
import numpy as np
from utils.embedding_utils import create_embeddings, create_faiss_index
from utils.response_generation import generate_response

app = FastAPI()

# Load FAISS index
index = faiss.read_index("embeddings/faiss_index.idx")

class Query(BaseModel):
    query: str
    species: str

@app.post("/get_response/")
def get_response(query: Query):
    # Retrieve embeddings for the species and use FAISS to find nearest match
    user_query_embedding = create_embeddings({query.species: [query.query]})[query.species][0]
    _, I = index.search(np.array([user_query_embedding]).astype("float32"), k=1)
    
    # Fetch and return response
    species_embedding = index.reconstruct(int(I[0][0]))
    response = generate_response(query.query, species_embedding)
    return {"response": response}
