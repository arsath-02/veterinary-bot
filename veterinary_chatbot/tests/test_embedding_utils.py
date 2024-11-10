# tests/test_embedding_utils.py
import faiss
import numpy as np
from utils.embedding_utils import create_embeddings, create_faiss_index

# Define a simple test dataset
test_data = {
    "dog": ["Dog care guide", "Dog health tips"],
    "cat": ["Cat care guide", "Cat health tips"]
}

def test_create_embeddings():
    # Generate embeddings
    embeddings = create_embeddings(test_data)
    
    # Check if embeddings are created correctly
    assert "dog" in embeddings and "cat" in embeddings, "Embeddings should contain keys for each species."
    assert len(embeddings["dog"]) == 2, "There should be 2 embeddings for 'dog'."
    assert embeddings["dog"][0].shape == (768,), "Each embedding should have shape (768,)."

    print("create_embeddings() test passed.")

def test_create_faiss_index():
    # Generate embeddings
    embeddings = create_embeddings(test_data)
    
    # Create FAISS index
    index = create_faiss_index(embeddings)
    
    # Check the number of embeddings in the index
    assert index.ntotal == 4, "FAISS index should contain embeddings for all entries in test_data."
    
    print("create_faiss_index() test passed.")

def test_faiss_retrieval():
    # Generate embeddings and create FAISS index
    embeddings = create_embeddings(test_data)
    index = create_faiss_index(embeddings)
    
    # Convert a sample query to an embedding
    query_embedding = create_embeddings({"dog": ["Dog health tips"]})["dog"][0].astype("float32")
    
    # Search for the nearest neighbor in FAISS index
    distances, indices = index.search(np.array([query_embedding]), k=1)
    
    # Ensure we retrieve at least one result and the nearest neighbor index is within bounds
    assert len(indices[0]) > 0, "No neighbors were found."
    assert indices[0][0] < index.ntotal, "Retrieved index is out of range."

    print("FAISS retrieval test passed.")

# Run tests
if __name__ == "__main__":
    test_create_embeddings()
    test_create_faiss_index()
    test_faiss_retrieval()

