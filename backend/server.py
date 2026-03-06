from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict
import uuid
from datetime import datetime, timezone
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import io

# Load env
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe
stripe_api_key = os.environ['STRIPE_API_KEY']

# FastAPI
app = FastAPI()
api_router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)

# ===== MODELS =====
class QuizAnswers(BaseModel):
    age: int
    weight: float
    height: int
    gender: str
    goal: str
    training_days: int
    equipment: str
    dietary_preference: str
    experience_level: str
    sleep_hours: str
    injuries: Optional[str] = ""

class QuizResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    answers: QuizAnswers
    calories: int
    protein: int
    carbs: int
    fats: int
    training_plan: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CalculationResult(BaseModel):
    quiz_id: str
    calories: int
    protein: int
    carbs: int
    fats: int
    training_plan: str
    bmr: int
    tdee: int

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

def calculate_macros(answers: QuizAnswers) -> CalculationResult:
    bmr = calculate_bmr(answers.weight, answers.height, answers.age, answers.gender)
    tdee = calculate_tdee(bmr, answers.training_days)
    
    goal_adjustments = {"lose_fat": -500, "gain_muscle": 300, "recomposition": -200}
    calories = tdee + goal_adjustments.get(answers.goal, 0)
    
    protein_per_kg = {"gain_muscle": 2.0, "lose_fat": 2.2, "recomposition": 2.0}.get(answers.goal, 2.0)
    protein = answers.weight * protein_per_kg
    if answers.dietary_preference == "vegetarian":
        protein *= 0.95
    protein = int(protein)
    
    fats = int((calories * 0.25) / 9)
    carbs = int((calories - (protein * 4) - (fats * 9)) / 4)
    
    training_plan = get_training_plan(answers.training_days, answers.experience_level)
    
    return CalculationResult(
        quiz_id="",
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
        training_plan=training_plan,
        bmr=bmr,
        tdee=tdee
    )

def get_training_plan(training_days: int, experience: str) -> str:
    if training_days >= 6:
        return "6-day Bro Split: Chest, Back, Shoulders, Biceps, Triceps, Legs + Active Rest"
    elif training_days == 5:
        return "5-day Bro Split: Chest, Back, Shoulders, Arms (Bi+Tri), Legs"
    elif training_days == 4:
        return "4-day Modified Split: Chest+Biceps, Back+Triceps, Shoulders, Legs"
    else:
        return "3-day Full Body: Upper Push/Pull, Lower, Full Body"

# ===== ROUTES =====
@api_router.post("/quiz/submit")
async def submit_quiz(answers: QuizAnswers):
    try:
        quiz_data = QuizResponse(answers=answers, calories=0, protein=0, carbs=0, fats=0, training_plan="")
        result = calculate_macros(answers)
        quiz_data.calories = result.calories
        quiz_data.protein = result.protein
        quiz_data.carbs = result.carbs
        quiz_data.fats = result.fats
        quiz_data.training_plan = result.training_plan
        doc = quiz_data.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.quiz_responses.insert_one(doc)
        return {
            "quiz_id": quiz_data.id,
            "calories": result.calories,
            "protein": result.protein,
            "carbs": result.carbs,
            "fats": result.fats,
            "training_plan": result.training_plan,
            "bmr": result.bmr,
            "tdee": result.tdee
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== FREE PREVIEW ROUTE =====
@api_router.post("/quiz/free_preview")
async def free_preview(answers: QuizAnswers):
    """Return only calories and protein for free users."""
    try:
        result = calculate_macros(answers)
        return {
            "calories": result.calories,
            "protein": result.protein
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic root
@api_router.get("/")
async def root():
    return {"message": "PROTOCOL API Ready"}

# Register router & CORS
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
