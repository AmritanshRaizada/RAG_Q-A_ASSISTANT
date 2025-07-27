# Simple RAG Q&A Chatbot

This project is a simple Retrieval-Augmented Generation (RAG) Q&A chatbot that runs locally. It uses a local text file as its knowledge base, embeds the text using SentenceTransformers, stores it in a FAISS index, and uses the Gemini API to generate answers.

## Features

- **Local Knowledge Base**: Uses a `docs.txt` file for context.
- **Sentence Embeddings**: `all-MiniLM-L6-v2` for creating text embeddings.
- **Vector Store**: FAISS for efficient similarity search.
- **Gemini API**: Uses the Gemini API for answer generation.
- **Simple API**: A Flask server with an `/ask` endpoint.

## Setup

1.  **Clone the repository** (or download the files).

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    You may also need to set your Gemini API key as an environment variable:
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```

## Usage

1.  **Run the Flask server**:
    ```bash
    python main.py
    ```
    The server will start, and you will see messages indicating that the models are loading and the FAISS index is being created. The server runs on `http://localhost:5001`.

2.  **Ask a question**:
    You can send a POST request to the `/ask` endpoint using a tool like `curl` or a simple Python script.

    **Example using `curl`**:
    ```bash
    curl -X POST http://localhost:5001/ask \
         -H "Content-Type: application/json" \
         -d '{"question": "What was the first artificial satellite?"}'
    ```

    **Expected Response**:
    ```json
    {
      "answer": "Sputnik 1",
      "context": "The history of space exploration is a testament to human curiosity and ingenuity. It began in the mid-20th century with the launch of the first artificial satellite, Sputnik 1, by the Soviet Union in 1957. This event marked the beginning of the Space Race, a period of intense competition between the United States and the Soviet Union. Key milestones include the first human in space, Yuri Gagarin, in 1961, and the first human on the Moon, Neil Armstrong, in 1969.",
      "question": "What was the first artificial satellite?"
    }
    ```

## How It Works

1.  **Load and Chunk**: The `docs.txt` file is loaded and split into smaller chunks.
2.  **Embed and Index**: Each chunk is converted into a numerical vector (embedding) and stored in a FAISS index for fast retrieval.
3.  **Retrieve**: When a question is asked, it is also embedded, and FAISS is used to find the most similar document chunks (the context).
4.  **Generate**: The retrieved context and the original question are passed to the Gemini API, which generates a final answer.
