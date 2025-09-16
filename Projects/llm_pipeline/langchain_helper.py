
#When a user asks for a question, llm provides the answers provided in the csv file 
from langchain_openai import OpenAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os 
from secret_key import openapi_key
os.environ['OPENAI_API_KEY']=openapi_key
llm=OpenAI(temperature=0.7) #LLM model
instructor_embedding = HuggingFaceInstructEmbeddings()#model_name="hkunlp/instructor-large")
vectordb_filepath = 'Faiss_index'

def create_vectordb():

    #Embeddings: converting raw test to high dimensional values i.e vectors and store it in Vectordb
    #Loading data from csv file
    loader =CSVLoader(file_path='kids_faqs.csv',source_column='Questions')
    data=loader.load()
    vectordb = FAISS.from_documents(documents=data,embedding=instructor_embedding) 
    vectordb.save_local(vectordb_filepath)

def get_qa_chain():
    #load the vectordb from local file to inmemory
    vectordb = FAISS.load_local(vectordb_filepath,instructor_embedding,allow_dangerous_deserialization=True)
    retriever = vectordb.as_retriever(score_threshold=0.7)
    prompt_template = """Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "Response" section in the source document context without making much changes.
    If the answer is not found in the context, kindly state "I don't know.Not in the file provided" Don't try to make up an answer.

    CONTEXT: {context}

    QUESTION: {question}"""

    PROMPT = PromptTemplate(template=prompt_template,input_variables=['context','question'])
    chain = RetrievalQA.from_chain_type(llm=llm, 
                     chain_type='stuff',
                     retriever=retriever,
                     input_key='query',
                     return_source_documents =True,
                     chain_type_kwargs = {'prompt':PROMPT}
                     )
    return chain 

if __name__ == '__main__':
    try:
        create_vectordb()
        chain=get_qa_chain()
        print(chain('do you provide internship?do you have EMI option?'))
    except Exception as E:
        print(f"Error: {E}")

    