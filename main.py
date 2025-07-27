# main.py

import os
import faiss
import numpy as np
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer

# --- 1. Configuration ---
DOCS_FILE = "docs.txt"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
CHUNK_SIZE = 300  # Approximate tokens per chunk
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAzv_xG7RBhXuGZeZKjCfKniNFxfkVSQ_Y")

# --- 2. Load Models and Configure API ---
print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print("Embedding model loaded.")

print("Configuring Gemini API...")
genai.configure(api_key=GEMINI_API_KEY)
llm = genai.GenerativeModel('gemini-1.5-flash')
print("Gemini API configured.")

# --- 3. Load and Process Document ---
def load_and_chunk_document(file_path):
    """Loads a text file and splits it into chunks."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE):
        chunks.append(" ".join(words[i:i + CHUNK_SIZE]))
    return chunks

print(f"Loading and chunking document: {DOCS_FILE}")
chunks = load_and_chunk_document(DOCS_FILE)
print(f"Document split into {len(chunks)} chunks.")

# --- 4. Embed and Index Chunks ---
print("Embedding text chunks...")
chunk_embeddings = embedding_model.encode(chunks, convert_to_tensor=False)
print("Embeddings created.")

d = chunk_embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(d)
faiss_index.add(np.array(chunk_embeddings))
print("FAISS index created and populated.")

# --- 5. RAG Core Functions ---
def retrieve_context(question, top_k=3):
    """Retrieves the top-k most relevant document chunks for a question."""
    question_embedding = embedding_model.encode([question])
    distances, indices = faiss_index.search(np.array(question_embedding), top_k)
    retrieved_chunks = [chunks[i] for i in indices[0]]
    return " ".join(retrieved_chunks)

def generate_answer(question, context):
    """Generates an answer using the Gemini API."""
    prompt = f"""
    Context: {context}
    Question: {question}
    Answer:
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating answer with Gemini: {e}")
        return "Sorry, I couldn't generate an answer."

# --- 6. Flask API ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """API endpoint to ask a question and get an answer."""
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Question not provided"}), 400

    question = data['question']
    print(f"Received question: {question}")

    context = retrieve_context(question)
    answer = generate_answer(question, context)

    print(f"Generated answer: {answer}")
    return jsonify({"question": question, "answer": answer, "context": context})

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
