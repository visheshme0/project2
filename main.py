from fastapi import FastAPI, Query, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

app = FastAPI()

# Load Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Enable CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ GET Request Support
@app.get("/api/")
async def answer_question_get(question: str = Query(..., description="Your question")):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use a valid model
        response = model.generate_content(question)
        return {"question": question, "answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")

# ✅ POST Request Support
@app.post("/api/")
async def answer_question_post(question: str = Form(...)):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use a valid model
        response = model.generate_content(question)
        return {"question": question, "answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")

# Home route to check if API is running
@app.get("/")
async def home():
    return {"message": "Welcome to the LLM API! Use GET or POST on /api/ to ask questions."}
