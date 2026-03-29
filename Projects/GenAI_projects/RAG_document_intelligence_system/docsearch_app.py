from fastapi import FastAPI
from pydantic import BaseModel
import time

# import your pipeline
from hybrid_rag_pipeline import (
    hybrid_search,
    reranker,
    answer_with_citations,
    prepare_pipeline
)
from RAG_Graph import build_graph
app = FastAPI()

# -------- Request Schema --------
class QueryRequest(BaseModel):
    """
    Request schema for RAG query endpoint.

    Attributes:
        query (str): User input question to be answered by the RAG system.
    """
    query: str

# -------- Load pipeline once --------
print("Loading pipeline...")

all_chunks, index, bm25 = prepare_pipeline()
graph=build_graph()
print("Pipeline ready!")


# -------- Endpoint --------
@app.post("/query")
def query_rag(req: QueryRequest):
    """
    Handle user query using RAG pipeline.

    This endpoint:
    1. Accepts a user query
    2. Runs the LangGraph-based RAG pipeline:
        - Hybrid retrieval (BM25 + vector search)
        - Cross-encoder reranking
        - LLM answer generation with citations
        - Validation and retry logic
    3. Returns the final answer along with source references

    Args:
        req (QueryRequest): Request object containing user query.

    Returns:
        dict:
            answer (str): Generated answer grounded in retrieved documents.
            sources (list): List of source documents with metadata (doc_id, page).
    """
    print('APP Started')
    start = time.time()
    result=graph.invoke({
        'query' : req.query,
        'all_chunks':all_chunks,
        'index':index,
        'bm25':bm25
    }
    )
    
    latency = round(time.time() - start, 2)
    # retrieved = hybrid_search(query, bm25, index, all_chunks, top_k=10)
    # reranked = reranker(query, retrieved, top_k=5)
    # answer = answer_with_citations(query, reranked)
    return {
        "answer": result["answer"],
        "sources": [
            {
                "doc_id": c["doc_id"],
                "page": c["page"]
            }
            for c in result["reranked"]
        ]
    }
    