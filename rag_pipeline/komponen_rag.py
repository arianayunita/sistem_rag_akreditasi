# File: rag_pipeline/komponen_rag.py
import os
import streamlit as st # Untuk error handling di UI jika komponen gagal load
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import config 
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config 

# @st.cache_resource # Cache resource untuk Streamlit
def get_rag_components():
    """
    REVISI: Menginisialisasi dan mengembalikan semua komponen RAG yang dibutuhkan,
    termasuk LLM utama dan LLM peringkas.
    """
    print("Memulai inisialisasi komponen RAG...")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")

    if not all([openai_api_key, pinecone_api_key, config.PINECONE_INDEX_NAME]):
        print("ERROR: API Key atau Nama Indeks Pinecone tidak ditemukan.")
        return None, None, None, None # Kembalikan empat nilai

    try:
        # PERUBAHAN: Inisialisasi dua LLM
        llm_utama = ChatOpenAI(model=config.MAIN_LLM_MODEL, temperature=0.2, openai_api_key=openai_api_key)
        llm_peringkas = ChatOpenAI(model=config.SUMMARIZER_LLM_MODEL, temperature=0, openai_api_key=openai_api_key)

        embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL, openai_api_key=openai_api_key)

        vector_store = PineconeVectorStore.from_existing_index(
            index_name=config.PINECONE_INDEX_NAME,
            embedding=embeddings,
            text_key=config.TEXT_KEY_FOR_METADATA
        )
        retriever = vector_store.as_retriever(search_kwargs={'k': 5}) # Ambil 5 chunk untuk diringkas

        print("Semua komponen RAG (LLM Utama, Peringkas, Retriever) berhasil diinisialisasi.")
        return llm_utama, llm_peringkas, embeddings, retriever

    except Exception as e:
        print(f"ERROR saat inisialisasi komponen RAG: {e}")
        # Di aplikasi Streamlit, ini akan lebih baik ditangani dengan st.error
        return None, None, None, None