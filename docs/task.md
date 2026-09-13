# IP-SAKTI Sahayak — Task Tracker

## Phase 1: Project Scaffolding
- [x] Backend: FastAPI project structure + requirements.txt
- [ ] Frontend: Next.js project initialization
- [ ] Root: .env.example, README.md, docker-compose.yml

## Phase 2: Backend Core
- [x] `app/core/config.py` — Environment config
- [x] `app/core/prompts.py` — System prompts
- [x] `app/models/schemas.py` — Pydantic models
- [x] `app/services/embedding_service.py` — Gemini embeddings
- [x] `app/services/llm_service.py` — Gemini LLM client
- [x] `app/services/rag_service.py` — RAG pipeline
- [x] `app/services/citation_service.py` — Citation extraction
- [x] `app/services/classifier_service.py` — Formulation classifier
- [x] `app/ingestion/ingest.py` — Corpus ingestion pipeline
- [x] `app/main.py` — FastAPI app entry point

## Phase 3: Legal Corpus
- [x] India: Patents Act, Biodiversity Act, D&C Act, GI Act, Trade Marks, TKDL, etc.
- [x] International: TRIPS, CBD, Nagoya, WIPO GRATK, PCT, Madrid, etc.

## Phase 4: API Routes
- [x] `POST /api/chat` — Main RAG query
- [x] `POST /api/chat/stream` — Streaming variant
- [x] `POST /api/classify` — Formulation classification
- [x] `GET /api/sources` — Corpus listing
- [x] `GET /api/health` — Health check

## Phase 5: Frontend
- [x] Design system (globals.css)
- [x] Layout + Header + Footer
- [x] Landing page
- [x] Chat interface with jurisdiction toggle
- [x] Citation panel + source viewer
- [x] Formulation classifier wizard
- [x] Confidence badge + disclaimer banner
- [x] Responsive design + animations

## Phase 6: Integration & Polish
- [x] Docker Compose setup
- [x] End-to-end testing
- [x] README with setup instructions
