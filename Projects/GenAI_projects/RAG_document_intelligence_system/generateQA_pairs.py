import json
import random
from hybrid_rag_pipeline import (
    load_docs,
    docs_to_text,
    chunking,
    embedding,
    llm
)

def prepare_chunks():
    print('=======================preparing_chunks')
    all_chunks = []
    docs = load_docs()

    for doc in docs:
        text_data = docs_to_text(doc)
        chunks = chunking(text_data)
        all_chunks.extend(chunks)

    all_chunks = embedding(all_chunks)
    return all_chunks


def generate_qa_pairs(chunks, num_samples=50):
    print('=======================generate_qa_pairs')
    qa_dataset = []
    sampled_chunks = random.sample(chunks, num_samples)

    for chunk in sampled_chunks:

        prompt = f"""
            Generate 1 question and answer pair from the context below.

            Rules:
            - Question should be specific
            - Answer must be directly from context
            - Keep answer short
            
            Context:
            {chunk['chunks']}

            Output:
            Question: ...
            Answer: ...
            """

        response = llm(prompt)

        try:
            lines = response.split("\n")
            question = lines[2].replace("Question:", "").strip()
            answer = lines[3].replace("Answer:", "").strip()

            qa_dataset.append({
                "question": question,
                "answer": answer,
                "doc_id": chunk["doc_id"],
                "page": chunk["page"],
                "chunk_id": chunk["chunk_id"]
            })

        except:
            continue

    return qa_dataset


if __name__ == "__main__":

    chunks = prepare_chunks()

    dataset = generate_qa_pairs(chunks, num_samples=100)

    with open("data/qa_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)

    print("QA dataset generated successfully!")