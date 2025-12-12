# File: app.py
import streamlit as st
import os
import json
from dotenv import load_dotenv

# Impor dari package rag_pipeline
from rag_pipeline.komponen_rag import get_rag_components # Inisialisasi LLM, Embedding, Retriever
# Fungsi analisis_penilaian_baru_dengan_rag_historis_v2 akan menggunakan prompt
# yang sudah didefinisikan di dalam modul analisis_llm.py itu sendiri.
from rag_pipeline.analisis_llm import run_full_analysis
# Fungsi utilitas konteks sudah dipanggil di dalam analisis_llm.py

# Muat environment variables dari .env
load_dotenv()

st.set_page_config(layout="wide", page_title="Analisis Penilaian Akreditasi")
st.title("✨ Sistem Analisis & Rekomendasi Penilaian Akreditasi ✨")
st.caption("Masukkan detail penilaian baru Anda untuk mendapatkan analisis dan rekomendasi.")

# Inisialisasi komponen RAG sekali saja menggunakan cache Streamlit
# REVISI: Inisialisasi komponen baru
@st.cache_resource
def load_components():
    return get_rag_components()

llm_utama, llm_peringkas, embeddings, retriever = load_components()

# Inisialisasi state untuk menyimpan hasil jika belum ada
if 'hasil_analisis_streamlit' not in st.session_state:
    st.session_state.hasil_analisis_streamlit = None


# # Gunakan CSS untuk mengubah warna latar belakang sidebar
# # Anda bisa mengganti kode warna hex (#f0f2f6) dengan warna lain
# st.markdown("""
# <style>
#     [data-testid=st.sidebar] {
#         background-color: #A9A9A9. ;
#     }
# </style>
# """, unsafe_allow_html=True)


# --- UI untuk Input ---
with st.sidebar:
    # ... (Kode UI Sidebar Anda dari sebelumnya, tidak ada perubahan signifikan di sini) ...
    st.header("⚙️ Input Data Penilaian Baru")
    pilihan_analisis_st = st.selectbox(
        "Jenis Analisis yang Diminta:",
        ("AK_DAN_AL"), #"AK_SAJA", "AL_SAJA"
        key="pilihan_analisis"
    )
    st.markdown("---")
    nomor_usulan_st_input = st.text_input("Nomor Usulan (Baru):", key="no_usul", placeholder="Contoh: USULAN_BARU_001")
    nomor_aspek_st_input = st.text_input("Nomor Aspek (Baru):", key="no_aspek", placeholder="Contoh: C1.X.Y")
    keterangan_aspek_st_input = st.text_area("Teks Keterangan Aspek:", height=100, key="ket_aspek", placeholder="Salin atau ketik keterangan aspek di sini...")
    st.markdown("---")
    st.subheader("Asesmen Kecukupan (AK)")
    komen_ak1_st_input = st.text_area("Komentar Asesor AK 1:", height=150, key="komen_ak1")
    nilai_ak1_st_input = st.text_input("Nilai Asesor AK 1 (0-4):", key="nilai_ak1", placeholder="misal: 3 atau 2.5")
    komen_ak2_st_input = st.text_area("Komentar Asesor AK 2:", height=150, key="komen_ak2")
    nilai_ak2_st_input = st.text_input("Nilai Asesor AK 2 (0-4):", key="nilai_ak2", placeholder="misal: 3 atau 3.5")
    st.markdown("---")
    st.subheader("Asesmen Lapangan (AL)")
    komen_al_st_input = st.text_area("Komentar Asesor AL:", height=150, key="komen_al")
    nilai_al_st_input = st.text_input("Nilai Asesor AL (0-4):", key="nilai_al", placeholder="misal: 3 atau 2.75")
    analisis_button_st = st.button("🚀 Jalankan Analisis", type="primary", use_container_width=True)


# --- Logika Pemrosesan saat Tombol Ditekan ---
if analisis_button_st:
    if not all([nomor_usulan_st_input, nomor_aspek_st_input, keterangan_aspek_st_input]):
        st.warning("Mohon isi Nomor Usulan, Nomor Aspek, dan Keterangan Aspek.")
    elif llm_utama is None or retriever is None: 
        st.error("Sistem RAG belum siap atau gagal diinisialisasi. Periksa log terminal/server dan konfigurasi API Key. Coba refresh halaman.")
    else:
        data_input_baru_dari_ui = {
            "nomor_usulan_input": nomor_usulan_st_input,
            "nomor_aspek_input": nomor_aspek_st_input,
            "keterangan_aspek_input": keterangan_aspek_st_input,
            "komen_ak1_input": komen_ak1_st_input,
            "nilai_ak1_input": nilai_ak1_st_input,
            "komen_ak2_input": komen_ak2_st_input,
            "nilai_ak2_input": nilai_ak2_st_input,
            "komen_al_input": komen_al_st_input,
            "nilai_al_input": nilai_al_st_input
        }
        
        with st.spinner("Menganalisis... Ini mungkin memerlukan waktu."):
            # REVISI: Panggil fungsi analisis utama yang baru
            st.session_state.hasil_analisis_streamlit = run_full_analysis(
                data_input_baru=data_input_baru_dari_ui,
                base_retriever_obj=retriever,
                main_llm_obj=llm_utama,
                summarizer_llm_obj=llm_peringkas
            )
            st.success("Analisis selesai!")

