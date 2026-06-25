# ==========================================================
# app.py
# GenAI RAG Assistant using Flask + ChromaDB + Claude API
# ==========================================================
 
 
# -----------------------------
# Import Flask
# -----------------------------
# Flask is used to create the web application.
from flask import Flask, render_template, request
 
 
# -----------------------------
# Import OS
# -----------------------------
# Used to access environment variables from .env
import os
 
 
# -----------------------------
# Import Requests
# -----------------------------
# Used to call the Claude REST API.
import requests
 
 
# -----------------------------
# Import dotenv
# -----------------------------
# Loads variables from .env file.
from dotenv import load_dotenv
 
 
# -----------------------------
# Import ChromaDB
# -----------------------------
# Used to search similar documents.
import chromadb
 
 
# -----------------------------
# Import Sentence Transformer
# -----------------------------
# Converts user questions into embeddings.
from sentence_transformers import SentenceTransformer



# ==========================================================
# Load environment variables
# ==========================================================
 
# Load variables from the .env file
load_dotenv()
 
 
# ==========================================================
# Read values from .env
# ==========================================================
 
# Read API key
API_KEY = os.getenv("ANTHROPIC_API_KEY")
 
# Read API endpoint
URL = os.getenv("LLM_ENDPOINT")
 
# Read model name
MODEL = os.getenv("LLM_MODEL")
 
 
# ==========================================================
# Create Flask application
# ==========================================================
 
# Create the Flask app
app = Flask(__name__)
 
 
# ==========================================================
# Load embedding model
# ==========================================================
 
# This model converts text into vector embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
 
 
# ==========================================================
# Connect to ChromaDB
# ==========================================================
 
# Connect to the existing database created earlier
client = chromadb.PersistentClient(path="chroma_db")
 
# Open the collection
collection = client.get_collection("genai_knowledge")




# Retrieve the most relevant context from ChromaDB
def retrieve_context(user_query):
 
    # Convert the user's question into an embedding
    query_embedding = model.encode(user_query).tolist()
 
    # Search the vector database for the top 3 similar documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
 
    # Return the retrieved documents
    return results




# Call the LLM API and generate the final response
def generate_response(user_query, context):
 
    # Combine retrieved context with the user's question
    prompt = f"""
Context:
{context}
 
Question:
{user_query}
 
Answer the question only using the given context.
"""
 
    # API headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
 
    # Request payload
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
 
    # Send request to Claude API
    response = requests.post(
        URL,
        headers=headers,
        json=payload
    )
 
    # Convert JSON response
    response_json = response.json()
 
    # Return assistant reply
    return response_json["choices"][0]["message"]["content"]



#create the flask route
# Home page route
@app.route("/", methods=["GET", "POST"])
def home():
 
    answer = ""
    retrieved_context = ""
 
    if request.method == "POST":
 
        # Get user's question from the HTML form
        user_query = request.form["question"]
 
        # Retrieve relevant documents
        results = retrieve_context(user_query)
 
        # Combine retrieved documents into one string
        retrieved_context = "\n".join(results["documents"][0])
 
        # Generate answer using the LLM
        answer = generate_response(user_query, retrieved_context)
 
    # Render the HTML page
    return render_template(
        "index.html",
        answer=answer,
        context=retrieved_context
    )



# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)