# File: config.py

# Konfigurasi Pinecone
PINECONE_INDEX_NAME = "indeks-rag-chunk-8000" # SESUAIKAN
PINECONE_SERVERLESS_CLOUD = "aws"
TEXT_KEY_FOR_METADATA = "chunk_text_content"

# PERUBAHAN: Definisikan nama model di sini agar mudah diganti
MAIN_LLM_MODEL = "gpt-4-turbo"
SUMMARIZER_LLM_MODEL = "gpt-3.5-turbo" # Model yang lebih efisien untuk meringkas
EMBEDDING_MODEL = "text-embedding-3-small"
# PINECONE_SERVERLESS_REGION akan diambil dari environment variable

# Nama Kolom Penting di CSV Anda
KOLOM_NOMOR_USULAN = 'nomor_usulan'
KOLOM_NOMOR_ASPEK = 'nomor_aspek'
KOLOM_KETERANGAN_ASPEK_CLEANED = 'keterangan_aspek_cleaned'
KOLOM_KOMEN_AK_CLEANED = 'komen_AK_cleaned'
KOLOM_NILAI_AK = 'nilai_AK'
KOLOM_NO_ASESOR_AK = 'no_asesor_AK' 
KOLOM_TIPE_ASESOR_AK = 'tipe_asesor' 
KOLOM_KOMEN_AL_CLEANED = 'komen_AL_cleaned'
KOLOM_NILAI_AL = 'nilai_AL'
KOLOM_KODE_ASESOR_AL = 'kode_asesor_AL'

# Kunci untuk menyimpan teks asli chunk di metadata Pinecone
TEXT_KEY_FOR_METADATA = "chunk_text_content"

# Skala Nilai (jika ingin dijadikan konstanta)
SKALA_NILAI_MIN = 0
SKALA_NILAI_MAKS = 4

print("Konfigurasi dimuat.")
