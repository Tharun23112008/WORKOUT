from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Workout API",
    version="0.1.0"
)

# Allow frontend
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


# CALORIE + PROTEIN CALCULATOR
def calculate_results(data):

    weight = float(data.get("weight", 70))
    height = float(data.get("height", 170))
    age = int(data.get("age", 25))
    gender = data.get("gender", "male")
    goal = data.get("goal", "maintain")
    training_days = int(data.get("training_days", 3))

    # BMR
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # activity multiplier
    if training_days <= 2:
        activity = 1.375
    elif training_days <= 4:
        activity = 1.55
    else:
        activity = 1.725

    tdee = bmr * activity

    # goal adjustment
    if goal == "lose_fat":
        calories = tdee - 400
    elif goal == "gain_muscle":
        calories = tdee + 300
    else:
        calories = tdee

    # protein
    protein = weight * 2

    return int(calories), int(protein)


@app.post("/api/quiz/submit")
async def submit_quiz(data: dict):

    calories, protein = calculate_results(data)

    return {
        "quiz_id": "demo123",
        "calories": calories,
        "protein": protein,
        "training_plan": "Push Pull Legs Split"
    }


@app.post("/api/payment/submit")
async def submit_payment(data: dict):
    return {
        "checkout_url": "https://example-payment-link.com",
        "status": "payment_started"
    }


@app.get("/api/checkout/status/{session_id}")
async def checkout_status(session_id: str):
    return {
        "payment_status": "paid",
        "status": "complete",
        "metadata": {
            "quiz_id": "demo123"
        }
    }


@app.get("/api/pdf/download/{quiz_id}")
async def download_pdf(quiz_id: str):
    return {
        "message": f"PDF for quiz {quiz_id} will be downloaded here"
    }
