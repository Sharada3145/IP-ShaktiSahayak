# IP-SAKTI Sahayak

A multilingual, RAG-based AI assistant for Intellectual Property (IP) and regulatory guidance in Ayurveda, across national (India) and international regimes.

## Overview
IP-SAKTI Sahayak helps AYUSH practitioners, researchers, MSMEs, and startups navigate overlapping regimes:
- Patents, geographical indications (GI), trademarks, trade secrets
- Access-and-Benefit-Sharing (ABS) duties under the Biological Diversity Act
- Drug-regulatory frameworks (Classical vs Proprietary, New Drugs, Phytopharmaceuticals)

## Architecture
- **Frontend**: Next.js 14, React, Vanilla CSS
- **Backend**: Python 3.11+, FastAPI
- **LLM/Embeddings**: Google Gemini API (`gemini-1.5-flash` / `text-embedding-004`)
- **Vector Database**: ChromaDB

## Features
- **Jurisdiction-Aware RAG Chat**: Strict separation between Indian national law and International treaties.
- **Formulation Classifier**: Step-by-step wizard to determine regulatory category and IP implications.
- **Citation Grounding**: Every claim is cited with specific statute/section and confidence indicator.
- **Safe Abstention**: Graceful fallback when the knowledge base lacks sufficient context.

## Local Setup

### 1. Prerequisites
- Node.js 18+
- Python 3.11+
- Google Gemini API Key

### 2. Environment Variables
Copy `.env.example` to `.env` in the root directory and add your API key.

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# Run the API server (will automatically ingest the corpus on first startup)
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

## Docker Deployment
```bash
docker-compose up --build -d
```
