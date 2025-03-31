from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Load Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# CORS Middleware (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "Welcome to the LLM API! Use the /api/ endpoint to ask questions."}

@app.post("/api/")
async def answer_question(question: str = Form(...), file: UploadFile = File(None)):
    try:
        # If a file is uploaded, process it (currently not implemented)
        if file:
            file_content = await file.read()

        # Call Gemini API for an answer
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(question)

        return {"question": question, "answer": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")
