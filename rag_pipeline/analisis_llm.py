# File: rag_pipeline/analisis_llm.py
import json
# rag_pipeline/analisis_llm.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
# CORRECTED IMPORT STATEMENT
# The dot (.) tells Python to import from the same package (rag_pipeline).
from .utilitas_konteks import format_new_assessment_data_to_context_string, summarize_historical_context

# ... other imports ...
try:
    from .utilitas_konteks import format_new_assessment_data_to_context_string, summarize_historical_context
except ImportError:
    # INCORRECT LINE BELOW
    from utilitas_konteks import format_new_assessment_data_to_context_string, summarize_historical_context 

PROMPT_AK_ANALYSIS_V4_SIMPLIFIED_TEMPLATE = """
Anda adalah seorang meta-analis akreditasi yang sangat teliti, objektif, dan ahli.
Tugas Anda adalah menganalisis DATA PENILAIAN AK BARU, dengan mempertimbangkan CONTOH DATA HISTORIS RELEVAN (jika ada) sebagai pembanding.

Berikut adalah data yang perlu Anda analisis:
{konteks_gabungan_ak} 
// 'konteks_gabungan_ak' berisi DATA PENILAIAN BARU dan KONTEKS HISTORIS

Lakukan analisis dengan langkah-langkah berikut (Chain-of-Thought yang detail):
1.  **Pahami Keterangan Aspek Utama (dari DATA BARU).**
2.  **Evaluasi Penilaian Asesor AK Pertama (dari DATA BARU):** Analisis keselarasan komentarnya dengan Keterangan Aspek baru, kualitas justifikasi, dan konsistensi komentar dengan nilai (skala 0-4).
3.  **Evaluasi Penilaian Asesor AK Kedua (dari DATA BARU, jika ada):** Lakukan hal yang sama.
4.  **Analisis Perbandingan Internal DATA BARU Antar Asesor (jika ada dua asesor):** Bandingkan kemiripan substansi komentar dan perbedaan nilai.
5.  **Tentukan Status Utama Konsistensi untuk DATA BARU:** ("KONSISTEN" atau "TIDAK_KONSISTEN").
6.  **Tentukan Status Sub-Kategori untuk DATA BARU berdasarkan definisi berikut:**
     - Jika Status Utama "KONSISTEN":
        - Pilih "Komentar dan Nilai Sama": JIKA komentar kedua asesor berkualitas baik, memiliki substansi yang sangat mirip atau mendukung satu sama lain, DAN nilai yang diberikan sama persis serta nilai tersebut didukung dengan baik oleh kedua komentar.
    - Jika Status Utama "TIDAK_KONSISTEN":
        - Pilih "Komentar Sama dan Nilai Berbeda": JIKA substansi utama atau sebagian besar isi komentar kedua asesor dinilai sangat mirip atau hampir identik, NAMUN nilai AK yang diberikan oleh keduanya berbeda secara signifikan (misal, selisih >= 0.25 atau > 1.0 pada skala 0-4).
        - Pilih "Komentar dan Nilai Berbeda": JIKA baik substansi komentar (fokus, observasi, kesimpulan) maupun nilai dari kedua asesor menunjukkan perbedaan yang signifikan dan mendasar.
        - Pilih "Komentar Berbeda dan Nilai Sama": JIKA nilai yang diberikan kedua asesor sama atau sangat mirip, NAMUN substansi komentar atau justifikasi yang diberikan sangat berbeda, bahkan mungkin bertentangan, atau salah satu/keduanya dinilai tidak cukup mendukung skor yang sama tersebut.
7.  **Analisis Komparatif dengan Data Historis (jika ada dan relevan):** Bagaimana DATA BARU ini dibandingkan dengan pola di data historis terkait status dan sub-kategori yang Anda tentukan?
8.  **Rumuskan Penjelasan dari Sistem:** Jelaskan secara detail alasan mengapa Anda memilih status utama dan sub-kategori tersebut, integrasikan temuan dari evaluasi internal, perbandingan internal, dan perbandingan historis (jika ada).
9. **Berikan Rekomendasi Nilai AK (jika memungkinkan dan ada dasar kuat):** Fokus pada skor konsensus atau penyesuaian untuk DATA BARU (skala 1-4), dengan justifikasi.

Setelah melakukan analisis langkah demi langkah, berikan output Anda HANYA dalam format JSON yang valid dan lengkap untuk DATA PENILAIAN BARU:
```json
{{
  "analisis_ak_baru": {{
    "nomor_usulan_analisis": "NOMOR_USULAN_BARU_DARI_INPUT",
    "nomor_aspek_analisis": "NOMOR_ASPEK_BARU_DARI_INPUT",
    "data_asesor_1_input": {{
      "komentar_asli": "KOMENTAR_ASESOR_1_BARU",
      "nilai_asli": "NILAI_ASESOR_1_BARU (0-4)"
    }},
    "data_asesor_2_input": {{
      "komentar_asli": "KOMENTAR_ASESOR_2_BARU (atau '[Tidak ada data]')",
      "nilai_asli": "NILAI_ASESOR_2_BARU (0-4 atau 'N/A')"
    }},
    "status_utama_konsistensi_ak": "KONSISTEN / TIDAK_KONSISTEN",
    "status_sub_kategori_ak": "SESUAI_PILIHAN_LANGKAH_6_DI_ATAS (misal: 'Komentar Sama, Nilai Berbeda')",
    "penjelasan_sistem_ak": "Penjelasan detail dari CoT poin 8, mencakup analisis internal, perbandingan internal, dan perbandingan historis jika ada.",
    "rekomendasi_nilai_ak_sistem": {{
      "nilai_disarankan": "SKOR_ATAU_RENTANG_AK_BARU (1-4) / TIDAK_DIREKOMENDASIKAN_SAAT_INI",
      "alasan_rekomendasi_nilai": "Alasan mengapa skor ini direkomendasikan atau mengapa tidak bisa direkomendasikan saat ini."
    }}
  }}
}}
"""
prompt_ak_v4 = ChatPromptTemplate.from_template(PROMPT_AK_ANALYSIS_V4_SIMPLIFIED_TEMPLATE)
print("Template prompt V4 Sederhana untuk Analisis AK telah didefinisikan.")

