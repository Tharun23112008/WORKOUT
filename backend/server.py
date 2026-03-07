from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone

app = FastAPI()

# ===== MODELS =====
class QuizAnswers(BaseModel):
    age: int
    weight: float
    height: int
    gender: str
    goal: str
    training_days: int
    dietary_preference: str

class QuizResponse(BaseModel):
    quiz_id: str
    calories: int
    protein: int

# ===== CALCULATION LOGIC =====
def calculate_bmr(weight: float, height: int, age: int, gender: str) -> int:
    if gender.lower() == "male":
        return int(10 * weight + 6.25 * height - 5 * age + 5)
    return int(10 * weight + 6.25 * height - 5 * age - 161)

def calculate_tdee(bmr: int, training_days: int) -> int:
    if training_days <= 2: multiplier = 1.375
    elif training_days <= 4: multiplier = 1.55
    elif training_days <= 5: multiplier = 1.725
    else: multiplier = 1.9
    return int(bmr * multiplier)

def calculate_macros(answers: QuizAnswers):
    bmr = calculate_bmr(answers.weight, answers.height, answers.age, answers.gender)
    tdee = calculate_tdee(bmr, answers.training_days)

    goal_adjustments = {"lose_fat": -500, "gain_muscle": 300, "recomposition": -200}
    calories = tdee + goal_adjustments.get(answers.goal, 0)

    protein_per_kg = {"gain_muscle": 2.0, "lose_fat": 2.2, "recomposition": 2.0}.get(answers.goal, 2.0)
    protein = int(answers.weight * protein_per_kg)
    if answers.dietary_preference.lower() == "vegetarian":
        protein = int(protein * 0.95)

    return {"calories": calories, "protein": protein}

# ===== ROUTES =====
@app.post("/quiz/submit", response_model=QuizResponse)
async def submit_quiz(answers: QuizAnswers):
    try:
        macros = calculate_macros(answers)
        return QuizResponse(
            quiz_id=str(uuid.uuid4()),
            calories=macros['calories'],
            protein=macros['protein']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API Ready"}
