# IP-SAKTI Sahayak — Project Walkthrough

The Core MVP for IP-SAKTI Sahayak has been successfully built! This solution provides a robust, RAG-based AI assistant tailored for the Ayurvedic IP and regulatory landscape.

## 🏗️ Architecture & Stack

- **Frontend**: Next.js 14 with App Router, featuring a glassmorphism-inspired "premium" design using Vanilla CSS.
- **Backend**: Python FastAPI with modular services for LLM generation, RAG retrieval, citation extraction, and formulation classification.
- **AI Models**: Google Gemini API (`gemini-1.5-flash` for chat, `text-embedding-004` for vector embeddings).
- **Vector Database**: ChromaDB (persistent local storage for the curated legal corpus).

## 🚀 Key Features Implemented

### 1. Jurisdiction-Aware RAG Engine
The backend explicitly separates Indian national law from international treaties. The frontend features a prominent **Jurisdiction Toggle** (🇮🇳 India / 🌍 International) that dictates the context retrieval and system prompting, preventing dangerous legal conflations.

### 2. Intelligent Formulation Classifier
The `/classify` route provides a multi-turn, wizard-like interface where the user describes their product. The LLM asks clarifying questions to determine which of the 6 regulatory pathways applies:
- Classical/Generic Medicine
- Patent/Proprietary Medicine
- New Drug / Non-classical
- Phytopharmaceutical
- Ayurveda-Aahar / Nutraceutical
- Cosmetic

It then outputs a rich result card detailing the **Regulatory Requirements**, **IP Implications**, **ABS Compliance**, and **Relevant Statutes**.

### 3. Citation Grounding & Confidence
Every RAG chat response strictly cites its sources based on the retrieved context. A custom `CitationService` parses the LLM output and validates it against known statutes (e.g., *Patents Act, 1970 — Section 3(p)*), rendering them in the UI with color-coded **Confidence Badges** (High/Medium/Low).

### 4. Curated Legal Corpus
The system includes a dedicated `corpus/` directory with version-tracked Markdown files for key legislation, including:
- Patents Act 1970
- Biological Diversity Act 2002
- Drugs and Cosmetics Act 1940
- TKDL Overview
- TRIPS Agreement
- Nagoya Protocol
- WIPO GRATK Treaty 2024

On startup, the FastAPI app automatically ingests any new/updated corpus documents into ChromaDB.

## 💻 Running the Application

### Local Development

**1. Start the Backend:**
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*(On first run, the backend will parse the Markdown corpus, generate embeddings via Gemini, and build the ChromaDB vector store.)*

**2. Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment
The project is fully containerized and ready for cloud deployment:
```bash
docker-compose up --build -d
```

## 🎨 Design Highlights
- **Ayurvedic Aesthetics**: The UI uses a deep dark mode background with Saffron (`#D4A843`) and Deep Green (`#2D5F3E`) gradients, reflecting Ayurvedic heritage in a modern tech context.
- **Glassmorphism**: Cards and panels use blurred, semi-transparent backgrounds for a premium feel.
- **Dynamic Interactions**: Smooth micro-animations on buttons, chat bubbles, and the classification wizard.

## 🔮 Next Steps for Phase 2
- **Bhashini Integration**: Connect the Bhashini API for Hindi/regional language support in the UI and chat.
- **Knowledge Graph**: Transition from pure vector search to a Neo4j knowledge graph for complex multi-hop reasoning.
- **Live Registry Connectors**: Integrate live API calls to IP India (InPASS) or CTRI databases.
