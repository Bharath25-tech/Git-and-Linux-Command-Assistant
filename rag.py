import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Preserve your existing database directory.
PERSISTENT_DIRECTORY = BASE_DIR / "db1" / "chroma_db"

# Your knowledge base directory.
DOCS_DIRECTORY = BASE_DIR / "docs"

# Keep this as None to use the existing/default ChromaDB
# collection associated with your configured database.
# If you originally created a named collection, set its
# exact original name here.
COLLECTION_NAME = None

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL = "openai/gpt-oss-120b"


# ============================================================
# GROQ API CONFIGURATION
# ============================================================

groq_api_key = os.getenv("GROQ_API_KEY")

try:
    if "GROQ_API_KEY" in st.secrets:
        groq_api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, RuntimeError):
    # Local execution may not have Streamlit secrets configured.
    pass

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Configure it in Streamlit Cloud "
        "Secrets or your local .env file."
    )

model = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
    api_key=groq_api_key,
)


# ============================================================
# HUGGING FACE EMBEDDINGS
# ============================================================

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


embeddings = get_embeddings()


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

def connect_database():
    """
    Connect to the existing ChromaDB database.
    Does not automatically overwrite or rebuild your database.
    """

    if not PERSISTENT_DIRECTORY.exists():
        raise FileNotFoundError(
            f"ChromaDB directory does not exist: "
            f"{PERSISTENT_DIRECTORY}"
        )

    kwargs = {
        "persist_directory": str(PERSISTENT_DIRECTORY),
        "embedding_function": embeddings,
    }

    if COLLECTION_NAME:
        kwargs["collection_name"] = COLLECTION_NAME

    vectorstore = Chroma(**kwargs)

    return vectorstore


db = connect_database()


# ============================================================
# DATABASE DIAGNOSTICS
# ============================================================

def get_database_count():
    """Return the number of entries in the connected collection."""

    return db._collection.count()


def get_database_status():
    """Return useful diagnostic information."""

    return {
        "database_directory": str(PERSISTENT_DIRECTORY),
        "database_directory_exists": PERSISTENT_DIRECTORY.exists(),
        "collection_name": db._collection.name,
        "document_count": get_database_count(),
        "docs_directory_exists": DOCS_DIRECTORY.exists(),
    }


# ============================================================
# OPTIONAL DOCUMENT LOADING
# ============================================================

def load_txt_documents():
    """
    Load TXT documents from docs/.

    This function is provided for diagnostics and rebuilding
    the knowledge base when necessary.
    """

    from langchain_community.document_loaders import (
        DirectoryLoader,
        TextLoader,
    )

    if not DOCS_DIRECTORY.exists():
        raise FileNotFoundError(
            f"TXT knowledge base not found: {DOCS_DIRECTORY}"
        )

    txt_files = list(DOCS_DIRECTORY.rglob("*.txt"))

    if not txt_files:
        raise ValueError(
            f"No TXT documents found in {DOCS_DIRECTORY}"
        )

    loader = DirectoryLoader(
        str(DOCS_DIRECTORY),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
        silent_errors=False,
    )

    documents = loader.load()

    if not documents:
        raise ValueError(
            "TXT files exist, but no document content was loaded."
        )

    return documents


def create_chunks(documents):
    """Split documents into chunks for vector search."""

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_documents(documents)


def build_database():
    """
    Build a new ChromaDB collection from TXT documents.

    IMPORTANT:
    Use this only when you intentionally want to create a new
    collection. It does not replace the existing database.
    """

    documents = load_txt_documents()
    chunks = create_chunks(documents)

    if not chunks:
        raise ValueError("No document chunks were generated.")

    new_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSISTENT_DIRECTORY),
        collection_name="git_linux_knowledge",
    )

    return new_db


# ============================================================
# REWRITE FOLLOW-UP QUESTIONS
# ============================================================

def rewrite_question(user_question, chat_history):
    """
    Convert follow-up questions into standalone search queries.
    """

    if not chat_history:
        return user_question

    messages = [
        SystemMessage(
            content=(
                "Rewrite the user's latest question as a standalone "
                "search query using the conversation history. "
                "Return only the rewritten question."
            )
        ),
        *chat_history,
        HumanMessage(
            content=f"New question: {user_question}"
        ),
    ]

    response = model.invoke(messages)

    return response.content.strip()


# ============================================================
# RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve(search_question, k=4):
    """
    Retrieve relevant document chunks from ChromaDB.
    """

    count = get_database_count()

    print("========== RAG DIAGNOSTICS ==========")
    print("Database directory:", PERSISTENT_DIRECTORY)
    print("Collection name:", db._collection.name)
    print("Collection document count:", count)
    print("Search question:", search_question)

    if count == 0:
        print("WARNING: The ChromaDB collection is empty.")

        return []

    results = db.similarity_search(
        search_question,
        k=min(k, count),
    )

    print("Retrieved document count:", len(results))

    for index, document in enumerate(results, start=1):
        print(f"Retrieved document {index}:")
        print(document.page_content[:200])
        print("Source:", document.metadata.get("source", "Unknown"))

    print("=====================================")

    return results


# ============================================================
# STREAM ANSWERS
# ============================================================

def stream_answer(user_question, docs, chat_history):
    """
    Generate a streamed response grounded in retrieved documents.
    """

    if not docs:
        yield (
            "I couldn't find any reference documents in the connected "
            "ChromaDB collection. Please check the collection count "
            "and confirm that the correct database is connected."
        )
        return

    formatted_docs = "\n\n".join(
        (
            f"[Reference {index} | Source: "
            f"{Path(str(doc.metadata.get('source', 'Unknown'))).name}]\n"
            f"{doc.page_content}"
        )
        for index, doc in enumerate(docs, start=1)
    )

    combined_input = f"""
Question:
{user_question}

Reference documents:
{formatted_docs}

Instructions:
1. Answer using the reference documents.
2. Explain Git and Linux commands clearly.
3. Include command examples when the documents support them.
4. Never invent information and claim it came from a document.
5. If the documents do not contain enough information, explain that.
"""

    messages = [
        SystemMessage(
            content=(
                "You are Git & Linux Command Assistant, a developer "
                "productivity assistant. Help users understand Git, "
                "Linux terminal commands, common errors, and developer "
                "workflows. Ground factual answers in the supplied "
                "reference documents."
            )
        ),
        *chat_history,
        HumanMessage(content=combined_input),
    ]

    for chunk in model.stream(messages):
        if not chunk.content:
            continue

        if isinstance(chunk.content, str):
            yield chunk.content

        elif isinstance(chunk.content, list):
            for block in chunk.content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")

                    if text:
                        yield text
