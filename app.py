import os
import time
import streamlit as st
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. MODERN ARCHITECTURE IMPORTS 
# (Strict alignment with langchain v1.2.12+)
# ==========================================
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import TextLoader

# ==========================================
# 2. DATA SCHEMAS (Pydantic v2.12.5 Contract)
# ==========================================
class BANTAnalysis(BaseModel):
    budget: str = Field(description="Budget details mentioned, including specific numbers, or 'Not explicitly mentioned'")
    authority: str = Field(description="Who is the decision maker and what is the speaker's role?")
    need: str = Field(description="What is the core business pain point or problem?")
    timeline: str = Field(description="When does the client need this implemented or purchased?")

class CRMStructure(BaseModel):
    executive_summary: str = Field(description="A strict 3-sentence summary of the call.")
    action_items: List[str] = Field(description="A list of specific next steps and who owns them.")
    bant: BANTAnalysis = Field(description="BANT qualification framework analysis.")

# ==========================================
# 3. SYSTEM ARCHITECTURE
# ==========================================
class GTMAssistant:
    def __init__(self, api_key: str):
        os.environ["GOOGLE_API_KEY"] = api_key
        # Initialize Gemini with strict parameters for data extraction

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_store = None

    def initialize_knowledge_base(self, file_path: str):
        """Loads and embeds company data into the FAISS vector database."""
        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(docs, self.embeddings)

    def process_transcript(self, transcript_text: str) -> CRMStructure:
        """Orchestrates the retrieval and structured generation pipeline."""
        if not self.vector_store:
            raise ValueError("Knowledge base not initialized.")

        # 1. Retrieve context
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})
        relevant_docs = retriever.invoke(transcript_text)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # 2. Construct the core prompt
        prompt_template = """
        You are an elite Sales Operations Assistant. Your job is to extract CRM data from raw sales transcripts.
        
        Company Product Context (Use this to verify facts/pricing):
        {context}
        
        Raw Sales Transcript:
        {transcript}
        
        Analyze the transcript and extract the requested CRM data structures. Be highly precise.
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "transcript"])
        
        # 3. Enforce structured output via Pydantic integration
        structured_llm = self.llm.with_structured_output(CRMStructure)
        chain = prompt | structured_llm
        
        return chain.invoke({"context": context, "transcript": transcript_text})

def mock_crm_push(payload: CRMStructure):
    """Simulates a network call to Salesforce/HubSpot API."""
    time.sleep(1.5) 
    return True

# ==========================================
# 4. PRESENTATION LAYER (Streamlit v1.51.0)
# ==========================================
st.set_page_config(page_title="GTM Workflow Assistant", layout="wide")
st.title("⚡ AI GTM Workflow Assistant")
st.markdown("Transform raw sales calls into structured, CRM-ready data.")

# Sidebar configuration
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

if api_key:
    assistant = GTMAssistant(api_key=api_key)
    
    # Initialize the Knowledge Base silently
    with st.spinner("Initializing Product Vector Database..."):
        if os.path.exists("data/product_context.txt"):
            assistant.initialize_knowledge_base("data/product_context.txt")
        else:
            st.error("Fatal Error: Missing 'data/product_context.txt'. Ensure your directory structure is correct.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Raw Call Transcript")
        
        default_transcript = ""
        if os.path.exists("data/sample_transcript.txt"):
            with open("data/sample_transcript.txt", "r") as f:
                default_transcript = f.read()
                
        transcript_input = st.text_area("Paste Transcript Here", value=default_transcript, height=400)
        
        process_button = st.button("Analyze & Extract Data", type="primary")

    with col2:
        st.subheader("Structured CRM Output")
        
        if process_button and transcript_input:
            with st.spinner("Analyzing transcript and mapping to product context..."):
                try:
                    result = assistant.process_transcript(transcript_input)
                    st.session_state['crm_data'] = result
                    
                    st.success("Extraction Complete")
                    st.markdown(f"**Executive Summary:**\n{result.executive_summary}")
                    
                    st.markdown("**Action Items:**")
                    for item in result.action_items:
                        st.markdown(f"- {item}")
                        
                    st.markdown("**BANT Analysis:**")
                    st.json({
                        "Budget": result.bant.budget,
                        "Authority": result.bant.authority,
                        "Need": result.bant.need,
                        "Timeline": result.bant.timeline
                    })
                    
                except Exception as e:
                    st.error(f"Processing Error: {str(e)}")

        # State persistence for the mock API push
        if 'crm_data' in st.session_state:
            st.divider()
            if st.button("Push to Salesforce (Mock API)"):
                with st.spinner("Syncing with CRM..."):
                    success = mock_crm_push(st.session_state['crm_data'])
                    if success:
                        st.toast("Successfully synced to Salesforce Contact ID: 0038W00001QwErT", icon="✅")
                        st.success("Data pushed successfully. Workflow complete.")
else:
    st.warning("System locked. Please enter your Gemini API Key in the sidebar to begin.")