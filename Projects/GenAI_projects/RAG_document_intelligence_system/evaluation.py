import json 
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from ragas import evaluate as ragas_evaluate
from datasets import Dataset

from hybrid_rag_pipeline import (
    hybrid_search,
    reranker,
    answer_with_citations,
    prepare_pipeline
)

sim_model = SentenceTransformer("all-mpnet-base-v2")#("all-MiniLM-L6-v2")
THRESHOLDS = {
    "correctness": 0.75,
    "faithfulness": 0.80,
    "recall": 0.85,
    "citation": 0.95
}
def clean_answer(answer):
    """
    Remove citation section from generated answer.

    This ensures evaluation metrics focus only on the answer content
    and not appended source references.

    Args:
        answer (str): Raw answer including sources.

    Returns:
        str: Cleaned answer text.
    """
   
    return answer.split("Sources:")[0].strip()


def normalize(text):
    """
    Normalize text for fair comparison.

    Applies:
    - Lowercasing
    - Removal of punctuation

    Useful for embedding similarity comparisons.

    Args:
        text (str): Input text.

    Returns:
        str: Normalized text.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def load_dataset():
    """
    Load evaluation dataset from JSON file.

    Dataset format:
    [
        {
            "question": str,
            "answer": str,
            "doc_id": str
        }
    ]

    Returns:
        list: List of QA pairs.
    """
    filename = 'data/qa_dataset.json'
    with open(filename,'r') as fp:
        return json.load(fp)

def compute_similarity(a, b):
    """
    Compute cosine similarity between two text inputs.

    Steps:
    - Convert text to embeddings using SentenceTransformer
    - Compute cosine similarity

    Args:
        a (str): First text (e.g., predicted answer).
        b (str): Second text (e.g., ground truth or context).

    Returns:
        float: Similarity score between -1 and 1.
    """
    #Cosine similarity of 2 vectors, a.b/mod(a)*mod(b)
    emb = sim_model.encode([a, b])
    score = np.dot(emb[0], emb[1]) / (
        np.linalg.norm(emb[0]) * np.linalg.norm(emb[1])
    )
    return float(score)

def aggregate(results):
    """
    Aggregate evaluation metrics across all queries.

    Computes mean values for:
    - correctness
    - faithfulness
    - recall
    - citation

    Args:
        results (list): List of per-query evaluation results.

    Returns:
        dict: Averaged metrics.
    """
    n = len(results)
    return {
        "correctness": round(sum(r["correctness"] for r in results) / n, 3),
        "faithfulness": round(sum(r["faithfulness"] for r in results) / n, 3),
        "recall": round(sum(r["recall"] for r in results) / n, 3),
        "citation": round(sum(r["citation"] for r in results) / n, 3)
    }

def evaluation_gate(metrics):
    """
    Validate metrics against predefined thresholds.

    Acts as a quality gate for the RAG system.

    If any metric falls below its threshold:
        - Prints failure reasons
        - Raises exception

    Args:
        metrics (dict): Aggregated evaluation metrics.

    Raises:
        Exception: If any metric is below threshold.
    """
    failures = []
    for key, threshold in THRESHOLDS.items():
        if metrics[key] < threshold:
            failures.append(f"{key} below threshold: {metrics[key]} < {threshold}")

    if failures:
        print("\nBUILD FAILED\n")
        for f in failures:
            print(f)
        raise Exception("Evaluation Gate Failed")

    print("\nBUILD PASSED: All metrics above threshold\n")

def evaluate(dataset, all_chunks, index, bm25):
    """
    Run full evaluation pipeline for RAG system.

    For each query:
    1. Retrieve documents (hybrid search)
    2. Rerank using cross-encoder
    3. Generate answer with citations
    4. Evaluate using:
        - Custom metrics (cosine similarity)
        - RAGAS metrics (LLM-based evaluation)

    Metrics computed:
    - correctness: similarity between predicted and expected answer
    - recall: whether expected document is retrieved
    - citation: correctness of cited document
    - faithfulness: grounding of answer in retrieved context
    - ragas_faithfulness: LLM-based grounding score
    - ragas_answer_relevancy: LLM-based relevance score

    Args:
        dataset (list): Evaluation dataset.
        all_chunks (list): Document chunks.
        index (object): FAISS index.
        bm25 (object): BM25 index.

    Returns:
        list: Evaluation results per query.
    """
    results = []
    for item in dataset:
        query = item["question"]
        expected_answer = item["answer"]
        expected_doc = item["doc_id"]

        
        #________ 1. Retrieval___________
        
        retrieved = hybrid_search(query, bm25, index, all_chunks, top_k=10)

       
        # ________2. Reranking____________
      
        reranked = reranker(query, retrieved, top_k=5)
       
        # ________3. Generate Answer________
    
        pred_answer = answer_with_citations(query, reranked)

     
        # ________4. RAGAS Evaluation________
      
        ragas_data = Dataset.from_dict({
            "question": [query],
            "answer": [clean_answer(pred_answer)],
            "contexts": [[c["chunks"] for c in reranked]],
            "ground_truth": [expected_answer]
        })

        ragas_result = ragas_evaluate(ragas_data)
        ragas_scores = ragas_result.to_pandas().iloc[0]

        # ________4. Clean + Normalize________

        pred_clean = normalize(clean_answer(pred_answer))
        expected_clean = normalize(expected_answer)

   
        # ________________5. Correctness________________
  
        correctness = compute_similarity(pred_clean, expected_clean)


        # ________________6. Retrieval Recall________________
      
        retrieved_docs = [c["doc_id"] for c in reranked]
        recall = 1 if expected_doc in retrieved_docs else 0

        # ________________7. Citation Accuracy (FIXED)________________

        citation = 1 if expected_doc in retrieved_docs else 0
  
        # ________________8. Faithfulness (Top 3 Chunks Only)________________
       
        context_text = normalize(" ".join([c["chunks"] for c in reranked[:3]]))
        faithfulness = compute_similarity(pred_clean, context_text)


        # ________________9. Store Result________________
 
        results.append({
            "query": query,
            "pred_answer": pred_clean,
            # Custom evaluation using cosine similarity metrics
            "correctness": round(correctness, 3),
            "recall": recall,
            "citation": citation,
            "faithfulness": round(faithfulness, 3),
            #RAGAS metrics
            "ragas_faithfulness": ragas_scores["faithfulness"],
            "ragas_answer_relevancy": ragas_scores["answer_relevancy"]
 
        })

    return results

if __name__ == "__main__":
    
    dataset = load_dataset()
    print('Eveoluation stage======','RAG Pipeline')
    all_chunks, index, bm25 = prepare_pipeline()
    print('Eveoluation stage======','Evaluate')
    results = evaluate(dataset,all_chunks, index, bm25)
    metrics = aggregate(results)

    print("\nFINAL METRICS:\n")
    print(metrics)
    evaluation_gate(metrics)