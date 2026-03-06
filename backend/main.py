from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Workout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "API running"}

@app.get("/health")
def health():
    return {"message": "Server is healthy"}


# QUIZ SUBMIT ENDPOINT (THIS FIXES YOUR 404)
@app.post("/api/quiz/submit")
def submit_quiz(data: dict):
    return {
        "quiz_id": "demo123",
        "message": "Quiz submitted successfully"
    }


# PAYMENT STATUS
@app.get("/api/checkout/status/{session_id}")
def checkout_status(session_id: str):
    return {
        "payment_status": "paid",
        "status": "complete",
        "metadata": {
            "quiz_id": "demo123"
        }
    }


# PDF DOWNLOAD
@app.get("/api/pdf/download/{quiz_id}")
def download_pdf(quiz_id: str):
    return {
        "message": f"PDF for quiz {quiz_id} will be downloaded here"
    }
