import sys
import streamlit as st
import pandas as pd
import llm_benchmarker
import cloud_api
import time
import os

st.set_page_config(page_title="SLM vs LLM Benchmark", layout="wide")

# --- UI Header ---
st.title("🔬 Hybrid LLM Research Lab")
st.markdown("Comparing **Local SLMs** (Ollama) vs **Cloud LLMs** (Groq/Llama 4 Scout).")

tab1, tab2 = st.tabs(["🚀 Live Benchmarking", "📊 Results & Analytics"])

# ==========================================
# TAB 1: LIVE BENCHMARKING
# ==========================================
with tab1:
    col_settings, col_display = st.columns([1, 3])
    
    with col_settings:
        st.header("Parameters")
        grade = st.selectbox("Grade", range(1, 11), index=4)
        
        # Split models by source
        local_model = st.selectbox("Local Model (Ollama)", ["phi3", "llama3.2:3b"])
        cloud_model = st.selectbox("Cloud Model (API)", ["Llama4", "deepseek"])
        
        run_btn = st.button("Generate Comparison")

    with col_display:
        if run_btn:
            logic =  llm_benchmarker.get_logic_for_grade(grade)
            prompt =  llm_benchmarker.math_prompt_generator(grade, logic)
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader(f"🏠 Local: {local_model}")
                start_time = time.time()
                # Call Ollama
                res_local =  llm_benchmarker.call_ollama(prompt, local_model)
                local_latency = time.time() - start_time
                st.json(res_local)
                local_eval = llm_benchmarker.evaluate_response(res_local, logic)
                # --- CALL LOGGING FOR LOCAL ---
                llm_benchmarker.log_experiment(
                    grade=grade,
                    model_name=local_model,
                    model_type="Local",
                    latency=local_latency,
                    is_correct=local_eval["is_correct"],
                    has_hallucination=local_eval["hallucination"]
                )
                # Display Metrics
                st.metric("Latency", f"{local_latency:.2f}s")
               
            with c2:
                st.subheader(f"☁️ Cloud: {cloud_model}")
                start_time = time.time()
                # Call Cloud API (DeepSeek/Llama)
                res_cloud = llm_benchmarker.call_cloud_model(prompt, cloud_model)
                cloud_latency = time.time() - start_time
                st.json(res_cloud)
                cloud_eval = llm_benchmarker.evaluate_response(res_cloud, logic)
                # --- CALL LOGGING FOR CLOUD ---
                llm_benchmarker.log_experiment(
                    grade=grade,
                    model_name=cloud_model,
                    model_type="Cloud",
                    latency=cloud_latency,
                    is_correct=cloud_eval["is_correct"],
                    has_hallucination=cloud_eval["hallucination"]
                )
                # Display Metrics
                st.metric("Latency", f"{cloud_latency:.2f}s")

# ==========================================
# TAB 2: RESULTS & ANALYTICS (REFINED)
# ==========================================
with tab2:
    st.header("📊 Research Performance Analysis")
    
    if os.path.exists('research_logs.csv'):
        df_logs = pd.read_csv('research_logs.csv')
        
        # --- Metric Summary ---
        # Ensure 'Correct' and 'Latency' columns are treated as numbers
        avg_acc = df_logs.groupby('Model')['Correct'].mean() * 100
        avg_lat = df_logs.groupby('Model')['Latency'].mean()
        
        m1, m2 = st.columns(2)
        with m1:
            st.subheader("Accuracy by Model (%)")
            st.bar_chart(avg_acc)
        with m2:
            st.subheader("Avg Latency (Seconds)")
            st.bar_chart(avg_lat)

        # --- Hallucination Analysis ---
        st.subheader("Hallucination Trends")
        hallucination_rate = df_logs.groupby('Model')['Hallucination'].sum()
        st.write("Total Syntactic Hallucinations Detected per Model:")
        st.table(hallucination_rate)
        
        # --- Economic Impact Analysis (Updated for Llama 4 Scout) ---
        st.divider()
        st.header("💰 Economic Impact Analysis")
        # Passing df_logs to your updated calculation function
        savings_data = llm_benchmarker.calculate_savings(df_logs)

        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            st.metric("Cloud API Costs Avoided", f"${savings_data['Total Savings (Local)']}")
            st.caption("Based on Llama 4 Scout pricing ($0.11/$0.34 per 1M)")
        with ec2:
            # Calculate total time difference
            local_time = df_logs[df_logs['Type'] == 'Local']['Latency'].sum()
            cloud_time = df_logs[df_logs['Type'] == 'Cloud']['Latency'].sum()
            st.metric("Total Latency 'Debt'", f"{local_time - cloud_time:.2f}s", delta_color="inverse")
            st.caption("The 'Cost' of local privacy in time")
        with ec3:
            st.metric("Cost per 1k Queries", f"${savings_data['Cost per 1000 Queries']}")
            st.caption("Projected Cloud operational expense")

        # --- Raw Data Export ---
        st.divider()
        st.subheader("📥 Export Data for LaTeX/Paper")
        st.dataframe(df_logs)
        st.download_button(
            label="Download CSV for Analysis",
            data=df_logs.to_csv(index=False),
            file_name="llm_math_results.csv",
            mime="text/csv"
        )
    else:
        st.warning("No research data found. Run some benchmarks in the first tab to see analysis!")