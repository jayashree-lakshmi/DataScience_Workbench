from typing import TypedDict,List,Dict
from hybrid_rag_pipeline import (
    hybrid_search,
    llm,
    reranker,
    answer_with_citations,
    prepare_pipeline
)
from evaluation import (
    normalize,
    compute_similarity,
    clean_answer
)
from langgraph.graph import StateGraph


class RAGState(TypedDict):
    """
    Shared state object passed between LangGraph nodes.

    This acts as the central memory for the RAG pipeline and stores:
    - Input query
    - Retrieval resources (chunks, indexes)
    - Intermediate results (retrieved, reranked)
    - Final answer
    - Control signals for retry logic

    Attributes:
        query (str): User input query.
        all_chunks (List[Dict]): All document chunks with metadata.
        index (object): FAISS vector index.
        bm25 (object): BM25 keyword index.
        retrieved (List[Dict]): Retrieved chunks from hybrid search.
        reranked (List[Dict]): Top-ranked chunks after cross-encoder reranking.
        answer (str): Final generated answer with citations.
        needs_retry (bool): Flag indicating whether pipeline should retry.
        retry_count (int): Number of retry attempts performed.
    """
    query:str
    all_chunks:List[Dict]
    index: object
    bm25: object

    retrieved: List[Dict]
    reranked: List[Dict]

    answer: str

    # evaluation signals (optional for later)
    needs_retry: bool
    retry_count: int 

#Node1:Prepare pipeline
def prepare_node(state:RAGState):
    """
    Initialize retrieval pipeline resources.

    Loads and preprocesses documents:
    - Chunking
    - Embedding generation
    - FAISS index creation
    - BM25 index creation

    Returns:
        dict: Updated state containing all_chunks, index, and bm25 objects.
    """
    all_chunks, index, bm25 = prepare_pipeline()
    return {
        "all_chunks":all_chunks,
        "index":index,
        "bm25":bm25
    }
#Node2: Hybrid Search
def retriver_node(state:RAGState):
    """
    Perform hybrid retrieval using BM25 and vector search.

    Enhancements:
    - Dynamically increases top_k based on retry count.
    - Rewrites query using LLM on retries to improve retrieval quality.

    Args:
        state (RAGState): Current pipeline state.

    Returns:
        dict: Retrieved chunks and updated retry count.
    """
    retry = state.get("retry_count", 0)
    
    #Increase search space each retry
    top_k = 10 + (retry * 5)
    query = state["query"]
    if retry > 0:
        query = llm(f"Rewrite this for better document retrieval:\n{query}")
    results = hybrid_search(state['query'], state['bm25'], state['index'], state['all_chunks'], top_k=10)
    return {'retrieved':results,
            "retry_count": retry }

#Node3: Reranker
def reranker_node(state:RAGState):
    """
    Re-rank retrieved documents using a cross-encoder model.

    This step improves relevance by scoring query-document pairs
    and selecting the most semantically relevant chunks.

    Args:
        state (RAGState): Current pipeline state.

    Returns:
        dict: Top-ranked document chunks.
    """
    ranked = reranker(state['query'], state['retrieved'], top_k=5)
    return {'reranked':ranked}

#Node4:Generate answers
def generate_answers_node(state:RAGState):
    """
    Generate final answer using LLM with retrieved context.

    The answer is grounded in reranked chunks and includes citations.

    Args:
        state (RAGState): Current pipeline state.

    Returns:
        dict: Generated answer string.
    """
    answers = answer_with_citations(state['query'], state['reranked'])
    return {'answer':answers}

#Node5: Validate answer
def validate_node(state: RAGState):
     """
    Validate generated answer using semantic similarity (faithfulness check).

    This node determines whether the answer is sufficiently grounded
    in retrieved context. If not, it triggers a retry.

    Logic:
    - Computes cosine similarity between answer and context
    - Uses top 3 chunks for better grounding
    - Retries if similarity < threshold
    - Limits retries to prevent infinite loops

    Args:
        state (RAGState): Current pipeline state.

    Returns:
        dict:
            needs_retry (bool): Whether to retry pipeline
            retry_count (int): Updated retry count
    """

    retry = state.get("retry_count", 0)
    answer = state["answer"]
    # Use more context (important)
    if not state.get("reranked"):
        return {"needs_retry": True, "retry_count": retry + 1}
    context = " ".join([c["chunks"] for c in state["reranked"][:3]])
    pred_clean = normalize(clean_answer(answer))
    context_clean = normalize(context)

    faithfulness = compute_similarity(pred_clean, context_clean)
    # Retry logic
    needs_retry = faithfulness < 0.75 and retry < 2   # limit retries
    

    return {"needs_retry": needs_retry,
            "retry_count": retry + 1}

#Retry Logic
def route_validation(state):
     """
    Route decision after validation step.

    Determines next step in graph execution:
    - 'retry' → re-run retrieval pipeline
    - 'end' → finish execution

    Args:
        state (RAGState): Current pipeline state.

    Returns:
        str: Next node label ("retry" or "end")
    """
    return "retry" if state["needs_retry"] else "end"

#Build Graph
def build_graph():
    """
    Construct and compile LangGraph pipeline for RAG workflow.

    Graph Flow:
        prepare → retrieve → rerank → generate → validate
                                           ↑        ↓
                                           └── retry ──

    Features:
    - Hybrid retrieval (BM25 + vector search)
    - Cross-encoder reranking
    - LLM-based answer generation with citations
    - Adaptive retry loop with validation

    Returns:
        Compiled LangGraph object ready for execution.
    """
    builder = StateGraph(RAGState)
    builder.add_node("prepare", prepare_node)
    builder.add_node("retrieve", retriver_node)
    builder.add_node("rerank", reranker_node)
    builder.add_node("generate", generate_answers_node)
    builder.add_node("validate", validate_node)
    #Data Flow
    builder.set_entry_point("prepare")
    builder.add_edge("prepare", "retrieve")
    builder.add_edge("retrieve", "rerank")
    builder.add_edge("rerank", "generate")
    builder.add_edge("generate", "validate")
    #retry if the validate node says retry , loop back to Retriever node
    builder.add_conditional_edges(
        "validate",
        route_validation,
        {
            "retry": "retrieve",   # re-run retrieval
            "end": "__end__"
        }
    )
    graph = builder.compile()
    return graph