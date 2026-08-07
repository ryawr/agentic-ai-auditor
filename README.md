# 🛡️ Agentic AI Compliance Extractor

**Agentic AI Compliance Extractor** is a robust, retrieval-augmented generation (RAG) application designed to extract and verify compliance policies from regulatory documents. By leveraging advanced vector search and high-speed LLM inference, this tool allows users to semantically query complex regulatory PDFs and receive accurate, context-aware responses. 

### **[Live app](https://agentic-ai-auditor-nifar6hdkdtgkkhquuzprk.streamlit.app/)**

## 🚀 Features

* **Intelligent Document Parsing:** Accurately extracts text and structural elements from complex regulatory PDFs.
* **Semantic Search:** Uses vector embeddings to find the most relevant document chunks based on user queries.
* **Hybrid Vector Database Management:**
  * **Persistent Knowledge Base:** Maintains a persistent vector database pre-loaded specifically with the **NIST AI RMF** document, eliminating the need to re-parse this standard framework on every run.
  * **Dynamic On-the-Go Ingestion:** Users can upload and query any custom regulatory PDF file on the fly. The application will automatically process the document and generate a **temporary vector database** specifically for that session's RAG workflow.
* **High-Speed Inference:** Generates precise compliance policy answers in real-time.
* **Interactive Web Interface:** Provides a streamlined, user-friendly dashboard for uploading documents and extracting policies.

---

## 🛠️ Architecture & Tech Stack

This project utilizes a modern AI stack tailored for speed and accuracy in agentic workflows:

* **[Unstructured](https://unstructured.io/):** Handles the heavy lifting of document ingestion. It is used for intelligent PDF parsing, partitioning, and chunking of unstructured regulatory text into optimal segments for embedding.
* **[Chroma DB](https://www.trychroma.com/):** Acts as the core vector database. It locally stores the vector embeddings generated from the document chunks, allowing for fast, persistent (for NIST AI RMF), and temporary (for custom uploads) similarity search.
* **[Groq API](https://groq.com/):** Powers the Large Language Model (LLM) inference. By utilizing Groq's LPU (Language Processing Unit) inference engine, the application achieves lightning-fast reasoning and response generation based on the retrieved context.
* **[Streamlit](https://streamlit.io/):** Serves as the frontend framework, delivering an interactive and responsive web application deployed via the cloud.

---

## 📁 Repository Structure

The core deployment files for the application are located in the `app_cloud` directory. 

```text
agentic-ai-auditor/
├── app_cloud/               # Streamlit application and cloud deployment files
│   ├── app.py               # Main Streamlit application script
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Example environment variables (if applicable)
│   └── ...                  
├── ...