# --- Menampilkan Hasil Analisis ---
if st.session_state.hasil_analisis_streamlit:
    hasil = st.session_state.hasil_analisis_streamlit
    st.markdown("---")
    st.header(f"📊 Hasil Analisis untuk Usulan {hasil.get('nomor_usulan_analisis')} - Aspek {hasil.get('nomor_aspek_analisis')}")
    st.caption(f"Jenis analisis yang diminta: {hasil.get('jenis_analisis_diminta')}")

    if hasil.get("error_sistem_fatal"):
        st.error(f"Terjadi Error Sistem Fatal: {hasil['error_sistem_fatal']}")
    else:
        # Menampilkan Output Mentah JSON untuk Debugging Awal
        st.subheader("Output JSON Mentah dari Sistem:")
        st.json(hasil) # Ini akan menampilkan seluruh struktur JSON

        # Menampilkan Analisis AK jika ada
        ak_result_data = hasil.get("analisis_ak_llm_baru")
        if ak_result_data and isinstance(ak_result_data, dict):
            ak_nested_data = ak_result_data.get("analisis_ak_baru") # Akses ke nested dictionary
            if isinstance(ak_nested_data, dict) and not ak_nested_data.get("error_analisis_ak"):
                with st.expander("Detail Analisis Asesmen Kecukupan (AK)", expanded=True):
                    st.info(f"**Status Utama Konsistensi:** {ak_nested_data.get('status_utama_konsistensi_ak', 'N/A')}")
                    st.markdown(f"**Sub-Kategori Status:** {ak_nested_data.get('status_sub_kategori_ak', 'N/A')}")
                    st.markdown("**Penjelasan Sistem:**")
                    st.markdown(f"> {ak_nested_data.get('penjelasan_sistem_ak', 'Tidak ada penjelasan.')}")
                    # saran_ak = ak_nested_data.get("saran_tindak_lanjut_ak_opsional", [])
                    # if saran_ak:
                    #     st.success("**Saran Tindak Lanjut AK (Opsional):**")
                    #     for saran in saran_ak: st.markdown(f"- {saran}")
                    rek_nilai_ak = ak_nested_data.get("rekomendasi_nilai_ak_sistem", {})
                    if rek_nilai_ak.get("nilai_disarankan") and rek_nilai_ak.get("nilai_disarankan") not in ["TIDAK_DIREKOMENDASIKAN_SAAT_INI", "N/A"]:
                        st.warning("**Saran Nilai AK dari Sistem:**")
                        st.markdown(f"**Nilai Disarankan:** `{rek_nilai_ak['nilai_disarankan']}`")
                        st.markdown(f"**Alasan:** {rek_nilai_ak.get('alasan_rekomendasi_nilai', 'N/A')}")
                    elif rek_nilai_ak.get("nilai_disarankan"):
                         st.warning(f"**Saran Nilai AK dari Sistem:** {rek_nilai_ak['nilai_disarankan']}")
            elif isinstance(ak_result_data, dict) and ak_result_data.get("info_analisis_ak"):
                 with st.expander("Analisis Asesmen Kecukupan (AK)", expanded=True): st.info(ak_result_data["info_analisis_ak"])
            elif isinstance(ak_result_data, dict) and ak_result_data.get("error_analisis_ak"):
                 with st.expander("Analisis Asesmen Kecukupan (AK)", expanded=True): st.error(f"Error pada analisis AK: {ak_result_data['error_analisis_ak']}")
        
        # Menampilkan Analisis AL jika ada
        al_result_data = hasil.get("analisis_al_llm_baru")
        if al_result_data and isinstance(al_result_data, dict):
            al_nested_data = al_result_data.get("analisis_al_baru") # Akses ke nested dictionary
            if isinstance(al_nested_data, dict) and not al_nested_data.get("error_analisis_al"):
                with st.expander("Detail Analisis Asesmen Lapangan (AL)", expanded=True):
                    st.info(f"**Status Relevansi Komentar AL:** {al_nested_data.get('status_relevansi_komentar_al', 'N/A')}")
                    st.markdown("**Penjelasan Sistem:**")
                    st.markdown(f"> {al_nested_data.get('penjelasan_sistem_al', 'Tidak ada penjelasan.')}")
                    st.markdown(f"**Analisis terhadap Nilai AL Asli:** {al_nested_data.get('analisis_terhadap_nilai_al_asli', 'N/A')}")
                    # saran_al = al_nested_data.get("saran_tindak_lanjut_al_opsional", [])
                    # if saran_al:
                    #     st.success("**Saran Tindak Lanjut AL (Opsional):**")
                    #     for saran in saran_al: st.markdown(f"- {saran}")
                    rek_nilai_al = al_nested_data.get("rekomendasi_nilai_al_sistem", {})
                    if rek_nilai_al.get("nilai_disarankan") and rek_nilai_al.get("nilai_disarankan") not in ["TIDAK_DIREKOMENDASIKAN_SAAT_INI", "N/A"]:
                        st.warning("**Saran Nilai AL dari Sistem:**")
                        st.markdown(f"**Nilai Disarankan:** `{rek_nilai_al['nilai_disarankan']}`")
                        st.markdown(f"**Alasan:** {rek_nilai_al.get('alasan_rekomendasi_nilai', 'N/A')}")
                    elif rek_nilai_al.get("nilai_disarankan"):
                         st.warning(f"**Saran Nilai AL dari Sistem:** {rek_nilai_al['nilai_disarankan']}")
            elif isinstance(al_result_data, dict) and al_result_data.get("info_analisis_al"):
                 with st.expander("Analisis Asesmen Lapangan (AL)", expanded=True): st.info(al_result_data["info_analisis_al"])
            elif isinstance(al_result_data, dict) and al_result_data.get("error_analisis_al"):
                 with st.expander("Analisis Asesmen Lapangan (AL)", expanded=True): st.error(f"Error pada analisis AL: {al_result_data['error_analisis_al']}")

    if st.button("Bersihkan Hasil"):
        st.session_state.hasil_analisis_streamlit = None
        st.rerun()
