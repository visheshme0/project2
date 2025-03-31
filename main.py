from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import pandas as pd
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

@app.get("/")
async def home():
    return {"message": "Welcome to the LLM API! Use the /api/ endpoint to ask questions."}

@app.post("/api/")
async def answer_question(question: str = Form(...), file: UploadFile = File(None)):
    try:
        file_content = ""
        
        if file:
            file_extension = file.filename.split(".")[-1]
            
            # Read file content
            content = await file.read()
            
            if file_extension == "txt":
                file_content = content.decode("utf-8")
            elif file_extension == "csv":
                df = pd.read_csv(file.file)
                file_content = df.to_string()  # Convert CSV content to a string
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Only TXT and CSV are allowed.")
        
        # Combine question with file content
        input_prompt = f"Question: {question}\nFile Content: {file_content}"
        
        # Call Gemini API
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(input_prompt)

        return {"question": question, "answer": response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")
