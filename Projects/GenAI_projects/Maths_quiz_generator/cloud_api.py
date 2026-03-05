import os
import requests
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=API_KEY)

def call_deepseek(prompt):
    """DeepSeek R1"""
    print("Attempting DeepSeek R1(Reasoning)...")
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}", 
               "Content-Type": "application/json"}
    payload = {                                                                                                                                                                                                                                            
        "model": "deepseek-reasoner", # R1 model for math
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    return response.json()['choices'][0]['message']['content']

def call_llama(prompt):
    API_KEY = os.getenv('GROQ_API_KEY')
    client = Groq(api_key=API_KEY)
    print("Attempting (Llama 4 Scout)...")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"})
    return response.choices[0].message.content

