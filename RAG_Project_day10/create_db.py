# ============================================================
# create_db.py
# Purpose:
# Read knowledge.txt
# Convert text into embeddings
# Store embeddings inside ChromaDB
# ============================================================
 
 
# -----------------------------
# Import required libraries
# -----------------------------
 
# Reads the text file
import os
 
# Creates embeddings
from sentence_transformers import SentenceTransformer
 
# Chroma Vector Database
import chromadb
 
# Used to create a persistent database
from chromadb.config import Settings
 
 
# -----------------------------
# Load embedding model
# -----------------------------
 
# all-MiniLM-L6-v2 is a lightweight embedding model
# It converts sentences into vectors (embeddings)
 
model = SentenceTransformer("all-MiniLM-L6-v2")
 
 
# -----------------------------
# Read knowledge.txt
# -----------------------------
 
# Open the knowledge file
 
with open("knowledge.txt", "r", encoding="utf-8") as file:
 
    # Read entire file
    text = file.read()
 
 
# -----------------------------
# Split knowledge into chunks
# -----------------------------
 
# Each paragraph becomes one document
 
documents = text.split("\n\n")
 
 
# Remove empty chunks
 
documents = [doc.strip() for doc in documents if doc.strip()]
 
 
print("Documents Loaded:", len(documents))
 
 
# -----------------------------
# Create embeddings
# -----------------------------
 
# Convert every document into a vector
 
embeddings = model.encode(documents).tolist()
 
 
print("Embeddings Created")
 
 
# -----------------------------
# Create Chroma Database
# -----------------------------
 
client = chromadb.PersistentClient(path="chroma_db")
 
 
# -----------------------------
# Create collection
# -----------------------------
 
collection = client.get_or_create_collection(
    name="genai_knowledge"
)
 
 
# -----------------------------
# Store every document
# -----------------------------
 
for i, doc in enumerate(documents):
 
    collection.add(
 
        ids=[str(i)],
 
        documents=[doc],
 
        embeddings=[embeddings[i]]
 
    )
 
 
print("Database Created Successfully!")
print("Saved inside folder -> chroma_db")