PROMPT_AL_ANALYSIS_V4_SIMPLIFIED_TEMPLATE = """
Anda adalah seorang analis akreditasi yang sangat teliti, objektif, dan ahli.
Tugas Anda adalah menganalisis DATA PENILAIAN AL BARU, dengan mempertimbangkan CONTOH DATA HISTORIS RELEVAN (jika ada) sebagai pembanding.

Berikut adalah data yang perlu Anda analisis:
{konteks_gabungan_al} 
// 'konteks_gabungan_al' berisi DATA PENILAIAN BARU (termasuk 'Keterangan Aspek Utama (Input Baru)' dan 'Asesmen Lapangan (AL) (Input Baru)') 
// dan KONTEKS HISTORIS. Fokuskan analisis AL pada 'Keterangan Aspek Utama (Input Baru)' sebagai standar yang harus dipenuhi 
// oleh 'Komentar' dan 'Nilai' dari 'Asesmen Lapangan (AL) (Input Baru)'.

Lakukan analisis dengan langkah-langkah berikut (Chain-of-Thought yang detail):

1.  **Identifikasi Poin-Poin Kunci dari Standar:** Baca dengan saksama 'Keterangan Aspek Utama (Input Baru)' (selanjutnya disebut Keterangan Aspek). Identifikasi dan simpulkan poin-poin kunci atau kriteria esensial (misalnya, N poin) yang harus dijawab, didemonstrasikan, atau dijelaskan dalam komentar AL.
2.  **Evaluasi Komentar AL Terhadap Setiap Poin Kunci:** Untuk 'Komentar' dari 'Asesmen Lapangan (AL) (Input Baru)' (selanjutnya disebut Komentar AL):
    a.  Untuk setiap poin kunci yang telah Anda identifikasi dari Keterangan Aspek, tentukan apakah Komentar AL telah membahas/menjawab/merefleksikan poin kunci tersebut.
    b.  Untuk poin kunci yang dibahas, nilai kualitas pembahasannya: Apakah spesifik? Apakah mendalam? Apakah didukung oleh observasi/bukti konkret dari lapangan (jika sifatnya memungkinkan)?
    c.  Hitung berapa banyak dari N poin kunci yang telah dibahas dengan kualitas baik oleh Komentar AL.
3.  **Tentukan Status Relevansi Komentar AL:** Berdasarkan evaluasi pada langkah 2, pilih SATU Status Relevansi Komentar AL yang paling tepat dari kategori berikut:
    * `SANGAT_RELEVAN`: Komentar AL membahas secara memadai dan berkualitas baik sebagian besar atau semua poin kunci (misalnya, >75% hingga 100% poin kunci) dari Keterangan Aspek. Pembahasan untuk setiap poin kunci detail, spesifik, dan didukung bukti.
    * `CUKUP_RELEVAN`: Komentar AL membahas secara memadai sejumlah poin kunci yang signifikan namun tidak semuanya (misalnya, 50% - 75% poin kunci). Beberapa poin dibahas baik, lainnya mungkin kurang detail atau hanya disentuh permukaannya.
    * `KURANG_RELEVAN`: Komentar AL hanya membahas secara memadai sebagian kecil poin kunci (misalnya, 25% - <50% poin kunci). Sebagian besar poin kunci tidak terjawab atau tidak dibahas dengan cukup. Komentar mungkin terlalu umum.
    * `TIDAK_RELEVAN`: Komentar AL hampir tidak membahas sama sekali atau sama sekali tidak membahas poin-poin kunci (<25% poin kunci), atau isinya menyimpang jauh dari Keterangan Aspek.
4.  **Analisis Komparatif dengan Data Historis (jika ada dan relevan):** Bagaimana DATA PENILAIAN AL BARU ini (terutama status relevansi yang Anda tentukan) dibandingkan dengan pola di data historis yang relevan? Apakah ada kesamaan atau perbedaan yang signifikan? Nyatakan jika tidak ada data historis yang relevan untuk perbandingan.
5.  **Rumuskan Penjelasan dari Sistem:** Jelaskan secara detail alasan mengapa Anda memilih status relevansi tersebut. Rujuk pada poin-poin kunci dari Keterangan Aspek dan bagaimana Komentar AL membahas (atau gagal membahas) poin-poin tersebut. Integrasikan juga temuan dari perbandingan historis (jika ada dan signifikan).
6.  **Analisis terhadap Nilai AL yang Diberikan:** Berdasarkan 'Nilai' dari 'Asesmen Lapangan (AL) (Input Baru)' (skala 1-4): Apakah nilai tersebut konsisten dengan Komentar AL dan Status Relevansi yang telah Anda tentukan? Jelaskan.
7.  **Berikan Rekomendasi Nilai AL (jika memungkinkan dan ada dasar kuat):** Berdasarkan keseluruhan analisis Anda (terutama kualitas pemenuhan poin kunci oleh Komentar AL dan konsistensinya dengan nilai asli), berikan rekomendasi skor untuk Asesmen Lapangan (AL) BARU (skala 0-4), dengan justifikasi yang jelas. Jika tidak yakin, nyatakan "TIDAK_DIREKOMENDASIKAN_SAAT_INI".

Setelah melakukan analisis, berikan output Anda HANYA dalam format JSON yang valid dan lengkap untuk DATA PENILAIAN AL BARU:
```json
{{
  "analisis_al_baru": {{
    "nomor_usulan_analisis": "Isi dengan nomor usulan dari konteks data baru",
    "nomor_aspek_analisis": "Isi dengan nomor aspek dari konteks data baru",
    "komentar_al_asli": "Isi dengan Komentar dari 'Asesmen Lapangan (AL) (Input Baru)'",
    "nilai_al_asli": "Isi dengan Nilai dari 'Asesmen Lapangan (AL) (Input Baru)'",
    "status_relevansi_komentar_al": "PILIH_SALAH_SATU_DARI_4_KATEGORI_BARU (misal: RELEVAN_CUKUP)",
    "penjelasan_sistem_al": "Penjelasan detail dari CoT poin 5, merujuk pada pemenuhan poin kunci dan perbandingan historis jika ada.",
    "analisis_terhadap_nilai_al_asli": "Analisis Anda berdasarkan CoT poin 6.",
    "rekomendasi_nilai_al_sistem": {{
      "nilai_disarankan": "SKOR_AL_BARU (1-4) / TIDAK_DIREKOMENDASIKAN_SAAT_INI",
      "alasan_rekomendasi_nilai": "Alasan mengapa skor ini direkomendasikan atau mengapa tidak bisa direkomendasikan saat ini, kaitkan dengan pemenuhan poin kunci."
    }}
  }}
}}
"""
prompt_al_v4 = ChatPromptTemplate.from_template(PROMPT_AL_ANALYSIS_V4_SIMPLIFIED_TEMPLATE)
print("Template prompt V4 Sederhana untuk Analisis AL telah didefinisikan.")

