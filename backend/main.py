from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import smtplib
import os
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

quiz_store = {}

SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "tharunatwork23@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
NOTIFY_EMAIL = "tharunatwork23@gmail.com"

class QuizAnswers(BaseModel):
    age: int
    weight: float
    height: int
    gender: str
    goal: str
    training_days: int
    dietary_preference: str
    experience_level: Optional[str] = "intermediate"
    equipment: Optional[str] = "full_gym"
    sleep_hours: Optional[str] = "7_plus"
    injuries: Optional[str] = ""

class QuizResponse(BaseModel):
    quiz_id: str
    calories: int
    protein: int
    training_plan: str

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return int(10 * weight + 6.25 * height - 5 * age + 5)
    return int(10 * weight + 6.25 * height - 5 * age - 161)

def calculate_tdee(bmr, training_days):
    if training_days <= 2: multiplier = 1.375
    elif training_days <= 4: multiplier = 1.55
    elif training_days <= 5: multiplier = 1.725
    else: multiplier = 1.9
    return int(bmr * multiplier)

def get_training_plan(training_days, experience_level):
    plans = {
        3: "Full Body 3-Day Split (Mon/Wed/Fri)",
        4: "Upper/Lower 4-Day Split",
        5: "Push/Pull/Legs + Upper/Lower",
        6: "Bro Split: Chest/Back/Shoulders/Biceps/Triceps/Legs"
    }
    return plans.get(training_days, "Custom Training Split")

def calculate_macros(answers):
    bmr = calculate_bmr(answers.weight, answers.height, answers.age, answers.gender)
    tdee = calculate_tdee(bmr, answers.training_days)
    goal_adjustments = {"lose_fat": -500, "gain_muscle": 300, "recomposition": -200}
    calories = tdee + goal_adjustments.get(answers.goal, 0)
    protein_per_kg = {"gain_muscle": 2.0, "lose_fat": 2.2, "recomposition": 2.0}.get(answers.goal, 2.0)
    protein = int(answers.weight * protein_per_kg)
    if answers.dietary_preference.lower() == "vegetarian":
        protein = int(protein * 0.95)
    carbs = int((calories * 0.45) / 4)
    fats = int((calories * 0.25) / 9)
    return {"calories": calories, "protein": protein, "carbs": carbs, "fats": fats}

def generate_pdf(answers, macros, user_email):
    buffer = io.BytesIO()
    doc = SimpleDocT
async def download_pdf(quiz_id: str):
    return {
        "message": f"PDF for quiz {quiz_id} will be downloaded here"
    }
