# import sys
# try:
#     import pysqlite3
#     sys.modules["sqlite3"] = pysqlite3
# except Exception:
#     pass

# import streamlit as st
# from dotenv import load_dotenv
# import os
# import datetime
# import pandas as pd
# from utils import structure_logs, chunk_structured_logs
# from langchain_core.documents import Document
# from langchain_community.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.chains import RetrievalQA
# from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv
import os
import datetime
import pandas as pd

from utils import structure_logs, chunk_structured_logs

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA


from langchain_groq import ChatGroq
from langchain_core.documents import Document


# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Init LLM + Embeddings
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama3-70b-8192")
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)


# Initialize session state
if "all_chunk_insights" not in st.session_state:
    st.session_state.all_chunk_insights = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

# Sidebar
with st.sidebar:
    st.title("📘 How to Use")
    st.markdown("""
    1. Upload .log or .txt  
    2. Filter logs by severity  
    3. Run AI Chunk Analysis  
    4. Generate Summary or Ask Questions
    """)

# Main UI
st.markdown("<h1 style='text-align:center;'>🧠 LogMentor RAG</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Structured Log Analysis with ChromaDB + LLM</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Upload & Filter", "🔍 Chunk Analysis", "🧠 Final Summary", "💬 Ask Logs"
])

# Tab 1 – Upload + Filter
with tab1:
    uploaded_file = st.file_uploader("📁 Upload log file", type=["txt", "log"])
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.text_area("📄 Preview Logs", raw_text[:2000], height=300)

        # Log filtering
        level = st.selectbox("🔎 Filter by Level", ["All", "INFO", "DEBUG", "WARNING", "ERROR"])
        if level != "All":
            raw_text = "\n".join([line for line in raw_text.splitlines() if level in line])
            st.text_area("📄 Filtered Logs", raw_text[:2000], height=300)

        structured_logs = structure_logs(raw_text)
        st.session_state.chunks = chunk_structured_logs(structured_logs)

        st.success(f"✅ Structured {len(structured_logs)} log entries into {len(st.session_state.chunks)} chunks")

        # Run AI Chunk Analysis
        if st.button("🚀 Run AI Chunk Analysis"):
            with st.spinner("Analyzing chunks..."):
                st.session_state.all_chunk_insights.clear()
                for i, chunk in enumerate(st.session_state.chunks):
                    prompt = f"""
                    You are a professional log analyst. Analyze the following logs:
                    
{chunk}

                    Return:
                    1. Summary
                    2. Errors
                    3. Root cause
                    4. Suggested Fix
                    """
                    result = llm.invoke(prompt)
                    st.session_state.all_chunk_insights.append(result)
            st.success("✅ Chunk Analysis Completed!")

# Tab 2 – Chunk-wise LLM Analysis
with tab2:
    if st.session_state.all_chunk_insights:
        for i, result in enumerate(st.session_state.all_chunk_insights):
            with st.expander(f"🔍 Chunk {i+1}"):
                st.markdown(result.content)
    else:
        st.info("No analysis yet. Go to Tab 1, upload logs, and click Run Analysis.")

# Tab 3 – Final Summary + Download
with tab3:
    if st.session_state.all_chunk_insights:
        combined = "\n\n".join([res.content for res in st.session_state.all_chunk_insights])
        final_prompt = f"Summarize all these chunk-wise log analyses:\n{combined}"
        final_result = llm.invoke(final_prompt)

        st.success("📄 Final Summary")
        st.markdown(final_result.content)

        # Download Button
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"log_summary_{timestamp}.txt"
        st.download_button("📥 Download Summary", data=final_result.content, file_name=file_name, mime="text/plain")
    else:
        st.info("No chunks analyzed. Please analyze logs first.")

# Tab 4 – Chat With Logs (RAG)
with tab4:
    if st.session_state.chunks:
        with st.spinner("📦 Embedding and indexing chunks..."):
            documents = [Document(page_content=chunk) for chunk in st.session_state.chunks]
            vectorstore = Chroma.from_documents(documents, embedding)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        user_query = st.text_input("💬 Ask something about the logs")
        if user_query:
            with st.spinner("💡 Thinking..."):
                response = qa_chain.run(user_query)
                st.markdown("🧠 **Answer**")
                st.markdown(response)
    else:
        st.info("No logs to query. Please upload and analyze first.")