# --- REVISI: Fungsi Analisis Utama ---
def run_full_analysis(
    data_input_baru: dict,
    base_retriever_obj,
    main_llm_obj,
    summarizer_llm_obj
):
    """Fungsi analisis RAG yang menerapkan alur Retrieve-Summarize-Generate."""

    # 1. Format Data Baru
    konteks_data_baru_str, nu_out, na_out = format_new_assessment_data_to_context_string(data_input_baru)

    # 2. Retrieve: Ambil chunk historis
    query_utama = (f"Analisis untuk aspek: {data_input_baru.get('keterangan_aspek_input', '')}. "
                   f"Komentar: {data_input_baru.get('komen_ak1_input', '')} ...")

    retrieved_chunks = base_retriever_obj.invoke(query_utama)
    unique_chunks = list({doc.page_content: doc for doc in retrieved_chunks}.values())

    # 3. Summarize: Meringkas chunk historis
    konteks_historis_str = summarize_historical_context(unique_chunks, summarizer_llm_obj, query_utama)

    # 4. Generate: Gabungkan dan kirim ke LLM utama
    konteks_final = (
        f"DATA_PENILAIAN_BARU_YANG_DIANALISIS:\n{konteks_data_baru_str}\n\n"
        f"<RINGKASAN_KONTEKS_HISTORIS_SEBAGAI_PEMBANDING>:\n{konteks_historis_str}"
    )

    hasil_json = {"nomor_usulan_analisis": nu_out, "nomor_aspek_analisis": na_out}
    json_parser = JsonOutputParser()
    ak_prompt = ChatPromptTemplate.from_template(PROMPT_AK_ANALYSIS_V4_SIMPLIFIED_TEMPLATE)
    al_prompt = ChatPromptTemplate.from_template(PROMPT_AL_ANALYSIS_V4_SIMPLIFIED_TEMPLATE)

    # Analisis AK dan AL
    chain_ak = ak_prompt | main_llm_obj | json_parser
    try: hasil_json["analisis_ak_llm_baru"] = chain_ak.invoke({"konteks_gabungan_ak": konteks_final})
    except Exception as e: hasil_json["analisis_ak_llm_baru"] = {"error": f"Gagal analisis AK: {e}"}

    chain_al = al_prompt | main_llm_obj | json_parser
    try: hasil_json["analisis_al_llm_baru"] = chain_al.invoke({"konteks_gabungan_al": konteks_final})
    except Exception as e: hasil_json["analisis_al_llm_baru"] = {"error": f"Gagal analisis AL: {e}"}

    return hasil_json