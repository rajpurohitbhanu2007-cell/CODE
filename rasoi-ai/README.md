# RasoiAI Backend

Multimodal Indian Fridge-to-Recipe & Shopping List Generator powered by FastAPI and Google Gemini Vision.

---

## Quick Start

### 1. Prerequisites
- **Python 3.11+** installed
- **uv** (recommended package manager) or standard `pip`

If `uv` is not installed, install it via:
```powershell
pip install uv
```

### 2. Environment Configuration
Create or update your `.env` file in the project root:
```env
# Gemini API Key (Get free key from https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Set to true to use realistic canned responses without API calls
DEMO_MODE=false

# Port configuration
PORT=8000
```

### 3. Install Dependencies
```powershell
uv sync
```

---

## Running the Server

### Option A: Using the Startup Scripts (Recommended)

- **PowerShell:**
  ```powershell
  .\run.ps1
  ```
- **Command Prompt (CMD):**
  ```cmd
  run.bat
  ```

### Option B: Using `uv run` Directly
```powershell
uv run uvicorn src.rasoi_ai.main:app --reload --host 0.0.0.0 --port 8000
```

### Option C: Using Virtual Environment Directly
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn src.rasoi_ai.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Interactive Endpoints

Once the server is running:
- **Interactive Visual Testbed UI:** [http://localhost:8000/test](http://localhost:8000/test)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health & Status:** [http://localhost:8000/](http://localhost:8000/)

---

## Available API Routes

- `POST /api/detect-ingredients`: Upload a fridge image to detect ingredients using Gemini Vision.
- `POST /api/mock-detect`: Fast mock detection endpoint for frontend development.
- `POST /api/match-recipes`: Match confirmed ingredients against Indian recipe corpus.
- `GET /api/popular-ingredients`: Returns popular pantry ingredients for UI tag suggestions.
- `GET /api/pantry-staples`: Returns basic spices & essentials (Masala Dabba).
