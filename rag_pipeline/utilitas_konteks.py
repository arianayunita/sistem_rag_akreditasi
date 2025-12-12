# File: rag_pipeline/utilitas_konteks.py
import pandas as pd
import json
# Impor konstanta kolom dari config.py jika dibutuhkan
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config # akses config.KOLOM_NOMOR_USULAN, dll.
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def format_new_assessment_data_to_context_string(new_data: dict) -> tuple[str, str, str]:
    # === SALIN FUNGSI LENGKAP DARI LANGKAH 12 (REVISI TOTAL) ANDA KE SINI ===
    # Contoh singkat:
    nomor_usulan_baru = new_data.get('nomor_usulan_input', "N/A_USULAN_BARU")
    nomor_aspek_baru = new_data.get('nomor_aspek_input', "N/A_ASPEK_BARU")
    keterangan_aspek_input = new_data.get('keterangan_aspek_input', '[Keterangan Aspek Tidak Diinput]')
    
    parts = [f"Analisis untuk Usulan (BARU): {nomor_usulan_baru}", f"Aspek: {nomor_aspek_baru}"]
    parts.append(f"\n\nKeterangan Aspek Utama (Input Baru):\n{keterangan_aspek_input}")
    
    # Bagian AK
    parts.append(f"\n\n--- Asesmen Kecukupan (AK) (Input Baru) ---")
    komen_ak1 = new_data.get('komen_ak1_input', '')
    nilai_ak1 = str(new_data.get('nilai_ak1_input', '')).strip()
    if komen_ak1.strip() or nilai_ak1:
        parts.append(f"\nAsesor AK Tipe 1 (Baru):")
        parts.append(f"  Komentar:\n    {komen_ak1 if komen_ak1.strip() else '[Tidak diinput]'}")
        parts.append(f"  Nilai: {nilai_ak1 if nilai_ak1 else 'N/A'}")
    else:
        parts.append(f"\nAsesor AK Tipe 1 (Baru):\n  Komentar:\n    [Data tidak diinput]\n  Nilai: N/A")
    # Lakukan hal yang sama untuk Asesor AK 2
    komen_ak2 = new_data.get('komen_ak2_input', '')
    nilai_ak2 = str(new_data.get('nilai_ak2_input', '')).strip()
    if komen_ak2.strip() or nilai_ak2:
        parts.append(f"\nAsesor AK Tipe 2 (Baru):")
        parts.append(f"  Komentar:\n    {komen_ak2 if komen_ak2.strip() else '[Tidak diinput]'}")
        parts.append(f"  Nilai: {nilai_ak2 if nilai_ak2 else 'N/A'}")
    else:
        parts.append(f"\nAsesor AK Tipe 2 (Baru):\n  Komentar:\n    [Data tidak diinput]\n  Nilai: N/A")
        
    # Bagian AL
    parts.append(f"\n\n--- Asesmen Lapangan (AL) (Input Baru) ---")
    komen_al = new_data.get('komen_al_input', '')
    nilai_al = str(new_data.get('nilai_al_input', '')).strip()
    if komen_al.strip() or nilai_al:
        parts.append(f"Komentar:\n    {komen_al if komen_al.strip() else '[Tidak diinput]'}")
        parts.append(f"Nilai: {nilai_al if nilai_al else 'N/A'}")
    else:
        parts.append(f"Komentar dan Nilai AL tidak diinput untuk analisis ini.")
        
    return "\n".join(parts), nomor_usulan_baru, nomor_aspek_baru


def format_retrieved_historical_docs(retrieved_docs: list) -> str:
    # === SALIN FUNGSI LENGKAP DARI LANGKAH 12 (REVISI TOTAL) ANDA KE SINI ===
    # Contoh singkat:
    if not retrieved_docs: return "[Tidak ada data historis relevan yang ditemukan sebagai pembanding.]"
    parts = []
    for i, doc in enumerate(retrieved_docs):
        content = doc.page_content
        if content and isinstance(content, str) and content.strip():
            # Menggunakan konstanta dari config untuk metadata
            hist_nu = doc.metadata.get(config.KOLOM_NOMOR_USULAN, "N/A")
            hist_na = doc.metadata.get(config.KOLOM_NOMOR_ASPEK, "N/A")
            parts.append(f"--- Contoh Historis {i+1} (Usulan Hist: {hist_nu}, Aspek Hist: {hist_na}) ---\n{content}")
    if not parts: return "[Tidak ada konten valid dari data historis.]"
    return "\n\n<PEMISAH_CONTOH_HISTORIS>\n\n".join(parts)


def summarize_historical_context(retrieved_docs: list, summarizer_llm, query_text: str) -> str:
    """Meringkas list chunk historis menjadi satu paragraf padat."""
    if not retrieved_docs:
        return "Tidak ada konteks historis yang relevan ditemukan."

    combined_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

    summarization_prompt_template = """Berdasarkan potongan-potongan informasi dari berbagai kasus penilaian historis berikut, buatlah satu paragraf ringkasan yang padat. Fokuskan ringkasan pada poin-poin kunci, temuan signifikan, dan pola masalah yang paling relevan dengan topik berikut: "{query_text}"

Informasi Historis untuk Diringkas:
{historical_text}

Ringkasan Padat:"""
    summarization_prompt = ChatPromptTemplate.from_template(summarization_prompt_template)
    summarization_chain = summarization_prompt | summarizer_llm | StrOutputParser()

    try:
        summary = summarization_chain.invoke({"historical_text": combined_text, "query_text": query_text})
        return summary
    except Exception as e:
        return f"[Gagal meringkas konteks: {e}]"