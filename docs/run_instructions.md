# How to Run IP-ShaktiSahayak

This project consists of a FastAPI backend and a Next.js (or React) frontend. Follow these instructions to run the project locally.

## Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- A Google Gemini API key (AI Studio)

---

## 1. Running the Backend

The backend uses FastAPI, ChromaDB for vector storage, and the Google GenAI SDK for LLM and embeddings.

### Setup

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment variables:
   - Copy the `.env.example` file (if available) or create a new `.env` file in the root project folder (or inside the backend folder depending on the config path, typically project root).
   - Add your Gemini API key:
     ```env
     GOOGLE_API_KEY="your_ai_studio_api_key_here"
     ```

### Running the Server

1. **Ingest the Corpus** (Run this once or whenever documents in `backend/corpus/` are updated):
   ```bash
   python -c "from app.ingestion.ingest import run_ingestion; run_ingestion()"
   ```

2. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

The backend will be available at:
- API Base: `http://127.0.0.1:8000`
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

---

## 2. Running the Frontend

The frontend communicates with the backend via the `/api/chat` and other tool endpoints.

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the node dependencies:
   ```bash
   npm install
   ```

3. Configure the environment variables:
   - If there is a `.env` or `.env.local` file in the frontend folder, ensure it points to the local backend URL:
     ```env
     NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
     ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at: `http://localhost:3000`

---

## 3. Running with Docker Compose (Optional)

If the project includes a `docker-compose.yml` file, you can run both services simultaneously using Docker.

1. Ensure your `.env` file is properly configured with your `GOOGLE_API_KEY`.
2. Run the following command from the project root:
   ```bash
   docker-compose up --build
   ```
3. Access the frontend at `http://localhost:3000` and backend at `http://localhost:8000`.
