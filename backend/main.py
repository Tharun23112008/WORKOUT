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

# QUIZ SUBMISSION (THIS IS WHAT YOUR FRONTEND NEEDS)
@app.post("/api/payment/submit")
def submit_quiz(data: dict):
    return {
        "quiz_id": "demo123",
        "message": "Quiz submitted successfully"
    }

@app.get("/api/checkout/status/{session_id}")
def checkout_status(session_id: str):
    return {
        "payment_status": "paid",
        "status": "complete",
        "metadata": {
            "quiz_id": "demo123"
        }
    }

@app.get("/api/pdf/download/{quiz_id}")
def download_pdf(quiz_id: str):
    return {"message": f"PDF for quiz {quiz_id} will be downloaded here"}
