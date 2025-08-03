import streamlit as st
from dotenv import load_dotenv
import os
import datetime
import pandas as pd
from utils import structure_logs, chunk_structured_logs
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM & Embeddings
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-70b-8192")
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Setup Streamlit Session State
if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "all_chunk_insights" not in st.session_state:
    st.session_state.all_chunk_insights = []

# Sidebar
with st.sidebar:
    st.title("📘 How to Use")
    st.markdown("""
    1. Upload `.log` or `.txt` file  
    2. Filter logs by severity  
    3. Run AI Chunk Analysis  
    4. View Summary or Ask Questions
    """)

# Title
st.markdown("<h1 style='text-align:center;'>🧠 LogMentor RAG</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Structured Log Analysis with ChromaDB + LLM</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Upload & Filter", "🔍 Chunk Analysis", "🧠 Final Summary", "💬 Ask Logs"
])

# --- Tab 1: Upload & Filter ---
with tab1:
    uploaded_file = st.file_uploader("📁 Upload log file", type=["txt", "log"])
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.text_area("📄 Preview Logs", raw_text[:2000], height=300)

        level = st.selectbox("🔎 Filter by Level", ["All", "INFO", "DEBUG", "WARNING", "ERROR"])
        if level != "All":
            raw_text = "\n".join([line for line in raw_text.splitlines() if level in line])
            st.text_area("📄 Filtered Logs", raw_text[:2000], height=300)

        structured_logs = structure_logs(raw_text)
        st.session_state.chunks = chunk_structured_logs(structured_logs)

        st.success(f"✅ Structured {len(structured_logs)} entries into {len(st.session_state.chunks)} chunks.")

        if st.button("🚀 Run AI Chunk Analysis"):
            with st.spinner("Analyzing..."):
                st.session_state.all_chunk_insights.clear()
                for chunk in st.session_state.chunks:
                    prompt = f"""
                    You are a professional log analyst. Analyze the following logs:
                    ```
                    {chunk}
                    ```
                    Return:
                    1. Summary
                    2. Errors
                    3. Root cause
                    4. Suggested Fix
                    """
                    response = llm.invoke(prompt)
                    st.session_state.all_chunk_insights.append(response)
            st.success("✅ Analysis Complete!")

# --- Tab 2: Chunk-Wise Results ---
with tab2:
    if st.session_state.all_chunk_insights:
        for idx, result in enumerate(st.session_state.all_chunk_insights):
            with st.expander(f"🔍 Chunk {idx + 1}"):
                st.markdown(result.content)
    else:
        st.info("No analysis yet. Upload logs and run analysis in Tab 1.")

# --- Tab 3: Final Summary + Download ---
with tab3:
    if st.session_state.all_chunk_insights:
        combined_text = "\n\n".join([res.content for res in st.session_state.all_chunk_insights])
        final_prompt = f"Summarize all these chunk-wise log analyses:\n{combined_text}"
        final_summary = llm.invoke(final_prompt)

        st.success("📄 Final Summary")
        st.markdown(final_summary.content)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"log_summary_{timestamp}.txt"
        st.download_button("📥 Download Summary", final_summary.content, file_name, "text/plain")
    else:
        st.info("No summaries yet. Please analyze logs first.")

# --- Tab 4: Ask Questions (RAG) ---
with tab4:
    if st.session_state.chunks:
        with st.spinner("📦 Indexing logs with Chroma..."):
            docs = [Document(page_content=chunk) for chunk in st.session_state.chunks]
            vectorstore = Chroma.from_documents(docs, embedding)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        user_question = st.text_input("💬 Ask something about the logs")
        if user_question:
            with st.spinner("💡 Thinking..."):
                answer = qa.run(user_question)
                st.markdown("🧠 **Answer**")
                st.markdown(answer)
    else:
        st.info("Upload and analyze logs to enable querying.")
