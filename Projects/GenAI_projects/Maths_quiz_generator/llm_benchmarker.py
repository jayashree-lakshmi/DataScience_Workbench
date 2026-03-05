
import os 
import requests
import json
import time
import random
import sys
import math
import  maths_logic
import re
import cloud_api
import csv


def math_prompt_generator(grade, logic):
    # Determine if the hint should be visible in the question (for Grades 8, 9, 10)
    question_display = logic.problem
    if int(grade) > 8:
        question_display = f"{logic.problem} (Hint: {logic.hint})"
   
    return f"""
      ### ROLE
      Expert Grade {grade} Mathematics Teacher.
      
      ### DATA (STRICT TRUTH)
      - Question: {logic.problem}
      - Correct Answer: {logic.solution}
      - Teaching Logic/Hint: {logic.hint}
      
      ### TASK
      Generate a JSON response for this question. 
      1. Create a "choices" list containing 4 unique options:
         - One option MUST be the correct answer: {logic.solution}.dont include {logic.problem} 
         - The other 3 must be "smart" distractors (common errors like wrong sign, addition instead of multiplication, etc.).
         - The "choices" list MUST be an array of 4 unique strings or numbers. 
         - SHUFFLE the list so the correct answer is not always in the same position.
         - EVERY option in the "choices" list MUST be a raw integer or a string. 
3. DO NOT include math operations (like + or *) inside the choices list.
      2. Write a supportive 'explanation' for a Grade {grade} student. 
         Base the explanation strictly on the Teaching Logic provided: {logic.hint}.
        

      ### JSON FORMAT
      {{
        "id": 1,
        "grade": {grade},
        "question_text": "{question_display}",
        "choices": [],
        "answer": "{logic.solution}",
        "explanation": "..."
      }}
      """

def get_logic_for_grade(grade):
    grade = int(grade)
    # Find the closest grade match if exact grade isn't in dict
    available_grades = sorted(maths_logic.MATH_CONFIG.keys())
    closest_grade = max([g for g in available_grades if g <= grade] or [1])
    
    # Pick a random operation from that grade's list
    operation = random.choice(maths_logic.MATH_CONFIG[closest_grade])
    return operation()

def evaluate_response(raw_response, logic_task):
    try:
        # Standardize formatting
        clean_content = re.sub(r'```json|```', '', raw_response).strip()
        data = json.loads(clean_content)
        
        is_correct = str(data.get("answer")).strip() == str(logic_task.solution).strip()
        
        # --- IMPROVED HALLUCINATION CHECK ---
        choices = data.get("choices", [])
        has_syntax_hallucination = False
        
        for choice in choices:
            choice_str = str(choice).replace(" ", "") # Remove spaces for easier checking
            
            # Check for actual operations: +, *, / 
            # Or a '-' that is NOT at the start of the string (which would be a negative number)
            if any(op in choice_str for op in "+*/"):
                has_syntax_hallucination = True
                break
            
            # Check for subtraction (a minus sign with a digit before it)
            if re.search(r'\d-', choice_str):
                has_syntax_hallucination = True
                break
        if has_syntax_hallucination:
            print(raw_response)
        return {
            "valid_json": True,
            "is_correct": is_correct,
            "hallucination": has_syntax_hallucination,
            "data": data
        }
    except Exception as e:
        return {"valid_json": False, "error": str(e)}

def calculate_savings(df_logs):
    """
    Economic Impact Analysis for Llama 4 Scout vs. Local Phi-3.
    Metrics based on Groq April 2025 Pricing.
    """
    # March 2026 Price Points (USD)
    INPUT_PRICE_1M = 0.11
    OUTPUT_PRICE_1M = 0.34
    
    # Average tokens for a Grade 5-10 Math JSON response
    # (Approx 50 tokens for question/choices + 100 for explanation)
    avg_input_tokens = 250  
    avg_output_tokens = 150 
    
    # Cost per single Cloud request
    cost_per_request = ((avg_input_tokens / 1_000_000) * INPUT_PRICE_1M) + \
                       ((avg_output_tokens / 1_000_000) * OUTPUT_PRICE_1M)
    
    # Filter by model type
    cloud_runs = df_logs[df_logs['Type'] == 'Cloud'].shape[0]
    local_runs = df_logs[df_logs['Type'] == 'Local'].shape[0]
    
    total_cloud_spend = cloud_runs * cost_per_request
    total_savings = local_runs * cost_per_request # What it WOULD have cost
    
    return {
        "Cloud Actual Spend (USD)": round(total_cloud_spend, 6),
        "Total Savings (Local)": round(total_savings, 6),
        "Cost per 1000 Queries": round(cost_per_request * 1000, 4)
    }

def log_experiment(grade, model_name, model_type, latency, is_correct, has_hallucination):
    file_exists = os.path.isfile('research_logs.csv')
    with open('research_logs.csv', mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Grade', 'Model', 'Type', 'Latency', 'Correct', 'Hallucination'])
        writer.writerow([time.time(), grade, model_name, model_type, latency, is_correct, has_hallucination])

def call_ollama(prompt,local_model):
    """Ollama - The Offline Safety Net"""
    print(f"🏠 Attempting Local Ollama ({local_model})...")
    url = "http://localhost:11434/api/chat"
    # Use a random seed so every API call is fresh
    random_seed = random.randint(1, 1000000)
    payload = {
        "model": local_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.7, # Makes the output stable/deterministic
            #"num_predict": 1024,
            "seed":random_seed,# Stop the model from rambling
            #"top_k": 20 # Narrow the focus for math accuracy
        }
    }
    
    response = requests.post(url, json=payload, timeout=120)
    return response.json()['message']['content']

def call_cloud_model(prompt,cloud_model):
    if cloud_model=='deepseek':
      return cloud_api.call_deepseek(prompt)
    elif cloud_model=='Llama4':
      return cloud_api.call_llama(prompt)
    
def generate_math_questions(grade):
    result = []
    for i in range(15):
      logic=get_logic_for_grade(grade)
      prompt = math_prompt_generator(grade,logic)
      raw_json= call_ollama(prompt,'phi3')
      cleaned_data=json.loads(raw_json)
      cleaned_data["id"] = i + 1
      cleaned_data["answer"] = logic.solution
      print(cleaned_data)
      result.append(cleaned_data)
      time.sleep(0.5)

    return result
  
if __name__=="__main__":
    grade = sys.argv[1]
    res = generate_math_questions(grade)
    #print(res)
