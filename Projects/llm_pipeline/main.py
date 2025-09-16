
import streamlit as st
from langchain_helper import create_vectordb, get_qa_chain
from PIL import Image

st.set_page_config(page_title="Kids Q&A Bot", page_icon="🧠", layout="centered")

# 🎉 Title and mascot
st.markdown("<h1 style='text-align: center;'>🧠 Curious Kids Q&A Bot</h1>", unsafe_allow_html=True)
import random
greetings = [
    "Ready to explore something amazing?",
    "Ask me anything—I'm full of fun facts!",
    "Curious minds welcome!",
    "🍎 Learning is delicious—let's snack on some knowledge!"
]
st.markdown(f"<p style='text-align: center; font-size:16px;'>{random.choice(greetings)}</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Ask me anything fun, weird, or wonderful!</p>", unsafe_allow_html=True)

# Create knowledge base
if st.button('📚 Create Knowledgebase'):
    create_vectordb()
    st.success("Knowledgebase created! Ready to answer curious questions.")

# Question input
question = st.text_input('🔍 What do you want to know today?')

if question:
    chain = get_qa_chain()
    response = chain(question)
    source_docs = response.get('source_documents', [])
    
    # Answer display
    st.markdown("<p style='font-size:16px; font-weight:bold;'>✅ Here's what I found:</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style='
            background-color:#fff3cd;
            color:#000;
            padding:15px;
            border-left: 6px solid #ffc107;
            border-radius:10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        '>
        """ + response['result'] + "</div>", unsafe_allow_html=True)

    # Show source toggle
    with st.expander("📖 Show where I got this from"):
        for doc in source_docs:
            st.markdown(f"**Source:** {doc.metadata['source']}")
            st.code(doc.page_content)

    # Fallback if no match
    if not source_docs or response['result'].strip().lower().startswith("i don't know"):
        st.warning("Hmm... I couldn't find that in my files. Try asking something else!")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size:14px;'>Made with 💡 for curious minds!</p>", unsafe_allow_html=True)
