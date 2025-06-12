# How to Run the Durak Game

## 1. Backend (Python/FastAPI)

1. **Install dependencies** (in your backend directory):
    ```bash
    pip install fastapi uvicorn pydantic
    ```

2. **Start the backend server**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    - The API will be available at `http://127.0.0.1:8000/api`.

## 2. Frontend (React/Vite)

1. **Install dependencies** (in your project root):
    ```bash
    npm install
    ```

2. **Start the frontend dev server**:
    ```bash
    npm run dev
    ```
    - The app will be available at `http://localhost:5173` (or as shown in your terminal).

---

**Note:**  
- You must run both the backend (`uvicorn backend.main:app --reload`) and the frontend (`npm run dev`) for the game to work.
- Bots must be Python files implementing the required interface (see `backend/example_bot.py` for an example).
- If you see security warnings after `npm install`, you can run `npm audit fix` or `npm audit fix --force` to attempt to resolve them. These warnings are common and do not usually affect development, but review them before using in production.
