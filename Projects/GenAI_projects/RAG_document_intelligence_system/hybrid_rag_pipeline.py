import os 
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss 
import numpy as np
from rank_bm25 import BM25Okapi
from groq import Groq

#load embedding model
encoding_model = SentenceTransformer("all-MiniLM-L6-v2")
chunk_size=800
chunk_overlap=120
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=API_KEY)
rerank = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def load_docs(): #Load Documents
    """
    Load document file paths from the data directory.

    Only PDF files are considered.

    Returns:
        list: List of file paths for PDF documents.
    """
    folder_path = 'data/raw_docs'
    documents = []
    doc_files = os.listdir(folder_path)
    for file in doc_files:
        print(file)
        filename = os.path.join(folder_path,file)
        if os.path.exists(filename):
            if file.endswith('.pdf'):
                documents.append(filename)
    return documents

def docs_to_text(filepath): # pdf Docs to text converter
    """
    Extract text content from a PDF file.

    Converts each page into a structured dictionary containing:
    - document ID
    - page number
    - extracted text

    Args:
        filepath (str): Path to the PDF file.

    Returns:
        list: List of page-level dictionaries.
    """
    with pdfplumber.open(filepath) as fp:
        page_text = []
        for i,pages in enumerate(fp.pages):
            text = pages.extract_text()
            page_text.append({'doc_id':os.path.basename(filepath),'page_num':i+1,
                          'text':text})
            
    return page_text

