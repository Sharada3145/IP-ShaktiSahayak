# IP-SAKTI Sahayak — Project Walkthrough (Phase 2)

Welcome to Phase 2 of IP-SAKTI Sahayak! The AI assistant has been significantly expanded to handle two of the most complex areas of Ayurvedic Intellectual Property and Regulatory Compliance.

## 🚀 New Features in Phase 2

### 1. ABS Compliance Helper
The Biological Diversity Act (and its 2023 amendment) imposes strict Access and Benefit-Sharing (ABS) obligations. The new **ABS Compliance Helper** (`/abs-helper`) provides an interactive wizard to determine exact requirements.

- **Dynamic Decision Tree**: Evaluates if the user is an Indian citizen, a foreign entity, or a registered AYUSH practitioner.
- **Exemption Handling**: Accurately handles the 2023 exemptions for codified traditional knowledge and registered practitioners.
- **Clear Guidance**: Outputs whether the user needs **Prior Approval from the NBA** (Form 1, Form 3) or **Prior Intimation to the SBB** (Form A), along with benefit-sharing estimates.

### 2. TKDL Prior-Art Pointer
A critical hurdle for Ayurvedic patents is Section 3(p) of the Patents Act (Traditional Knowledge). Since the official TKDL is closed, we built the **TKDL Prior-Art Pointer** (`/tkdl-check`) using a curated dictionary of common Ayurvedic botanicals.

- **Ingredient Analysis**: Users input a comma-separated list of botanicals (e.g., *Ashwagandha, Brahmi*) and the intended therapeutic use.
- **Mock TK Matching**: The system cross-references these against known classical indications.
- **Risk Assessment**: If a direct match is found (e.g., Turmeric for wound healing), it flags the formulation with a **HIGH Risk** for Section 3(p) rejection.
- **Strategic Advice**: Advises users on whether they need to prove synergism, novel extraction methods, or clinical efficacy to overcome potential objections.

## 🏗️ Technical Updates
- Refactored `backend/app/api/routes/classify.py` into a unified `tools.py` router handling all three specialized wizards (Classify, ABS, TKDL).
- Added `ABSService` and `TKDLService` to the backend logic layer.
- Added `AbsStartRequest`, `TkdlCheckRequest`, and corresponding response models to `schemas.py`.
- Built rich Next.js UI components for both tools, maintaining the dark-mode glassmorphism aesthetic with Saffron and Green accents.

## 💻 Running the Application

Both the new backend routes and frontend pages are seamlessly integrated into the existing stack.

**1. Start the Backend:**
```bash
cd backend
# Make sure your venv is active
uvicorn app.main:app --reload --port 8000
```

**2. Start the Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` — you will now see the new navigation links in the header for **ABS Compliance** and **TKDL Check**.

## 🔮 Next Steps for Phase 3
- **Bhashini Integration**: Connect the Bhashini API for Hindi/regional language translation across the UI and RAG chat.
- **Knowledge Graph**: Transition the RAG engine from pure vector similarity to a Neo4j knowledge graph for complex multi-hop reasoning.
