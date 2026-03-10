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

# ===== IN-MEMORY STORE =====
quiz_store = {}

# ===== EMAIL CONFIG =====
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "tharunatwork23@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
NOTIFY_EMAIL = "tharunatwork23@gmail.com"

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
    if answers.dietary_preference.lower() == "vegetarian":
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

    # Header
    story.append(Paragraph("365 DAYS OF DISCIPLINE", title_style))
    story.append(Paragraph("Your Personalized Protocol Blueprint", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY))
    story.append(Spacer(1, 16))

    # Personal Stats
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
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))

    # Daily Targets
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

    # Training Plan
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

    # Nutrition Guide
    story.append(Paragraph("NUTRITION GUIDE", heading_style))

    diet = answers.get("dietary_preference", "non_vegetarian")
    if diet == "vegetarian":
        meal_examples = [
            ("Breakfast", f"~{int(macros['calories']*0.25)} kcal", "Paneer bhurji with whole wheat roti + milk"),
            ("Lunch", f"~{int(macros['calories']*0.35)} kcal", "Dal + rice + curd + sabzi + salad"),
            ("Pre-workout", f"~{int(macros['calories']*0.10)} kcal", "Banana + peanut butter"),
            ("Post-workout", f"~{int(macros['calories']*0.15)} kcal", "Whey protein shake + fruits"),
            ("Dinner", f"~{int(macros['calories']*0.20)} kcal", "Tofu stir fry + quinoa/roti + vegetables"),
            ("Before bed", f"~{int(macros['calories']*0.05)} kcal", "Cottage cheese (paneer) or Greek yogurt"),
        ]
    elif diet == "eggitarian":
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

    # Recovery Protocol
    story.append(Paragraph("RECOVERY PROTOCOL", heading_style))
    recovery_items = [
        "Sleep 7-9 hours every night — this is non-negotiable for muscle growth",
        "Drink 3-4 litres of water daily — more on training days",
        "On rest days: 20-30 min walk + full body stretching",
        "Deload every 8-10 weeks — reduce weight by 40% for one week",
        "Avoid alcohol — it directly impairs protein synthesis and recovery",
        "Creatine monohydrate 5g/day is the only supplement worth taking",
    ]
    for item in recovery_items:
        story.append(Paragraph(f"• {item}", body_style))
    story.append(Spacer(1, 20))

    # Discipline Rules
    story.append(Paragraph("THE 365 DISCIPLINE RULES", heading_style))
    rules = [
        "Never miss a Monday — momentum starts the week",
        "Track your food for at least the first 4 weeks",
        "Progressive overload: add weight or reps every week",
        "Do not change the program for at least 12 weeks",
        "Consistency beats intensity — showing up matters more than perfect workouts",
        "Take progress photos every 4 weeks — the mirror lies, photos don't",
    ]
    for i, rule in enumerate(rules, 1):
        story.append(Paragraph(f"{i}. {rule}", body_style))
    story.append(Spacer(1, 20))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"Generated for: {user_email} | Date: {datetime.now().strftime('%d %b %Y')} | 365 Days of Discipline",
        small_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ===== ROUTES =====
@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "365 Days of Discipline API Ready"}

@app.post("/api/quiz/submit", response_model=QuizResponse)
async def submit_quiz(answers: QuizAnswers):
    try:
        macros = calculate_macros(answers)
        quiz_id = str(uuid.uuid4())
        training_plan = get_training_plan(answers.training_days, answers.experience_level)

        # Store answers for later PDF generation
        quiz_store[quiz_id] = {
            "answers": answers.dict(),
            "macros": macros,
            "training_plan": training_plan,
            "created_at": datetime.now().isoformat()
        }

        return QuizResponse(
            quiz_id=quiz_id,
            calories=macros["calories"],
            protein=macros["protein"],
            training_plan=training_plan
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/submit")
async def submit_payment(
    quiz_id: str = Form(...),
    email: str = Form(...),
    screenshot: UploadFile = File(...)
):
    try:
        screenshot_data = await screenshot.read()

        # Get stored quiz data
        quiz_data = quiz_store.get(quiz_id)

        # Send notification email to you
        if SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg["From"] = SMTP_EMAIL
                msg["To"] = NOTIFY_EMAIL
                msg["Subject"] = f"💰 New Payment - {email}"

                body = f"""
New payment received!

Customer Email: {email}
Quiz ID: {quiz_id}
Time: {datetime.now().strftime('%d %b %Y %H:%M')}

Stats:
"""
                if quiz_data:
                    a = quiz_data["answers"]
                    m = quiz_data["macros"]
                    body += f"""
- Age: {a.get('age')}
- Weight: {a.get('weight')}kg
- Height: {a.get('height')}cm
- Goal: {a.get('goal')}
- Training Days: {a.get('training_days')}
- Diet: {a.get('dietary_preference')}
- Calories: {m['calories']} kcal
- Protein: {m['protein']}g
"""

                body += "\nPayment screenshot attached."
                msg.attach(MIMEText(body, "plain"))

                # Attach screenshot
                img_part = MIMEImage(screenshot_data)
                img_part.add_header("Content-Disposition", "attachment",
                                    filename=f"payment_{quiz_id[:8]}.jpg")
                msg.attach(img_part)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.sendmail(SMTP_EMAIL, NOTIFY_EMAIL, msg.as_string())
            except Exception as e:
                print(f"Email error: {e}")

        # Generate and send PDF to customer
        if quiz_data and SMTP_PASSWORD:
            try:
                pdf_buffer = generate_pdf(
                    quiz_data["answers"],
                    quiz_data["macros"],
                    email
                )

                msg2 = MIMEMultipart()
                msg2["From"] = SMTP_EMAIL
                msg2["To"] = email
                msg2["Subject"] = "Your 365 Days of Discipline Blueprint 💪"

                body2 = f"""Hi,

Thank you for your payment! Your personalized 365 Days of Discipline blueprint is attached.

Your Daily Targets:
- Calories: {quiz_data['macros']['calories']} kcal
- Protein: {quiz_data['macros']['protein']}g
- Carbs: {quiz_data['macros']['carbs']}g
- Fats: {quiz_data['macros']['fats']}g

Training Plan: {quiz_data['training_plan']}

Stay consistent. Results take time.

- Tharun
"""
                msg2.attach(MIMEText(body2, "plain"))

                pdf_attachment = MIMEBase("application", "octet-stream")
                pdf_attachment.set_payload(pdf_buffer.read())
                encoders.encode_base64(pdf_attachment)
                pdf_attachment.add_header("Content-Disposition", "attachment",
                                          filename="365_Days_of_Discipline.pdf")
                msg2.attach(pdf_attachment)

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.sendmail(SMTP_EMAIL, email, msg2.as_string())

            except Exception as e:
                print(f"PDF email error: {e}")

        return {"status": "success", "message": "Payment submitted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

Now you need to add two things:

**1. Add `reportlab` to your `requirements.txt`:**
```
fastapi
uvicorn
pydantic
reportlab
python-multipart
