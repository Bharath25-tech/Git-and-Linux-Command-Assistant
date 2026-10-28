# rag.py

# --- Streamlit Cloud sqlite fix for ChromaDB (safe to keep; ignored if not installed) ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables (GROQ_API_KEY from .env when running locally)
load_dotenv()

# On Streamlit Cloud the key lives in st.secrets; copy it into the environment.
if not os.getenv("GROQ_API_KEY"):
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY not found. Add it to .env (local) or Streamlit Secrets (cloud)."
    )

# Use a path relative to this file, so it works from any working directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(BASE_DIR, "db1", "chroma_db")

if not os.path.isdir(persistent_directory):
    raise RuntimeError(
        f"Chroma database folder not found at: {persistent_directory}. "
        "Make sure db1/chroma_db is committed to your GitHub repo."
    )

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# Set up AI model
# If "openai/gpt-oss-120b" is not available on your Groq account,
# change it to "llama-3.3-70b-versatile".
model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


def rewrite_question(user_question, chat_history):
    """Make the question standalone using the conversation history."""
    if not chat_history:
        return user_question

    messages = [
        SystemMessage(
            content="Given the chat history, rewrite the new question to be standalone and searchable. Just return the rewritten question."
        ),
    ] + chat_history + [
        HumanMessage(content=f"New question: {user_question}")
    ]
    return model.invoke(messages).content.strip()


def retrieve(search_question, k=3):
    """Find the k most relevant document chunks."""
    retriever = db.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(search_question)


def stream_answer(user_question, docs, chat_history):
    """Ask the LLM using the retrieved docs, and yield the answer piece by piece."""
    formatted_docs = "\n".join([f"- {doc.page_content}" for doc in docs])

    combined_input = f"""Based on the following documents, please answer this question: {user_question}

    Documents:
    {formatted_docs}

    Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
    """

    messages = [
        SystemMessage(
            content="You are a helpful assistant that answers questions based on provided documents and conversation history."
        ),
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]

    for chunk in model.stream(messages):
        if chunk.content:
            yield chunk.content