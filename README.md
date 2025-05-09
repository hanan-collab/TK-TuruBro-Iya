# TK-TuruBro-Iya

## 📘 Deskripsi Sistem

Proyek ini merupakan sistem pencarian semantik berbasis pembelajaran mesin yang mampu menemukan pertanyaan serupa menggunakan embedding dan Elasticsearch. Sistem ini cocok untuk aplikasi seperti pencarian FAQ otomatis atau deteksi duplikasi pertanyaan.

Sistem terbagi menjadi dua bagian utama:

1. **Notebook `tk_tbi.ipynb`** – Melakukan *indexing* data ke Elasticsearch menggunakan embedding dari model transformer.
2. **Backend FastAPI (`backend.py`)** – Menyediakan endpoint `/search/` yang menerima teks dari pengguna, mengubahnya menjadi embedding, dan melakukan pencarian ke Elasticsearch.

## 🧱 Arsitektur Sistem

```
[ User ] --> [ FastAPI Backend ] --> [ SentenceTransformer ]
                             |
                             v
                        [ Elasticsearch ]
                             ^
                             |
            [ Indexing dari Jupyter Notebook ]
```

- Pengguna mengirimkan pertanyaan melalui endpoint.
- Backend mengubah teks menjadi embedding menggunakan `SentenceTransformer`.
- Embedding dikirim ke Elasticsearch untuk pencarian berbasis kemiripan kosinus terhadap data yang sudah di-*index* dari notebook.

## ⚙️ Teknologi yang Digunakan

- **Python 3**
- **FastAPI** – Backend web framework.
- **Elasticsearch** – Mesin pencari berbasis vektor.
- **Sentence-Transformers** – Model pre-trained `all-MiniLM-L6-v2` untuk menghasilkan embedding semantik.
- **Docker Compose** – Untuk menjalankan Elasticsearch secara lokal.
- **Jupyter Notebook** – Untuk praproses dan indexing data.

## 📂 Dataset

Dataset `quora_dataset.csv` adalah kumpulan pasangan pertanyaan dari Quora yang digunakan untuk membangun indeks vektor dalam Elasticsearch. Tiap pertanyaan akan diproses menjadi embedding dan disimpan dengan field `text` dan `embedding`.

## 🚀 Cara Instalasi dan Menjalankan Sistem

### 1. Jalankan Elasticsearch dengan Docker

```bash
docker-compose up --build
```

Elasticsearch akan tersedia di `http://localhost:9200`.

### 2. Buat dan Index Data

Buka dan jalankan `tk_tbi.ipynb` menggunakan Jupyter Notebook:

```bash
jupyter notebook
```

Notebook akan:
- Membaca dataset Quora
- Menghasilkan embedding dari pertanyaan
- Meng-*index* data ke Elasticsearch

### 3. Jalankan Backend FastAPI

Pastikan dependensi sudah terinstal:

```bash
pip install fastapi uvicorn sentence-transformers elasticsearch
```

Lalu jalankan server FastAPI:

```bash
uvicorn backend:app --reload
```

Server akan berjalan di `http://127.0.0.1:8000`.

## 🧪 Contoh Penggunaan

### Endpoint: `/search/`

**Method:** `POST`  
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
      "doc_id": "1",
      "score": 0.89,
      "text": "Apa yang dimaksud dengan machine learning?"
    },
    ...
  ]
}
```

## 📝 Catatan Tambahan

- Pastikan Elasticsearch aktif sebelum menjalankan notebook dan backend.
