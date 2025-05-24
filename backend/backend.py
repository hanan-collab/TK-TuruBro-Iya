from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from collections import defaultdict
from openai import OpenAI
import json

app = FastAPI()
client = OpenAI(api_key="api-key", base_url="https://api.deepseek.com")

origins = ["*"]  # Ganti dengan domain frontend jika perlu
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('all-MiniLM-L6-v2')

es = Elasticsearch("http://143.198.220.249:9200")

class SearchRequest(BaseModel):
    text: str
    index_name: str
    page: int = 1
    page_size: int = 10

def generate_embedding(text: str):
    embedding = model.encode(text).tolist()
    return embedding

def search_in_elasticsearch(query_embedding, index_name, from_, size):
    query = {
        "from": from_,
        "size": size,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": query_embedding
                    }
                }
            }
        },
        "collapse": {
            "field": "question.keyword"  # Ambil hanya 1 dokumen per question
        }
    }

    response = es.search(index=index_name, body=query)
    return response["hits"]["hits"], response["hits"]["total"]["value"]

def summarize_answers_with_ai(question: str, answers: list):
    """
    Menggunakan AI untuk merangkum jawaban dan menentukan status resolved
    """
    if not answers:
        return {
            "summary": "Tidak ada jawaban yang tersedia",
            "is_resolved": False,
            "confidence": 0.0,
            "key_points": [],
            "resolution_indicators": []
        }
    
    # Gabungkan semua jawaban
    combined_answers = "\n\n".join([f"Answer {i+1}: {answer}" for i, answer in enumerate(answers)])
    
    prompt = f"""
Analyze this COMPLETE DISCUSSION THREAD as a whole. The question below was asked, and multiple people provided various answers over time. Please provide an OVERALL CONCLUSION of the entire discussion:

ORIGINAL QUESTION: {question}

COMPLETE DISCUSSION (all answers in chronological order):
{combined_answers}

Analyze this as ONE COMPLETE CONVERSATION and provide a JSON response with:

{{
    "summary": "Overall conclusion of what happened in this discussion - what was the main problem, what solutions were tried/suggested, and what was the final outcome",
    "is_resolved": true/false,
    "confidence": 0.0-1.0,
    "key_points": ["main takeaways from the entire discussion"],
    "resolution_indicators": ["phrases that show the discussion reached a conclusion"],
    "discussion_flow": {{
        "problem_identified": "What was the core issue discussed",
        "solutions_proposed": ["What solutions were suggested by the community"],
        "final_outcome": "What was the end result of this discussion",
        "community_consensus": "Did the community agree on a solution?"
    }}
}}

IMPORTANT: 
- Treat this as ONE CONTINUOUS DISCUSSION, not separate individual answers
- Focus on the FLOW and PROGRESSION of the conversation
- Look for the FINAL RESOLUTION or outcome of the entire thread
- Determine if the original question was ultimately answered/solved
- Consider the discussion as RESOLVED if there's clear indication the problem was solved or the question was satisfactorily answered

Resolution indicators include:
- Explicit thanks/confirmation from questioner
- "That worked", "Problem solved", "Thanks, fixed it"
- Clear consensus reached by the community
- No further questions or issues raised after solution
- Solution marked as accepted/correct
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing technical discussions and determining if issues have been resolved. Always respond with valid JSON only, without any markdown formatting or code blocks."},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            temperature=0.1
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Clean up the response - remove markdown code blocks if present
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]  # Remove ```json
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]  # Remove ```
        ai_response = ai_response.strip()
        
        # Parse JSON response
        try:
            result = json.loads(ai_response)
            return result
        except json.JSONDecodeError:
            # Fallback jika JSON parsing gagal
            return {
                "summary": ai_response,
                "is_resolved": False,
                "confidence": 0.0,
                "key_points": [],
                "resolution_indicators": [],
                "discussion_flow": {
                    "problem_identified": "Unable to parse AI response",
                    "solutions_proposed": [],
                    "final_outcome": "Analysis failed",
                    "community_consensus": "Unknown"
                }
            }
            
    except Exception as e:
        return {
            "summary": f"Error in AI analysis: {str(e)}",
            "is_resolved": False,
            "confidence": 0.0,
            "key_points": [],
            "resolution_indicators": [],
            "answer_categories": {
                "solutions": [],
                "explanations": [],
                "follow_ups": [],
                "confirmations": []
            }
        }

@app.post("/search/")
async def search(request: SearchRequest):
    text = request.text
    index_name = request.index_name
    page = request.page
    page_size = request.page_size

    query_embedding = generate_embedding(text)
    from_ = (page - 1) * page_size

    search_results, total_results = search_in_elasticsearch(query_embedding, index_name, from_, page_size)

    # Return hanya unique questions (dijamin oleh collapse)
    questions = [{"question": hit["_source"].get("question", "No question")} for hit in search_results]

    return {
        "total_results": total_results,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_results // page_size) + (1 if total_results % page_size > 0 else 0),
        "results": questions
    }

@app.post("/search/answers-by-exact-question/")
async def search_answers_by_exact_question(request: SearchRequest):
    text = request.text
    index_name = request.index_name

    query_embedding = generate_embedding(text)

    # Cari dokumen embedding paling mirip
    query = {
        "size": 1,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }
    response = es.search(index=index_name, body=query)
    hits = response["hits"]["hits"]
    if not hits:
        return {"message": "No matching document found."}

    best_question = hits[0]["_source"].get("question")
    if not best_question:
        return {"message": "Best matching document has no question."}

    # Cari semua dokumen dengan exact match menggunakan keyword field
    exact_match_query = {
        "size": 100,
        "query": {
            "term": {
                "question.keyword": best_question
            }
        }
    }
    exact_response = es.search(index=index_name, body=exact_match_query)
    exact_hits = exact_response["hits"]["hits"]

    # Ambil semua answer
    answers = [hit["_source"].get("answer", "").strip() for hit in exact_hits if hit["_source"].get("answer")]

    return {
        "question": best_question,
        "total_matched_docs": len(exact_hits),
        "answers": answers
    }

# Endpoint khusus untuk hanya mendapatkan rangkuman tanpa semua jawaban
@app.post("/search/summarize-discussion/")
async def summarize_discussion(request: SearchRequest):
    """
    Endpoint khusus untuk mendapatkan rangkuman diskusi tanpa mengembalikan semua jawaban
    Berguna untuk UI yang hanya ingin menampilkan summary
    """
    text = request.text
    index_name = request.index_name

    query_embedding = generate_embedding(text)

    # Cari dokumen embedding paling mirip
    query = {
        "size": 1,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }
    response = es.search(index=index_name, body=query)
    hits = response["hits"]["hits"]
    if not hits:
        return {"message": "No matching document found."}

    best_question = hits[0]["_source"].get("question")
    if not best_question:
        return {"message": "Best matching document has no question."}

    # Cari semua dokumen dengan exact match
    exact_match_query = {
        "size": 100,
        "query": {
            "term": {
                "question.keyword": best_question
            }
        }
    }
    exact_response = es.search(index=index_name, body=exact_match_query)
    exact_hits = exact_response["hits"]["hits"]

    # Ambil semua answer
    answers = [hit["_source"].get("answer", "").strip() for hit in exact_hits if hit["_source"].get("answer")]
    
    # Generate AI summary and analysis
    ai_analysis = summarize_answers_with_ai(best_question, answers)

    return {
        "question": best_question,
        "total_answers": len(answers),
        "analysis": ai_analysis
    }