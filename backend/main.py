from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import io
import traceback
import base64
import httpx
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ===== ENV VARS =====
MONGODB_URL = os.environ.get("MONGODB_URL", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "tharunatwork23@gmail.com")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "tharun365admin")

# EmailJS config (HTTP-based, works on Render free tier)
EMAILJS_SERVICE_ID = os.environ.get("EMAILJS_SERVICE_ID", "service_y3p7954")
EMAILJS_ADMIN_TEMPLATE_ID = os.environ.get("EMAILJS_ADMIN_TEMPLATE_ID", "template_dmwir7u")
EMAILJS_PDF_TEMPLATE_ID = os.environ.get("EMAILJS_PDF_TEMPLATE_ID", "template_ecu877b")
EMAILJS_PUBLIC_KEY = os.environ.get("EMAILJS_PUBLIC_KEY", "c3EPeMlWCA9fJbKtq")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== FILE-BASED PERSISTENT STORE =====
import json
from pathlib import Path

STORE_FILE = Path("/tmp/store.json")

def _load_store() -> dict:
    try:
        if STORE_FILE.exists():
            return json.loads(STORE_FILE.read_text())
    except Exception as e:
        print(f"Could not load store: {e}")
    return {}

def _save_store(store: dict):
    try:
        STORE_FILE.write_text(json.dumps(store))
    except Exception as e:
        print(f"Could not save store: {e}")

@app.on_event("startup")
async def startup_db():
    store = _load_store()
    print(f"Server started — store loaded with {len(store)} entries")

async def save_quiz(quiz_id: str, data: dict):
    store = _load_store()
    store[quiz_id] = data
    _save_store(store)

async def get_quiz(quiz_id: str):
    return _load_store().get(quiz_id)

async def save_payment(payment_id: str, data: dict):
    store = _load_store()
    store[f"payment_{payment_id}"] = data
    _save_store(store)

async def get_all_payments():
    store = _load_store()
    return [v for k, v in store.items() if k.startswith("payment_")]

async def update_payment_status(payment_id: str, status: str):
    store = _load_store()
    key = f"payment_{payment_id}"
    if key in store:
        store[key]["status"] = status
        _save_store(store)

# ===== MODELS =====
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

# ===== CALCULATION LOGIC =====
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
    diet = answers.dietary_preference.lower().strip()
    if diet == "vegetarian":
        protein = int(protein * 0.95)
    carbs = int((calories * 0.45) / 4)
    fats = int((calories * 0.25) / 9)
    return {"calories": calories, "protein": protein, "carbs": carbs, "fats": fats}

