from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Workout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# folder to store screenshots
UPLOAD_DIR = "payment_screenshots"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "API running"}


@app.get("/health")
def health():
    return {"message": "Server is healthy"}


# Checkout status endpoint (temporary mock)
@app.get("/api/checkout/status/{session_id}")
def checkout_status(session_id: str):
    return {
        "payment_status": "paid",
        "status": "complete",
        "metadata": {
            "quiz_id": "demo123"
        }
    }


# PDF download endpoint (temporary)
@app.get("/api/pdf/download/{quiz_id}")
def download_pdf(quiz_id: str):
    return {"message": f"PDF for quiz {quiz_id} will be downloaded here"}


# Payment screenshot submission
@app.post("/api/payment/submit")
async def submit_payment(
    quiz_id: str = Form(...),
    email: str = Form(...),
    screenshot: UploadFile = File(...)
):
    file_path = f"{UPLOAD_DIR}/{screenshot.filename}"

    with open(file_path, "wb") as f:
        f.write(await screenshot.read())

    return {
        "status": "payment proof received",
        "quiz_id": quiz_id,
        "email": email,
        "filename": screenshot.filename
    }
