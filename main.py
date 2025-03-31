from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

# Load OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        # If a file is uploaded, process it (not implemented in this basic version)
        if file:
            file_content = await file.read()
            # (Future: process file content if needed)

        # Call OpenAI API for an answer
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )

        return {"question": question, "answer": response["choices"][0]["message"]["content"]}

    except Exception as e:
        return {"error": str(e)}