# ===== PDF GENERATION =====
def generate_pdf(answers, macros, user_email):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    PRIMARY = HexColor("#FF5B9E")
    SECONDARY = HexColor("#34B3D2")
    DARK = HexColor("#0A0A0A")
    GRAY = HexColor("#888888")
    LIGHT_GRAY = HexColor("#F5F5F5")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", fontSize=28, textColor=PRIMARY,
                                  spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("Subtitle", fontSize=12, textColor=GRAY,
                                     spaceAfter=20, alignment=TA_CENTER)
    heading_style = ParagraphStyle("Heading", fontSize=14, textColor=PRIMARY,
                                    spaceAfter=8, fontName="Helvetica-Bold")
    body_style = ParagraphStyle("Body", fontSize=10, textColor=DARK,
                                 spaceAfter=6, leading=16)
    small_style = ParagraphStyle("Small", fontSize=9, textColor=GRAY, spaceAfter=4)

    goal_map = {"gain_muscle": "Gain Muscle", "lose_fat": "Lose Fat", "recomposition": "Recomposition"}
    goal_label = goal_map.get(answers.get("goal", ""), "Custom")
    training_plan = get_training_plan(answers.get("training_days", 4), answers.get("experience_level", "intermediate"))

    story = []
    story.append(Paragraph("365 DAYS OF DISCIPLINE", title_style))
    story.append(Paragraph("Your Personalized Protocol Blueprint", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    story.append(Spacer(1, 16))

    story.append(Paragraph("YOUR STATS", heading_style))
    stats_data = [
        ["Age", f"{answers.get('age')} years", "Weight", f"{answers.get('weight')} kg"],
        ["Height", f"{answers.get('height')} cm", "Gender", answers.get('gender', '').capitalize()],
        ["Goal", goal_label, "Training Days", f"{answers.get('training_days')} days/week"],
        ["Experience", answers.get('experience_level', '').capitalize(), "Diet", answers.get('dietary_preference', '').capitalize()],
    ]
    stats_table = Table(stats_data, colWidths=[80, 120, 80, 120])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (0, -1), PRIMARY),
        ('TEXTCOLOR', (2, 0), (2, -1), PRIMARY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT_GRAY, white]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#EEEEEE")),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("DAILY NUTRITION TARGETS", heading_style))
    nutrition_data = [
        ["CALORIES", "PROTEIN", "CARBS", "FATS"],
        [f"{macros['calories']} kcal", f"{macros['protein']}g", f"{macros['carbs']}g", f"{macros['fats']}g"],
    ]
    nutrition_table = Table(nutrition_data, colWidths=[118, 118, 118, 118])
    nutrition_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, 1), LIGHT_GRAY),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 16),
        ('TEXTCOLOR', (0, 1), (-1, 1), DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#EEEEEE")),
    ]))
    story.append(nutrition_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("YOUR TRAINING STRUCTURE", heading_style))
    story.append(Paragraph(f"<b>{training_plan}</b>", body_style))
    story.append(Spacer(1, 8))

    workout_split = {
        6: [
            ("Monday", "CHEST", "Bench Press 4x8, Incline DB Press 3x10, Cable Flyes 3x12, Push-Ups 2x15"),
            ("Tuesday", "BACK", "Deadlift 4x6, Pull-Ups 3x8, Barbell Row 3x10, Lat Pulldown 3x12"),
            ("Wednesday", "SHOULDERS", "OHP 4x8, Lateral Raises 4x12, Front Raises 3x12, Face Pulls 3x15"),
            ("Thursday", "BICEPS", "Barbell Curl 4x10, Hammer Curl 3x12, Incline DB Curl 3x12, Cable Curl 2x15"),
            ("Friday", "TRICEPS", "Skull Crushers 4x10, Tricep Dips 3x10, Pushdowns 3x12, Overhead Extension 3x12"),
            ("Saturday", "LEGS", "Squat 4x8, Romanian Deadlift 3x10, Leg Press 3x12, Calf Raises 4x15"),
            ("Sunday", "REST", "Active recovery: 20-30 min walk or stretching"),
        ],
        5: [
            ("Monday", "PUSH", "Bench Press 4x8, OHP 3x10, Lateral Raises 3x12, Tricep Pushdowns 3x12"),
            ("Tuesday", "PULL", "Deadlift 4x6, Pull-Ups 3x8, Barbell Row 3x10, Bicep Curls 3x12"),
            ("Wednesday", "LEGS", "Squat 4x8, Leg Press 3x12, Romanian Deadlift 3x10, Calf Raises 4x15"),
            ("Thursday", "UPPER", "Incline Press 4x10, DB Row 3x10, Shoulder Press 3x10, Curls 3x12"),
            ("Friday", "LOWER", "Front Squat 4x8, Hip Thrust 3x12, Leg Curl 3x12, Calf Raises 4x15"),
            ("Saturday", "REST", "Active recovery or cardio 20-30 min"),
            ("Sunday", "REST", "Full rest day"),
        ],
        4: [
            ("Monday", "UPPER A", "Bench Press 4x8, Row 4x8, OHP 3x10, Curl 3x12"),
            ("Tuesday", "LOWER A", "Squat 4x8, Romanian Deadlift 3x10, Leg Press 3x12, Calf Raises 4x15"),
            ("Wednesday", "REST", "Active recovery"),
            ("Thursday", "UPPER B", "Incline Press 4x10, Pull-Ups 3x8, Lateral Raises 3x12, Triceps 3x12"),
            ("Friday", "LOWER B", "Deadlift 4x6, Front Squat 3x8, Leg Curl 3x12, Hip Thrust 3x12"),
            ("Saturday", "REST", "Rest or light cardio"),
            ("Sunday", "REST", "Full rest day"),
        ],
        3: [
            ("Monday", "FULL BODY A", "Squat 3x8, Bench Press 3x8, Row 3x8, OHP 3x10, Curl 3x12"),
            ("Wednesday", "FULL BODY B", "Deadlift 3x6, Incline Press 3x10, Pull-Ups 3x8, Dips 3x10"),
            ("Friday", "FULL BODY C", "Front Squat 3x8, DB Press 3x10, Cable Row 3x12, Lateral Raises 3x12"),
        ],
    }

    split = workout_split.get(answers.get("training_days", 4), workout_split[4])
    workout_data = [["DAY", "FOCUS", "EXERCISES"]]
    for day, focus, exercises in split:
        workout_data.append([day, focus, exercises])

    workout_table = Table(workout_data, colWidths=[70, 80, 322])
    workout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('TEXTCOLOR', (0, 1), (0, -1), PRIMARY),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, -1), SECONDARY),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#EEEEEE")),
    ]))
    story.append(workout_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("NUTRITION GUIDE", heading_style))
    diet = answers.get("dietary_preference", "non_vegetarian").lower().strip()
    if diet in ("eggetarian", "eggitarian"):
        diet = "eggetarian"

    if diet == "vegetarian":
        meal_examples = [
            ("Breakfast", f"~{int(macros['calories']*0.25)} kcal", "Paneer bhurji with whole wheat roti + milk"),
            ("Lunch", f"~{int(macros['calories']*0.35)} kcal", "Dal + rice + curd + sabzi + salad"),
            ("Pre-workout", f"~{int(macros['calories']*0.10)} kcal", "Banana + peanut butter"),
            ("Post-workout", f"~{int(macros['calories']*0.15)} kcal", "Whey protein shake + fruits"),
            ("Dinner", f"~{int(macros['calories']*0.20)} kcal", "Tofu stir fry + quinoa/roti + vegetables"),
            ("Before bed", f"~{int(macros['calories']*0.05)} kcal", "Cottage cheese (paneer) or Greek yogurt"),
        ]
    elif diet == "eggetarian":
        meal_examples = [
            ("Breakfast", f"~{int(macros['calories']*0.25)} kcal", "4 eggs (2 whole + 2 whites) + oats + fruit"),
            ("Lunch", f"~{int(macros['calories']*0.35)} kcal", "Rice + dal + egg curry + salad"),
            ("Pre-workout", f"~{int(macros['calories']*0.10)} kcal", "Banana + boiled eggs"),
            ("Post-workout", f"~{int(macros['calories']*0.15)} kcal", "Whey protein + fruits"),
            ("Dinner", f"~{int(macros['calories']*0.20)} kcal", "Egg omelette + roti + vegetables"),
            ("Before bed", f"~{int(macros['calories']*0.05)} kcal", "Greek yogurt or cottage cheese"),
        ]
    else:
        meal_examples = [
            ("Breakfast", f"~{int(macros['calories']*0.25)} kcal", "Eggs + oats + fruit + milk"),
            ("Lunch", f"~{int(macros['calories']*0.35)} kcal", "Rice + chicken curry + dal + salad"),
            ("Pre-workout", f"~{int(macros['calories']*0.10)} kcal", "Banana + peanut butter"),
            ("Post-workout", f"~{int(macros['calories']*0.15)} kcal", "Whey protein shake + fruits"),
            ("Dinner", f"~{int(macros['calories']*0.20)} kcal", "Grilled chicken/fish + roti + vegetables"),
            ("Before bed", f"~{int(macros['calories']*0.05)} kcal", "Greek yogurt or cottage cheese"),
        ]

    meal_data = [["MEAL", "CALORIES", "EXAMPLE"]]
    for meal, cals, example in meal_examples:
        meal_data.append([meal, cals, example])

    meal_table = Table(meal_data, colWidths=[90, 80, 302])
    meal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('TEXTCOLOR', (0, 1), (0, -1), PRIMARY),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#EEEEEE")),
    ]))
    story.append(meal_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("RECOVERY PROTOCOL", heading_style))
    for item in [
        "Sleep 7-9 hours every night — this is non-negotiable for muscle growth",
        "Drink 3-4 litres of water daily — more on training days",
        "On rest days: 20-30 min walk + full body stretching",
        "Deload every 8-10 weeks — reduce weight by 40% for one week",
        "Avoid alcohol — it directly impairs protein synthesis and recovery",
        "Creatine monohydrate 5g/day is the only supplement worth taking",
    ]:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("THE 365 DISCIPLINE RULES", heading_style))
    for i, rule in enumerate([
        "Never miss a Monday — momentum starts the week",
        "Track your food for at least the first 4 weeks",
        "Progressive overload: add weight or reps every week",
        "Do not change the program for at least 12 weeks",
        "Consistency beats intensity — showing up matters more than perfect workouts",
        "Take progress photos every 4 weeks — the mirror lies, photos don't",
    ], 1):
        story.append(Paragraph(f"{i}. {rule}", body_style))
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"Generated for: {user_email} | Date: {datetime.now().strftime('%d %b %Y')} | 365 Days of Discipline",
        small_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


