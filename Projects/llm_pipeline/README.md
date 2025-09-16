# **Project: LLM Pipeline** 📦
# 🧠 Curious Kids Q&A Bot
A playful and educational chatbot built with LangChain and Streamlit that answers kids' everyday questions using a custom CSV knowledge base. Perfect for classrooms, parents, or curious young minds!


# How it Works
Loads questions and answers from kids_faqs.csv

Converts questions into vector embeddings using HuggingFace

Uses FAISS for fast semantic search
Answers only if a close match is found — otherwise says: "I don't know. Not in the file provided"

## 🛠️ Tech Stack
Step1: creating knowledge base stage: Loaded csv file which has question and answers list will be embedded using hugging face and loaded to vector db FAISS
Step2: When the user asks questions below process takes place
* Embeddings-Converts questions into vector format,HuggingFaceInstructEmbeddings 
* Stores and retrieves question embeddings-FAISS (Facebook AI Similarity Search)
* LLM model(OpenAI) -Generates answers from retrieved context,OpenAI via langchain_openai.OpenAI
* Retrieval Chain	Combines retriever + prompt + LLM - LangChain RetrievalQA

Frontend: developed using Streamlit application
---

## 🚀 Features

- ✅ Answers only from your curated CSV file — no made-up responses!
- 🔍 Semantic search with fuzzy matching to handle similar questions
- 🎨 Fun and friendly Streamlit interface with emojis and colorful styling
- 📚 Easy-to-update knowledge base using `kids_faqs.csv`
- 🔐 Secure API key management

---
## 📁 Project Structure

├── kids_faqs.csv # Your question-answer knowledge base 
├── langchain_helper.py # Core logic for vector DB and QA chain 
├── main.py # Streamlit frontend 
├── secret_key.py # Your OpenAI API key (excluded from Git) 
├── Faiss_index/ # Saved vector database

---

## 🛠️ Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/your-username/kids-qa-bot.git
cd kids-qa-bot

Create a file called secret_key.py and add:
openapi_key = "your-openai-api-key"

pip install -r requirements.txt

run the aoo
streamlit run main.py




