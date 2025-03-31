from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openi import OpenAI
import os

app = FastAPI()

# Load OpenAI API key from environment variables
api_key = os.getenv("OPEN_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")

client = openai.OpenAI(api_key=api_key)

# CORS Middleware (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    """
    Home route to check if API is running.
    """
    return {"message": "Welcome to the LLM API! Use the /api/ endpoint to ask questions."}

@app.post("/api/")
async def answer_question(question: str = Form(...), file: UploadFile = File(None)):
    """
    Accepts a question and an optional file, then returns an LLM-generated answer.
    """
    try:
        # If a file is uploaded, process it (currently not implemented)
        if file:
            file_content = await file.read()
            # (Future: process file content if needed)

        # Call OpenAI API for an answer
        client=OpenAI(api_key)
        chat_completion=client.chat.completions.create(
            message=[{"role":"user","content":question}],
            model="gpt-3.5-turbo"
        )
        response=chat_completion


        return {"question": question, "answer": response.choices[0].message.content}

    except openai.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")