async def send_emailjs(template_params: dict, template_id: str = None):
    """Send email via EmailJS HTTP API — works on Render free tier."""
    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": template_id or EMAILJS_ADMIN_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": template_params
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.emailjs.com/api/v1.0/email/send",
            json=payload
        )
        if resp.status_code != 200:
            raise Exception(f"EmailJS error {resp.status_code}: {resp.text}")
    print(f"✅ EmailJS sent to {template_params.get('to_email') or template_params.get('customer_email')}")


async def send_pdf_email(email: str, quiz_data: dict):
    """Send PDF to customer as base64 attachment via EmailJS."""
    pdf_buffer = generate_pdf(quiz_data["answers"], quiz_data["macros"], email)
    pdf_b64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    m = quiz_data["macros"]
    await send_emailjs({
        "to_email": email,
        "to_name": email.split("@")[0],
        "calories": str(m["calories"]),
        "protein": str(m["protein"]),
        "carbs": str(m["carbs"]),
        "fats": str(m["fats"]),
        "training_plan": quiz_data.get("training_plan", ""),
        "pdf_content": pdf_b64,
    }, template_id=EMAILJS_PDF_TEMPLATE_ID)


# ===== ROUTES =====
@app.get("/")
async def root():
    return {"message": "365 Days of Discipline API Ready"}

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "emailjs_configured": bool(EMAILJS_PUBLIC_KEY),
        "mongodb_configured": bool(MONGODB_URL)
    }

