import streamlit as st
import chromadb
import pypdf
import os
from openai import OpenAI
from dotenv import load_dotenv

import pytesseract

if os.path.exists('/usr/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
elif os.path.exists('/opt/homebrew/bin/tesseract'):
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title


load_dotenv()
groq_api_key = st.secrets.get("groq_api_key") or os.getenv("groq_api_key")

import shutil
st.sidebar.write("tesseract path:", shutil.which("tesseract"))


# ---------------------------------------------------------
# UI Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AI Compliance Extractor", layout="wide")
st.title("🛡️ Agentic AI Compliance Extractor")
st.markdown("Extract and verify compliance policies from regulatory PDFs using Vector Search and the Groq API.")

# ---------------------------------------------------------
# Sidebar Settings & Mode Selection
# ---------------------------------------------------------
st.sidebar.header("Configuration")
# groq_api_key = st.sidebar.text_input("Groq API Key", type="password", help="Get a free key from console.groq.com")

db_mode = st.sidebar.radio(
    "Vector Database Source:",
    ("Load Persistent Database", "Upload New PDF")
)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def get_groq_client(api_key):
    """Initialize the OpenAI client pointing to Groq's cloud endpoint."""
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

@st.cache_resource
def load_persistent_db():
    """Connects to a pre-existing ChromaDB folder on the hard drive."""
    db_path = "./chroma_db/nist_ai_rmf"
    if os.path.exists(db_path):
        client = chromadb.PersistentClient(path=db_path)
        try:
            return client.get_collection(name="nist_ai_rmf_full")
        except:
            # Fallback if the folder exists but the collection doesn't
            return client.create_collection(name="nist_ai_rmf_full")
    return None

@st.cache_resource
def process_uploaded_pdf(uploaded_file):
    """Parses a PDF on the fly and stores it in an ephemeral memory database."""
    elements = partition_pdf(
        filename=f"pdf/{uploaded_file.name}", 
        strategy="hi_res" 
    )

    chunks = chunk_by_title(
        elements,
        max_characters=1000, 
        new_after_n_chars=800,
        combine_text_under_n_chars=200
    )
    
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="uploaded_pdf")

    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk.text)
        
        metadata = chunk.metadata.to_dict()
        
        clean_metadata = {k: str(v) for k, v in metadata.items() if v is not None}
        metadatas.append(clean_metadata)
        
        ids.append(f"{uploaded_file.name}_chunk_{i}")
        
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    return collection

# ---------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------
collection = None

if db_mode == "Load Persistent Database":
    collection = load_persistent_db()
    if collection is None:
        st.sidebar.warning("No persistent database found at './chroma_db'.")
    else:
        st.sidebar.success("Persistent Vector Database loaded successfully!")
        
elif db_mode == "Upload New PDF":
    uploaded_file = st.sidebar.file_uploader("Upload Regulatory PDF", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Parsing and chunking PDF into Vector DB..."):
            collection = process_uploaded_pdf(uploaded_file)
        st.sidebar.success("PDF processed and loaded into active memory!")

# ---------------------------------------------------------
# Main Execution Flow
# ---------------------------------------------------------
st.markdown("---")
query_text = st.text_area(
    "What specific compliance policies or rules are you looking for?", 
    placeholder="e.g., 'What are the rules regarding proxy variables and disparate impact?'",
    height=100
)

if st.button("Extract Policies"):
    # Input Validation
    if not groq_api_key:
        st.error("Please enter your Groq API Key in the sidebar to proceed.")
    elif collection is None:
        st.error("Please load a vector database or upload a PDF first.")
    elif not query_text:
        st.warning("Please enter a query in the text box.")
    else:
        # Step 1: Retrieval
        with st.spinner("Searching Vector Database for matching clauses..."):
            results = collection.query(
                query_texts=[query_text], 
                n_results=6
            )
            retrieved_chunks = "\n\n".join(results['documents'][0])
            
        # Step 2: LLM Extraction
        with st.spinner("Extracting and formatting policies via Groq..."):
            extraction_prompt = f"""
            You are an expert Regulatory Compliance Officer. 
            
            User Query:
            {query_text}
            
            Raw Excerpts from Regulatory PDF:
            {retrieved_chunks}
            
            Task: Using ONLY the provided excerpts, extract the specific compliance policies, rules, and mathematical thresholds relevant to the user query.
            Do not include any extra information from your own knowledge.
            Format your response as a clear, highly readable summary using markdown formatting (bullet points, bold text). 
            If the excerpts do not contain the answer, state that explicitly.
            """
            
            try:
                client = get_groq_client(groq_api_key)
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": extraction_prompt}]
                )
                filtered_criteria = response.choices[0].message.content
                
                # Output Results
                st.success("Extraction Complete!")
                st.subheader("Readable Compliance Policies")
                st.markdown(filtered_criteria)
                
                with st.expander("View Raw Retrieved Chunks (For Auditing)"):
                    st.text(retrieved_chunks)
                    
            except Exception as e:
                st.error(f"Error communicating with the Groq API: {e}")