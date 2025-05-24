# TK-TuruBro-Iya

## 🔗 Project Links

🖥️ **Backend Repo**: [TK-TuruBro-Iya](https://github.com/username/TK-TuruBro-Iya)  
🎨 **Frontend Repo**: [IR by Reyhan Wiyasa](https://github.com/reyhanwiyasa/IR)  
🌐 **Live App**: [http://143.198.220.249/](http://143.198.220.249/)  
📚 **Dataset Used**: [Hugging Face – Quora QA Dataset](https://huggingface.co/datasets/toughdata/quora-question-answer-dataset)  
🎬 **Demo Video**: [YouTube Demonstration](https://youtu.be/1nAETk_fJ0Y)

## 📘 Deskripsi Sistem

Proyek ini merupakan sistem pencarian semantik berbasis pembelajaran mesin yang mampu menemukan pertanyaan serupa menggunakan embedding dan Elasticsearch. Sistem ini dilengkapi dengan fitur analisis diskusi menggunakan AI untuk menentukan status resolusi dan merangkum jawaban. Cocok untuk aplikasi seperti pencarian FAQ otomatis, deteksi duplikasi pertanyaan, dan analisis komunitas support.

Sistem terbagi menjadi dua bagian utama:

1. **Notebook `tk_tbi.ipynb`** – Melakukan *indexing* data ke Elasticsearch menggunakan embedding dari model transformer.
2. **Backend FastAPI (`backend.py`)** – Menyediakan multiple endpoints untuk pencarian semantik, pencarian jawaban eksak, dan analisis diskusi menggunakan AI.

## 🧱 Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  Backend                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌─────────────┐ │
│  │ User Query  │───▶│ Tokenizer &     │───▶│ Elastic      │───▶│ API         │ │
│  │             │    │ Embedding       │    │ Search       │    │ Semantic    │ │
│  └─────────────┘    └─────────────────┘    └──────────────┘    │ Search      │ │
│                              │                      │          └─────────────┘ │
│                              ▼                      ▼                          │
│                     ┌─────────────────┐    ┌──────────────┐                   │
│                     │ all-MiniLM-L6-v2│    │ Detail       │                   │
│                     │                 │    │ Answer       │                   │
│                     └─────────────────┘    └──────────────┘                   │
│                                                     │                          │
│                              ┌─────────────────────┼─────────────────────┐    │
│                              │                     ▼                     │    │
│                              │            ┌─────────────────┐            │    │
│                              │            │ Summarize API   │            │    │
│                              │            │                 │            │    │
│                              │            └─────────────────┘            │    │
│                              │                     │                     │    │
│                              │                     ▼                     │    │
│                              │            ┌─────────────────┐            │    │
│                              │            │ Deepseek API    │            │    │
│                              │            │                 │            │    │
│                              │            └─────────────────┘            │    │
│                              └─────────────────────┬─────────────────────┘    │
│                                                    │                          │
└────────────────────────────────────────────────────┼──────────────────────────┘
                                                     ▼
                                            ┌─────────────────┐
                                            │ Output          │
                                            │                 │
                                            └─────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                Frontend                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Komponen Utama:**
- **User Query Processing**: Menerima input teks dari pengguna
- **Embedding Generation**: Menggunakan SentenceTransformer model `all-MiniLM-L6-v2` untuk menghasilkan embedding semantik
- **Elasticsearch Integration**: Melakukan pencarian berbasis kemiripan kosinus terhadap data yang sudah di-index
- **AI Analysis**: Menggunakan Deepseek API untuk menganalisis diskusi dan menentukan status resolusi
- **Multiple Search Endpoints**: Mendukung pencarian pertanyaan, pencarian jawaban eksak, dan rangkuman diskusi

## ⚙️ Teknologi yang Digunakan

- **Python 3**
- **FastAPI** – Backend web framework dengan CORS support
- **Elasticsearch** – Mesin pencari berbasis vektor dengan cosine similarity
- **Sentence-Transformers** – Model pre-trained `all-MiniLM-L6-v2` untuk embedding semantik
- **Deepseek API** – AI model untuk analisis dan rangkuman diskusi
- **OpenAI Client** – Interface untuk mengakses Deepseek API
- **Docker Compose** – Untuk menjalankan Elasticsearch secara lokal
- **Jupyter Notebook** – Untuk praproses dan indexing data

## 📂 Dataset

Dataset menggunakan [Quora Question Answer Dataset](https://huggingface.co/datasets/toughdata/quora-question-answer-dataset) dari Hugging Face yang berisi pasangan pertanyaan dan jawaban asli dari platform Quora. Dataset ini dipilih karena kualitas tinggi dan keragaman topik yang dibahas oleh komunitas Quora.

**Karakteristik Dataset:**
- **Sumber**: Hugging Face - toughdata/quora-question-answer-dataset
- **Jumlah Data**: 10,000 sampel (subset dari dataset lengkap)
- **Format**: Pasangan question-answer dalam bahasa Inggris
- **Topik**: Beragam mulai dari teknologi, sains, kehidupan sehari-hari, hingga topik spesialis
- **Kualitas**: Data sudah melalui kurasi dan filtering untuk memastikan relevansi

**Struktur Data yang Diindex:**
- **question**: Pertanyaan yang diajukan pengguna Quora
- **answer**: Jawaban berkualitas dari komunitas Quora
- **embedding**: Vector embedding 384 dimensi dari pertanyaan untuk pencarian semantik

Dataset ini ideal untuk membangun sistem pencarian FAQ karena mencerminkan pola interaksi nyata antara pengguna yang bertanya dan komunitas yang memberikan jawaban berkualitas.

## 🚀 Cara Instalasi dan Menjalankan Sistem

### 1. Jalankan Elasticsearch dengan Docker

```bash
docker-compose up --build
```

Elasticsearch akan tersedia di `http://localhost:9200` atau server remote `http://143.198.220.249:9200`.

### 2. Buat dan Index Data

Buka dan jalankan `tk_tbi.ipynb` menggunakan Jupyter Notebook:

```bash
jupyter notebook
```

Notebook akan:
- Membaca dataset Quora
- Menghasilkan embedding dari pertanyaan menggunakan SentenceTransformer
- Meng-*index* data ke Elasticsearch dengan mapping yang sesuai

### 3. Setup Environment Variables

Pastikan untuk mengonfigurasi API key untuk Deepseek:

```python
# Ganti "api-key" dengan API key yang valid
client = OpenAI(api_key="your-deepseek-api-key", base_url="https://api.deepseek.com")
```

### 4. Jalankan Backend FastAPI

Pastikan dependensi sudah terinstal:

```bash
pip install fastapi uvicorn sentence-transformers elasticsearch openai
```

Lalu jalankan server FastAPI:

```bash
uvicorn backend:app --reload
```

Server akan berjalan di `http://127.0.0.1:8000`.

## 🧪 API Endpoints dan Contoh Penggunaan

### 1. Endpoint: `/search/` - Pencarian Pertanyaan Semantik

**Method:** `POST`  
**Deskripsi:** Mencari pertanyaan serupa berdasarkan semantic similarity  
**Body:**
```json
{
  "text": "Apa itu pembelajaran mesin?",
  "index_name": "doc-index",
  "page": 1,
  "page_size": 5
}
```

**Respon:**
```json
{
  "total_results": 100,
  "page": 1,
  "page_size": 5,
  "total_pages": 20,
  "results": [
    {
      "question": "Apa yang dimaksud dengan machine learning?"
    },
    {
      "question": "Bagaimana cara kerja algoritma supervised learning?"
    }
  ]
}
```

### 2. Endpoint: `/search/answers-by-exact-question/` - Pencarian Jawaban Berdasarkan Pertanyaan

**Method:** `POST`  
**Deskripsi:** Mencari semua jawaban untuk pertanyaan yang paling mirip secara semantik  
**Body:**
```json
{
  "text": "Bagaimana cara belajar Python?",
  "index_name": "doc-index"
}
```

**Respon:**
```json
{
  "question": "Bagaimana cara belajar Python untuk pemula?",
  "total_matched_docs": 15,
  "answers": [
    "Mulai dengan tutorial dasar Python di website resmi...",
    "Saya rekomendasikan untuk praktek langsung dengan project kecil...",
    "Bergabung dengan komunitas Python Indonesia sangat membantu..."
  ]
}
```

### 3. Endpoint: `/search/summarize-discussion/` - Rangkuman dan Analisis Diskusi

**Method:** `POST`  
**Deskripsi:** Menganalisis seluruh diskusi menggunakan AI dan memberikan rangkuman, status resolusi, serta insight diskusi  
**Body:**
```json
{
  "text": "Error saat install package Python",
  "index_name": "doc-index"
}
```

**Respon:**
```json
{
  "question": "Kenapa muncul error saat pip install?",
  "total_answers": 8,
  "analysis": {
    "summary": "Diskusi ini membahas masalah instalasi package Python yang dapat diselesaikan dengan upgrade pip dan menggunakan virtual environment. Komunitas memberikan beberapa solusi dan masalah berhasil diselesaikan.",
    "is_resolved": true,
    "confidence": 0.85,
    "key_points": [
      "Upgrade pip ke versi terbaru",
      "Gunakan virtual environment",
      "Periksa compatibility package dengan Python version"
    ],
    "resolution_indicators": [
      "Thanks, it worked!",
      "Problem solved after upgrading pip"
    ],
    "discussion_flow": {
      "problem_identified": "Error during package installation using pip",
      "solutions_proposed": [
        "Upgrade pip",
        "Use virtual environment",
        "Check Python compatibility"
      ],
      "final_outcome": "Issue resolved successfully",
      "community_consensus": "Upgrade pip was the primary solution"
    }
  }
}
```

## 🔍 Fitur Utama

### 1. **Semantic Search**
- Menggunakan embedding neural untuk memahami makna pertanyaan
- Pencarian berbasis kemiripan kosinus untuk hasil yang lebih relevan
- Support pagination untuk handling dataset besar

### 2. **Exact Question Matching**
- Menggunakan keyword field untuk pencarian eksak
- Collapse feature untuk menghindari duplikasi pertanyaan
- Aggregasi semua jawaban untuk pertanyaan yang sama

### 3. **AI-Powered Discussion Analysis**
- Integrasi dengan Deepseek API untuk analisis natural language
- Deteksi otomatis status resolusi diskusi
- Rangkuman key points dan solution flow
- Analisis konsensus komunitas

### 4. **Advanced Features**
- CORS support untuk integrasi frontend
- Error handling yang robust
- Flexible indexing dengan custom mapping
- Scalable architecture untuk production

## 📊 Arsitektur Data

```
Elasticsearch Index Structure:
├── question (text + keyword mapping)
├── answer (text)
├── embedding (dense_vector, 384 dimensions)
└── metadata fields
```

## 🔧 Konfigurasi dan Customization

### Model Embedding
Sistem menggunakan `all-MiniLM-L6-v2` yang menghasilkan embedding 384 dimensi. Model ini dapat diganti dengan:

```python
model = SentenceTransformer('model-name-lain')
```

### Elasticsearch Configuration
Server Elasticsearch dapat dikonfigurasi melalui:

```python
es = Elasticsearch("http://your-elasticsearch-url:9200")
```

### AI Analysis Customization
Prompt untuk analisis diskusi dapat disesuaikan dalam fungsi `summarize_answers_with_ai()` untuk use case spesifik.

## 📝 Catatan Tambahan

- Pastikan Elasticsearch aktif sebelum menjalankan notebook dan backend
- Deepseek API key diperlukan untuk fitur analisis diskusi
- Sistem mendukung CORS untuk integrasi dengan frontend aplikasi
- Gunakan virtual environment untuk menghindari konflik dependensi
- Index mapping sudah dioptimasi untuk pencarian semantik dan keyword matching