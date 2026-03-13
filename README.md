# DataScience_Workbench 
## 🚀 Welcome to my Data Science Portfolio! 

### This repository features projects that highlight my skills in data analysis, Python development, machine learning, and statistical modeling. Explore examples of data manipulation, predictive modeling, and insights from complex datasets, along with utilities to streamline daily tasks.

<img src="Images/Readmefile_cover.png" alt="DataScience_Workbench" width="100%">

---

## 🛠️ Core Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![SQL](https://img.shields.io/badge/SQL-CC2927?style=for-the-badge&logo=postgresql&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) ![LangChain](https://img.shields.io/badge/🦜%20LangChain-000000?style=for-the-badge) ![LangGraph](https://img.shields.io/badge/LangGraph-2e3b4e?style=for-the-badge) ![RAG](https://img.shields.io/badge/RAG-Systems-blueviolet?style=for-the-badge) ![Ollama](https://img.shields.io/badge/Ollama-white?style=for-the-badge&logo=ollama&logoColor=black)! ![FAISS](https://img.shields.io/badge/FAISS-Meta-0467DF?style=for-the-badge&logo=meta&logoColor=white)

---

## ✍️ Thought Leadership & Technical Writing
*Bridging the gap between childlike curiosity and professional AI engineering.*

| Category | Publication | Summary | Platform |
| :--- | :--- | :--- | :---: |
| **🔬 Primary Research** | [**Benchmarking Local SLMs vs. Cloud LLMs for Pedagogical Logic**](Projects/Maths_quiz_generator/Research_Paper.md) | A quantitative study on latency, TTFT, and cost-efficiency in educational AI. | [**Medium**](https://medium.com/@jayashree.lakshmi.jay/local-slms-vs-a5bf3b868f6f) |
| **🛠️ Engineering** | [**Building a Modular AI Story Generator with LangChain**](https://medium.com/@jayashree.lakshmi.jay/building-a-modular-ai-story-generator-with-langchain-a3c5c7c2f936) | Deep-dive into prompt chaining, modular architecture, and creative AI automation. | [**Medium**](https://medium.com/@jayashree.lakshmi.jay/building-a-modular-ai-story-generator-with-langchain-a3c5c7c2f936) |
| **💡 Philosophy** | [**Generative AI: A Childlike Curiosity Meets Technological Genius**](https://medium.com/@jayashree.lakshmi.jay/generative-ai-a-childlike-curiosity-meets-technological-genius-0e056386958a) | Exploring the intuitive nature of LLMs and how they mirror human learning patterns. | [**Medium**](https://medium.com/@jayashree.lakshmi.jay/generative-ai-a-childlike-curiosity-meets-technological-genius-0e056386958a) |

---

## 🏗️ Project Showcase

### 🤖 Generative AI & LLM Applications
*Advanced RAG pipelines, SLM benchmarking, and stateful AI agents.*

---
#### Project🔬: Production ready RAG document search with Citation Enforcement
<img src="Images/RAG_pipeline.png" align="left" width="300" alt="RAG Pipeline">
Built an end-to-end Retrieval Augmented Generation (RAG) system that answers questions from PDF documents using hybrid retrieval (BM25 + vector search) and cross-encoder reranking.
The pipeline generates grounded answers using Groq-hosted LLMs and automatically attaches source citations with document and page references.
![Status](https://img.shields.io/badge/status-active_development-orange)
<br clear="left"/>

#### Project🔬:  Local SLMs vs. Cloud LLMs: A Quantitative Study
<img src="Images/llm_slm_basic.png" align="left" width="300" alt="SLM vs LLM Research">

A technical research project evaluating the trade-offs between local execution and cloud-based inference.
- **Tech Stack:** ![Ollama](https://img.shields.io/badge/Ollama-white?style=flat&logo=ollama&logoColor=black) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
- **Key Focus:** Benchmarking **Inference Logic** vs. **Operational Cost-Efficiency**.
- **Insight:** Developed a framework to quantify "Syntax Hallucination" and latency across different hardware tiers.
- [**Research Project**](Projects/GenAI_projects/Maths_quiz_generator/README.md)

<br clear="left"/>

#### Project📚: Kids Bedtime Story Generator
<img src="Images/kidstory.png" align="left" width="300" alt="Story Generator">

An interactive storytelling engine that creates personalized narratives and illustrations for children.
- **Tech Stack:** ![LangChain](https://img.shields.io/badge/🦜_LangChain-black?style=flat) ![OpenAI](https://img.shields.io/badge/GPT--4o-412991?style=flat&logo=openai&logoColor=white) ![DALL-E](https://img.shields.io/badge/DALL--E_3-412991?style=flat&logo=openai&logoColor=white)
- **Key Focus:** Prompt engineering for moral extraction and creative consistency.
- **Feature:** Seamlessly integrates character traits and settings into high-quality generated tales.
- [**Explore Story Generator**](Projects/GenAI_projects/Kid_story_generator/README.md)

<br clear="left"/>

#### Project🧠: Curious Kids Q&A Bot (RAG Pipeline)
<img src="Images/llm_pipeline.png" align="left" width="300" alt="RAG Pipeline">

A robust Knowledge Retrieval system designed to answer complex questions using verified data.

- **Tech Stack:** ![Vector DB](https://img.shields.io/badge/FAISS-0467DF?style=flat&logo=meta&logoColor=white) ![RAG](https://img.shields.io/badge/RAG-Systems-blueviolet?style=flat) ![LangGraph](https://img.shields.io/badge/LangGraph-2e3b4e?style=flat)
- **Key Focus:** Semantic search and retrieval-augmented generation.
- **Architecture:** Employs a stateful graph to route queries between local vector stores and structured datasets.
- [**View RAG Implementation**](Projects/GenAI_projects/llm_pipeline/README.md)

<br clear="left"/>

---
---

### 🎯 Recommendation & Personalization Systems
*Building discovery engines through collaborative and content-based filtering.*



| Project | Preview | Core Algorithm | Link |
| :--- | :---: | :--- | :--- |
| **Music Recommender System 🎵** | <img src="Images/music_rec.png" width="200"> | Collaborative Filtering / KNN | [Read more](Projects/Music_recommender/README.md) |
| **Amazon Product Recommender 📦** | <img src="Images/amz_prod.png" width="200"> | Matrix Factorization / SVD | [Read more](Projects/Amazon_product_recommender/README.md) |

---

### 📊 NLP & User Behavior Analysis
*Extracting sentiment and segments from unstructured text and transaction data.*

#### 🧠 Depression Detection [Sentiment Analysis]
<img src="Images/depression_detection.png" align="right" width="250"> 

Predicting mental health indicators using various supervised machine learning models. 
- **Models:** Logistic Regression, Random Forest, BERT.
- **Focus:** Analyzing linguistic patterns for early detection.
- [Read full report](Projects/Tweet_sentiment_analysis_supervisedML/README.md)

<br clear="right"/>

#### 👥 Customer Segmentation
<img src="Images/customer_analysis.png" align="left" width="250"> 

Understanding customer behaviors, preferences, and demographics to enhance business strategies.
- **Method:** Unsupervised ML, K-Means Clustering, RFM Analysis.
- **Outcome:** Data-driven personas for targeted marketing.
- [Read full report](Projects/Customer_segmentation_unsupervisedML/README.md)

---

## 📈 Featured Research: Local SLM Efficiency

**Operational cost-efficiency of Local SLMs.** My latest benchmarks show that for specific pedagogical logic tasks, local 3B parameter models (like Phi-3) can maintain high instruction-following accuracy while reducing long-term API costs by over 90% compared to cloud-scale LLMs.

---