def chunking(page_text): # text to chunks
    """
    Split document text into overlapping chunks.

    Uses RecursiveCharacterTextSplitter to create manageable
    text segments for embedding and retrieval.

    Each chunk includes metadata for traceability.

    Args:
        page_text (list): Page-level extracted text.

    Returns:
        list: List of chunk dictionaries with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap,
                                              separators=["\n\n", "\n", ".", " ", "","........."])
    
    chunks_data = []
    for page in page_text:
        page_chunks = splitter.split_text(page['text'])
        for i,chunks in enumerate(page_chunks): #for every chunks applying metadata for citation
            chunks_metadata = {'page':page['page_num'],
                            'doc_id':page['doc_id'],
                            'chunk_id':f"{page['doc_id']}_{page['page_num']}_{i}",
                            'chunks':chunks}
            chunks_data.append(chunks_metadata)

    return chunks_data

def embedding(chunk_metadata):
    """
    Generate embeddings for all text chunks.

    Uses SentenceTransformer to convert text into vector representations.

    Args:
        chunk_metadata (list): List of chunk dictionaries.

    Returns:
        list: Updated chunks with embedding vectors.
    """
    chunk_text = [ch['chunks'] for ch in chunk_metadata]
    embed_chunktext = encoding_model.encode(chunk_text)
    for chunk, emb in zip(chunk_metadata,embed_chunktext):
        chunk['embedding'] = emb
    return chunk_metadata

def build_faiss_index(all_chunks):
    """
    Build FAISS vector index for semantic search.

    Uses L2 distance for similarity search.

    Args:
        all_chunks (list): Chunk data with embeddings.

    Returns:
        faiss.Index: FAISS index object.
    """
    embeddings = np.array([chunk['embedding'] for chunk in all_chunks]).astype("float32")
    dimension = embeddings.shape[1]
    #embedding to vector database/index
    index = faiss.IndexFlatL2(dimension) #creates a vector search index 
    #Flat → brute-force search, L2 → Euclidean distance similarity
    index.add(embeddings)
    return index

def build_bm25_index(chunks):
    """
    Build BM25 keyword-based retrieval index.

    Tokenizes text into lowercase words.

    Args:
        chunks (list): Chunk data.

    Returns:
        BM25Okapi: BM25 index object.
    """
    tokenized_chunks = [ch['chunks'].lower().split() for ch in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    return bm25

def bm25_search(query, bm25, chunks, top_k=5):
    """
    Perform keyword-based search using BM25.

    Args:
        query (str): Input query.
        bm25 (BM25Okapi): BM25 index.
        chunks (list): Chunk data.
        top_k (int): Number of results.

    Returns:
        list: Top matching chunks.
    """
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = [chunks[i] for i in top_indices]
    return results

def vector_search(query,index,chunks,top_k=5):
    """
    Perform semantic search using FAISS vector index.

    Args:
        query (str): Input query.
        index (faiss.Index): Vector index.
        chunks (list): Chunk data.
        top_k (int): Number of results.

    Returns:
        list: Top matching chunks.
    """
    query_embedding = encoding_model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    results = []
    for i in indices[0]:
        results.append(chunks[i])
    return results

def hybrid_search(query,bm25,index,all_chunks,top_k):
    """
    Combine BM25 and vector search results.

    Merges keyword-based and semantic retrieval outputs,
    removing duplicates.

    Args:
        query (str): Input query.
        bm25 (BM25Okapi): BM25 index.
        index (faiss.Index): Vector index.
        all_chunks (list): Chunk data.
        top_k (int): Number of results.

    Returns:
        list: Combined top-k results.
    """
    combined = {}
    #Implement Keyword Search : BM25
    bm25_res = bm25_search(query, bm25, all_chunks, top_k)
    #Implement Vector search: FAISS
    vect_res = vector_search(query,index,all_chunks,top_k)
    for r in bm25_res + vect_res:
        combined[r["chunk_id"]] = r
    return list(combined.values())[:top_k]

def reranker(query,retrieved_chunks,top_k):
    """
    Re-rank retrieved chunks using cross-encoder model.

    Improves relevance by scoring query-document pairs.

    Args:
        query (str): Input query.
        retrieved_chunks (list): Retrieved chunks.
        top_k (int): Number of final results.

    Returns:
        list: Top reranked chunks.
    """
    pairs = [(query,chu['chunks']) for chu in retrieved_chunks]
    scores = rerank.predict(pairs)
    for chunk,score in zip(retrieved_chunks,scores):
        chunk['rerank_score'] = score
    reranked = sorted(retrieved_chunks,key=lambda x:x['rerank_score'],reverse=True)
    return reranked[:top_k]

def generate_answer(query, ranking_results):
    """
    Generate answer using LLM based on retrieved context.

    Concatenates top chunks and sends prompt to LLM.

    Args:
        query (str): User query.
        ranking_results (list): Top-ranked chunks.

    Returns:
        str: Generated answer.
    """

    context=""
    for res in ranking_results:
        context += res['chunks']
    prompt = f"""
        You are a financial document assistant.
        Use ONLY the provided context to answer the question.
        If the answer exists partially in the context, extract the relevant information.
        Do NOT say "information not found" if related information exists.

        Context:
        {context}

        Question:
        {query}

        Answer concisely:
        """
    answer = llm(prompt)
    return answer

def attach_citations(answer, chunks):
    """
    Attach source citations to the generated answer.

    Uses top chunks to construct references.

    Args:
        answer (str): Generated answer.
        chunks (list): Retrieved chunks.

    Returns:
        str: Answer with citations appended.
    """
    citations = []
    for chunk in chunks[:2]:
        citation = f"{chunk['doc_id']} page {chunk['page']}"
        if citation not in citations:
            citations.append(citation)
    citation_text = "\n".join(citations)
    final_answer = f"""
                    {answer}

                    Sources:
                        {citation_text}
                    """
    return final_answer

def answer_with_citations(query, reranked_chunks):
    """
    Generate final answer with citations.

    Combines LLM output and source attribution.

    Args:
        query (str): User query.
        reranked_chunks (list): Top-ranked chunks.

    Returns:
        str: Final answer with citations.
    """
    answer = generate_answer(query, reranked_chunks)
    final_answer = attach_citations(answer, reranked_chunks)
    return final_answer

def llm(prompt):
    """
    Call Groq LLM API to generate response.

    Uses LLaMA-based model for text generation.

    Args:
        prompt (str): Input prompt.

    Returns:
        str: Generated response text.
    """
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",#llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content

def prepare_pipeline():
    """
    End-to-end pipeline preparation.

    Steps:
    1. Load documents
    2. Extract text
    3. Chunk text
    4. Generate embeddings
    5. Build FAISS index
    6. Build BM25 index

    Returns:
        tuple:
            - all_chunks (list)
            - index (faiss.Index)
            - bm25 (BM25Okapi)
    """
    all_chunks = []
    #Load Documents
    doc_list = load_docs()
    for doc in doc_list:
        print(f'================{os.path.basename(doc)} Processing...=================')
        # pdf Docs to text converter
        text_data = docs_to_text(doc)
        # text to chunks converter
        chunk_metadata = chunking(text_data)
        all_chunks.extend(chunk_metadata)
    
    #Chunks to embedings 
    all_chunks = embedding(all_chunks)
    #embeddings to vector store 
    index = build_faiss_index(all_chunks)
    print("Total chunks indexed:", len(all_chunks))
    #Implement Keyword Search : BM25 index
    bm25 = build_bm25_index(all_chunks)
    print("\nTop Results:\n")
    return all_chunks, index, bm25

def main(query):
    top_k=10
    all_chunks, index, bm25 = prepare_pipeline()
    hybrid_results=hybrid_search(query,bm25,index,all_chunks,top_k)
    print("\nTop Results:\n")
    for r in hybrid_results:
        print(f"{r['doc_id']} page {r['page']}")
        print(r["chunks"])
        print("-" * 40)
    ranking_results = reranker(query,hybrid_results,top_k)
    
    final_answer = answer_with_citations(query, ranking_results)
    print(final_answer)
    
if __name__ == '__main__':
    query = "What are the Non-Marketable Investments"
    main(query)

#python -m uvicorn docsearch_app:app --reload