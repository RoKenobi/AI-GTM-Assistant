# ⚡ AI GTM Workflow Assistant

A lightweight, internal Go-To-Market (GTM) tool designed to reduce manual sales administration by transforming raw sales call transcripts into structured, CRM-ready data.

## 📖 The Business Problem
Sales and Revenue teams lose countless hours to CRM hygiene. After every client call, representatives must manually synthesize messy conversations, identify key action items, and qualify the lead based on standard frameworks (BANT). This manual data entry creates bottlenecks, inconsistencies in CRM data, and takes time away from actual selling.

## 🎯 The Solution
This application automates the post-call workflow. It utilizes a Retrieval-Augmented Generation (RAG) architecture to cross-reference raw sales transcripts against internal product documentation, ensuring accurate, hallucination-free data extraction. 

The system processes the input and outputs a strict JSON schema containing an executive summary, action items, and a completed BANT analysis, ready to be pushed to Salesforce or HubSpot.

## ⚙️ Technical Architecture & Stack
- **Orchestration:** LangChain v1.x
- **LLM:** Google Gemini 2.0 Flash (Optimized for structured JSON extraction)
- **Vector Database:** FAISS (Facebook AI Similarity Search) for high-speed, local context retrieval
- **Data Validation:** Pydantic v2 (Enforcing strict schema output)
- **Frontend:** Streamlit

### Core Capabilities
1. **Context Grounding (RAG):** Uses a local vector store to hold product pricing, tiers, and SLAs. The LLM verifies transcript claims against this truth-source before generating summaries.
2. **BANT Evaluation Engine:** Evaluates the transcript explicitly for **B**udget, **A**uthority, **N**eed, and **T**imeline.
3. **Structured CRM Payload:** Bypasses standard conversational AI output in favor of deterministic, schema-validated JSON formatting.
4. **Mock API Integration:** Simulates network latency and state management for pushing formatted payloads to downstream CRM APIs.

## 🚀 Local Setup & Installation

Ensure you have Python 3.9+ installed.

1. Clone the repository and navigate to the project directory.

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install the required dependencies:
    pip install -r requirements.txt

4. Run the Streamlit application:
    streamlit run app.py

5. Paste your Google Gemini API key into the application sidebar to begin.

## 📂 Project Structure

    gtm-workflow-assistant/
    │
    ├── data/                       
    │   ├── product_context.txt     # RAG knowledge base (Truth Source)
    │   └── sample_transcript.txt   # Test input data
    │
    ├── requirements.txt            # Locked dependencies
    └── app.py                      # Core application and UI logic

## 🧠 Evaluation Metrics
The underlying LLM pipeline is evaluated on its ability to adhere to the Pydantic `CRMStructure` contract. If the model fails to extract a specific BANT criterion (e.g., no budget is discussed), it is strictly instructed to return "Not explicitly mentioned" rather than hallucinating a numeric value, ensuring high data integrity for the CRM database.