@app.post("/api/quiz/submit", response_model=QuizResponse)
async def submit_quiz(answers: QuizAnswers):
    try:
        print(f"📥 Received: age={answers.age} weight={answers.weight} gender={answers.gender} goal={answers.goal} days={answers.training_days} diet={answers.dietary_preference}")
        try:
            macros = calculate_macros(answers)
            print(f"✅ Macros: {macros}")
        except Exception as e:
            print(f"❌ CRASH in calculate_macros: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Macro calculation failed: {str(e)}")

        quiz_id = str(uuid.uuid4())
        training_plan = get_training_plan(answers.training_days, answers.experience_level)
        data = {
            "answers": answers.dict(),
            "macros": macros,
            "training_plan": training_plan,
            "created_at": datetime.now().isoformat()
        }
        try:
            await save_quiz(quiz_id, data)
            print(f"✅ Quiz saved: {quiz_id}")
        except Exception as e:
            print(f"❌ CRASH in save_quiz: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

        print(f"✅ Done — quiz_id={quiz_id}")
        return QuizResponse(
            quiz_id=quiz_id,
            calories=macros["calories"],
            protein=macros["protein"],
            training_plan=training_plan
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ UNEXPECTED: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/payment/submit")
async def submit_payment(
    quiz_id: str = Form(...),
    email: str = Form(...),
    screenshot: UploadFile = File(...)
):
    try:
        if screenshot.content_type and not screenshot.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
        screenshot_data = await screenshot.read()
        if len(screenshot_data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Screenshot too large. Max 10MB.")

        quiz_data = await get_quiz(quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz session not found. Please retake the quiz.")

        payment_id = str(uuid.uuid4())
        payment_record = {
            "payment_id": payment_id,
            "quiz_id": quiz_id,
            "email": email,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
            "quiz_data": quiz_data
        }
        await save_payment(payment_id, payment_record)
        print(f"✅ Payment saved: {payment_id} for {email}")

        try:
            a = quiz_data["answers"]
            m = quiz_data["macros"]
            approve_link = f"https://workout-cwle.onrender.com/api/admin/approve/{payment_id}?secret={ADMIN_SECRET}"
            await send_emailjs({
                "to_email": NOTIFY_EMAIL,
                "customer_email": email,
                "payment_id": payment_id,
                "time": datetime.now().strftime('%d %b %Y %H:%M'),
                "goal": a.get('goal', ''),
                "calories": str(m['calories']),
                "protein": str(m['protein']),
                "approve_link": approve_link,
            })
            print(f"✅ Admin notified at {NOTIFY_EMAIL}")
        except Exception as e:
            print(f"⚠️ Admin email failed (payment still saved): {e}")

        return {
            "status": "success",
            "payment_id": payment_id,
            "message": "Payment submitted. You'll receive your PDF within 24 hours after verification."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ CRASH in submit_payment: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===== ADMIN: VIEW PENDING PAYMENTS =====
@app.get("/api/admin/payments")
async def list_payments(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    payments = await get_all_payments()
    return {"payments": payments}


# ===== ADMIN: APPROVE PAYMENT & SEND PDF =====
@app.get("/api/admin/approve/{payment_id}")
async def approve_payment(payment_id: str, secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")

    store = _load_store()
    payment = store.get(f"payment_{payment_id}")
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.get("status") == "approved":
        return {"status": "already_approved", "message": f"PDF already sent to {payment.get('email')}."}

    email = payment["email"]
    quiz_data = payment.get("quiz_data") or await get_quiz(payment["quiz_id"])
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz data not found. Cannot generate PDF.")

    await update_payment_status(payment_id, "approved")
    try:
        await send_pdf_email(email, quiz_data)
        print(f"✅ PDF sent to {email}")
        return {"status": "success", "message": f"✅ PDF sent to {email} successfully!"}
    except Exception as e:
        await update_payment_status(payment_id, "send_failed")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF send failed: {str(e)}")
