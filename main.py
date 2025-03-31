from fastapi import FastAPI, Query, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import pandas as pd
import json
import os
import pdfplumber  # Better PDF processing

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

# Function to process different file types
async def process_file(file: UploadFile):
    file_content = ""
    file_extension = file.filename.split(".")[-1].lower()

    try:
        content = await file.read()

        if file_extension == "txt":
            file_content = content.decode("utf-8")
        elif file_extension == "csv":
            try:
                df = pd.read_csv(file.file)
                file_content = df.to_string()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid CSV format")
        elif file_extension == "json":
            try:
                data = json.loads(content.decode("utf-8"))
                file_content = json.dumps(data, indent=2)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file")
        elif file_extension == "pdf":
            try:
                with pdfplumber.open(file.file) as pdf:
                    file_content = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            except Exception:
                raise HTTPException(status_code=400, detail="Error reading PDF file")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Allowed: TXT, CSV, JSON, PDF.")

        return file_content[:5000]  # Limit content size to prevent API overload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ✅ GET Request Support
@app.get("/api/")
async def answer_question_get(question: str = Query(..., description="Your question")):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(question)
        return {"question": question, "answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# ✅ POST Request Support (With File Upload)
@app.post("/api/")
async def answer_question_post(question: str = Form(...), file: UploadFile = File(None)):
    try:
        file_content = await process_file(file) if file else ""

        # Combine question and file content
        input_prompt = f"Question: {question}\nFile Content: {file_content}"

        # Call Gemini API
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(input_prompt)

        return {"question": question, "answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

# Home route to check if API is running
@app.get("/")
async def home():
    return {"message": "Welcome to the LLM API! Use GET or POST on /api/ to ask questions and upload files."}
