# LogMentor RAG – AI Log Analysis App

**LogMentor RAG** is a Streamlit application for AI-driven analysis of log files. It combines log structuring and filtering, chunk-wise AI analysis, retrieval-augmented Q&A (RAG), and summary features—leveraging Llama3-70B (Groq), HuggingFace embeddings, and ChromaDB.

---

## 🚀 Features

- **Upload and preview** `.log` or `.txt` files.
- **Filter** logs by severity (**INFO**, **DEBUG**, **WARNING**, **ERROR**).
- **Automatic structuring** and **chunking** of logs.
- **AI analysis for each chunk**: summary, error detection, root cause, fix suggestions.
- **Final summary** creation and export.
- **Chat with your logs** using retrieval-augmented generation (RAG).
- **Tabbed Streamlit interface** for simple navigation.

---

## 🛠️ Requirements

- Python 3.9+
- pip
- [Groq API Key](https://console.groq.com/)
- `utils.py` (must provide `structure_logs` and `chunk_structured_logs`)

---

## 🗂️ Installation

1. **Clone/Download this repo**

2. **Install dependencies:**

    ```
    pip install streamlit python-dotenv pandas langchain chromadb sentence-transformers pysqlite3 langchain_groq
    ```

3. **Setup API key:**

    - Create a `.env` file in your project root with:

        ```
        GROQ_API_KEY=sk-...
        ```

    - Or export directly in terminal:

        ```
        export GROQ_API_KEY=sk-...
        ```

4. **Ensure your `utils.py` exists with:**
    - `structure_logs(raw_text)`
    - `chunk_structured_logs(structured_logs)`

---

## ▶️ How to Run

streamlit run app.py

---

## 💡 Usage

- **Sidebar:** Step-by-step how-to and app info.
- **Tab 1:** Upload log file, filter logs, run AI chunk analysis.
- **Tab 2:** Browse AI's explanation for each chunk.
- **Tab 3:** View/download the AI's overall summary.
- **Tab 4:** Chat and ask questions about your logs (RAG interface).

---

## 📁 File Structure Example

app.py # Main Streamlit app (this file)
utils.py # Log structure/chunk helpers (required)
.env # Your API key here (never commit)
requirements.txt # Optional, for deployment
---

## ⚠️ Notes

- Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings on CPU by default.
- All LLM responses and chunk analysis are performed via Groq API; ensure you have network access and API quota.
- For larger files/models, you may need more RAM.
- This app does **not** upload or store your log files outside your session.

---

## 🐛 Troubleshooting

- **ImportError:** Check required packages installed; verify `utils.py` exists and implements required functions.
- **API errors:** Double-check your GROQ_API_KEY and internet access.
- **Performance:** Large files may need chunking or hardware adjustment.
- **File Preview Issues:** Ensure your file encoding is utf-8.


---

## 🙏 Credits

Built using open source tools: Streamlit, LangChain, ChromaDB, HuggingFace, Groq, and Python community libraries.

---
