from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Workout API",
    version="0.1.0"
)

# CORS (allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROOT
@app.get("/")
def root():
    return {"status": "API running"}

# HEALTH CHECK
@app.get("/health")
def health():
    return {"message": "Server is healthy"}

# QUIZ SUBMIT (this is what your frontend needs)
@app.post("/api/quiz/submit")
async def submit_quiz(data: dict):
    """
    Receives quiz answers from frontend
    """
    return {
        "quiz_id": "demo123",
        "message": "Quiz submitted successfully"
    }

# PAYMENT SUBMIT (for checkout)
@app.post("/api/payment/submit")
async def submit_payment(data: dict):
    return {
        "checkout_url": "https://example-payment-link.com",
        "status": "payment_started"
    }

# CHECK PAYMENT STATUS
@app.get("/api/checkout/status/{session_id}")
async def checkout_status(session_id: str):
    return {
        "payment_status": "paid",
        "status": "complete",
        "metadata": {
            "quiz_id": "demo123"
        }
    }

# DOWNLOAD PDF
@app.get("/api/pdf/download/{quiz_id}")
async def download_pdf(quiz_id: str):
    return {
        "message": f"PDF for quiz {quiz_id} will be downloaded here"
    }}
