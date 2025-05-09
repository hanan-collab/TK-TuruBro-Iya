from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

# Inisialisasi FastAPI app
app = FastAPI()

# Inisialisasi SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Inisialisasi Elasticsearch client
es = Elasticsearch([{'scheme': 'http', 'host': 'localhost', 'port': 9200}])

# Pydantic model untuk validasi input
class SearchRequest(BaseModel):
    text: str
    index_name: str  # Nama index Elasticsearch
    page: int = 1  # Halaman yang ingin diambil, default adalah 1
    page_size: int = 10  # Jumlah hasil per halaman, default adalah 10

# Fungsi untuk menghasilkan embedding
def generate_embedding(text: str):
    # Menghasilkan embedding untuk input teks
    embedding = model.encode(text).tolist()
    return embedding

# Fungsi untuk melakukan query ke Elasticsearch dengan embedding dan pagination
def search_in_elasticsearch(query_embedding, index_name, from_: int, size: int):
    # Membuat query Elasticsearch dengan pagination
    query = {
        "from": from_,
        "size": size,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}  # Ganti dengan query yang sesuai jika perlu
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + _score",
                    "params": {
                        "query_vector": query_embedding
                    }
                }
            }
        }
    }

    # Menjalankan query ke Elasticsearch
    response = es.search(index=index_name, body=query)
    return response["hits"]["hits"], response["hits"]["total"]["value"]

# Endpoint untuk menerima teks dan mengembalikan hasil pencarian Elasticsearch dengan pagination
@app.post("/search/")
async def search(request: SearchRequest):
    text = request.text
    index_name = request.index_name
    page = request.page
    page_size = request.page_size

    # 1. Menghasilkan embedding untuk query
    query_embedding = generate_embedding(text)

    # 2. Menentukan parameter pagination
    from_ = (page - 1) * page_size  # Hitung offset berdasarkan halaman dan ukuran halaman

    # 3. Mencari di Elasticsearch menggunakan embedding dan pagination
    search_results, total_results = search_in_elasticsearch(query_embedding, index_name, from_, page_size)
    
    # 4. Mengembalikan hasil pencarian dengan informasi pagination
    results = []
    for hit in search_results:
        doc_id = hit["_source"].get("doc_id", "No doc_id")
        score = hit["_score"]
        text = hit["_source"].get("text", "No text")
        results.append({
            "doc_id": doc_id,
            "score": score,
            "text": text
        })
    
    return {
        "total_results": total_results,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_results // page_size) + (1 if total_results % page_size > 0 else 0),
        "results": results
    }
