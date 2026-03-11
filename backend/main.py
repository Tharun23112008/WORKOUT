from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import os
import io
import json
import traceback
import base64
import hashlib
import time as time_module
import httpx
from datetime import datetime
from pathlib import Path

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, BaseDocTemplate, PageTemplate, Frame, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ===== ENV VARS =====
NOTIFY_EMAIL           = os.environ.get("NOTIFY_EMAIL",            "tharunatwork23@gmail.com")
ADMIN_SECRET           = os.environ.get("ADMIN_SECRET",            "tharun365admin")
EMAILJS_SERVICE_ID     = os.environ.get("EMAILJS_SERVICE_ID",      "service_y3p7954")
EMAILJS_ADMIN_TMPL     = os.environ.get("EMAILJS_ADMIN_TEMPLATE_ID","template_dmwir7u")
EMAILJS_PDF_TMPL       = os.environ.get("EMAILJS_PDF_TEMPLATE_ID", "template_ecu877b")
EMAILJS_PUBLIC_KEY     = os.environ.get("EMAILJS_PUBLIC_KEY",      "c3EPeMlWCA9fJbKtq")
CLOUDINARY_CLOUD       = os.environ.get("CLOUDINARY_CLOUD_NAME",   "datg4264x")
CLOUDINARY_API_KEY     = os.environ.get("CLOUDINARY_API_KEY",      "638337381561993")
CLOUDINARY_API_SECRET  = os.environ.get("CLOUDINARY_API_SECRET",   "3wQLyZCGp66Ry0v71fJCl1nurBg")

# ===== APP =====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ===== PERSISTENT STORE =====
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
    store = _load_store(); store[quiz_id] = data; _save_store(store)

async def get_quiz(quiz_id: str):
    return _load_store().get(quiz_id)

async def save_payment(payment_id: str, data: dict):
    store = _load_store(); store[f"payment_{payment_id}"] = data; _save_store(store)

async def get_all_payments():
    store = _load_store()
    return [v for k, v in store.items() if k.startswith("payment_")]

async def update_payment_status(payment_id: str, status: str):
    store = _load_store()
    key = f"payment_{payment_id}"
    if key in store:
        store[key]["status"] = status; _save_store(store)

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

# ===== MACRO CALCULATION =====
def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, training_days):
    multipliers = {1: 1.2, 2: 1.375, 3: 1.375, 4: 1.55, 5: 1.55, 6: 1.725, 7: 1.9}
    return int(bmr * multipliers.get(training_days, 1.55))

def calculate_macros(answers):
    bmr  = calculate_bmr(answers.weight, answers.height, answers.age, answers.gender)
    tdee = calculate_tdee(bmr, answers.training_days)
    goal_adjustments = {"lose_fat": -500, "gain_muscle": 300, "recomposition": -200}
    calories = int(tdee + goal_adjustments.get(answers.goal, 0))
    protein_per_kg = {"gain_muscle": 2.0, "lose_fat": 2.2, "recomposition": 2.0}.get(answers.goal, 2.0)
    protein = int(answers.weight * protein_per_kg)
    diet = answers.dietary_preference.lower().strip()
    if diet == "vegetarian":
        protein = int(protein * 0.95)
    carbs = int((calories * 0.45) / 4)
    fats  = int((calories * 0.25) / 9)
    return {"calories": calories, "protein": protein, "carbs": carbs, "fats": fats}

def get_training_plan(training_days, experience_level):
    plans = {
        3: "Full Body 3-Day Split (Mon / Wed / Fri)",
        4: "Upper / Lower 4-Day Split",
        5: "Push / Pull / Legs + Upper / Lower",
        6: "Bro Split — Chest / Back / Shoulders / Arms / Legs",
    }
    return plans.get(training_days, "Custom Training Split")

# =====================================================================
# PREMIUM PDF GENERATION
# =====================================================================

# Brand colors — matching webapp
_BG      = HexColor("#0A0A0A")
_CARD    = HexColor("#141414")
_CARD2   = HexColor("#1A1A1A")
_HEADER  = HexColor("#1F1F1F")
_PRIMARY = HexColor("#FF5B9E")
_TEAL    = HexColor("#34B3D2")
_WHITE   = HexColor("#FFFFFF")
_GRAY    = HexColor("#888888")
_TEXT    = HexColor("#E0E0E0")
_BORDER  = HexColor("#2A2A2A")

_W, _H = A4

# Workout splits — keyed by training_days
_WORKOUT_SPLITS = {
    6: [
        ("Monday",    "CHEST",     "Bench Press 4x8, Incline DB Press 3x10, Cable Flyes 3x12, Push-Ups 2x15"),
        ("Tuesday",   "BACK",      "Deadlift 4x6, Pull-Ups 3x8, Barbell Row 3x10, Lat Pulldown 3x12"),
        ("Wednesday", "SHOULDERS", "OHP 4x8, Lateral Raises 4x12, Front Raises 3x12, Face Pulls 3x15"),
        ("Thursday",  "BICEPS",    "Barbell Curl 4x10, Hammer Curl 3x12, Incline DB Curl 3x12, Cable Curl 2x15"),
        ("Friday",    "TRICEPS",   "Skull Crushers 4x10, Tricep Dips 3x10, Pushdowns 3x12, Overhead Ext. 3x12"),
        ("Saturday",  "LEGS",      "Squat 4x8, Romanian Deadlift 3x10, Leg Press 3x12, Calf Raises 4x15"),
        ("Sunday",    "REST",      "Active recovery: 20-30 min walk or stretching"),
    ],
    5: [
        ("Monday",    "PUSH",  "Bench Press 4x8, OHP 3x10, Lateral Raises 3x12, Tricep Pushdowns 3x12"),
        ("Tuesday",   "PULL",  "Deadlift 4x6, Pull-Ups 3x8, Barbell Row 3x10, Bicep Curls 3x12"),
        ("Wednesday", "LEGS",  "Squat 4x8, Leg Press 3x12, Romanian Deadlift 3x10, Calf Raises 4x15"),
        ("Thursday",  "UPPER", "Incline Press 4x10, DB Row 3x10, Shoulder Press 3x10, Curls 3x12"),
        ("Friday",    "LOWER", "Front Squat 4x8, Hip Thrust 3x12, Leg Curl 3x12, Calf Raises 4x15"),
        ("Saturday",  "REST",  "Active recovery or cardio 20-30 min"),
        ("Sunday",    "REST",  "Full rest day"),
    ],
    4: [
        ("Monday",    "UPPER A", "Bench Press 4x8, Row 4x8, OHP 3x10, Curl 3x12"),
        ("Tuesday",   "LOWER A", "Squat 4x8, Romanian Deadlift 3x10, Leg Press 3x12, Calf Raises 4x15"),
        ("Wednesday", "REST",    "Active recovery"),
        ("Thursday",  "UPPER B", "Incline Press 4x10, Pull-Ups 3x8, Lateral Raises 3x12, Triceps 3x12"),
        ("Friday",    "LOWER B", "Deadlift 4x6, Front Squat 3x8, Leg Curl 3x12, Hip Thrust 3x12"),
        ("Saturday",  "REST",    "Rest or light cardio"),
        ("Sunday",    "REST",    "Full rest day"),
    ],
    3: [
        ("Monday",    "FULL BODY A", "Squat 3x8, Bench Press 3x8, Row 3x8, OHP 3x10, Curl 3x12"),
        ("Wednesday", "FULL BODY B", "Deadlift 3x6, Incline Press 3x10, Pull-Ups 3x8, Dips 3x10"),
        ("Friday",    "FULL BODY C", "Front Squat 3x8, DB Press 3x10, Cable Row 3x12, Lateral Raises 3x12"),
    ],
}

# Meal plans — keyed by diet type
_MEAL_PLANS = {
    "vegetarian": [
        ("Breakfast",    0.25, "Paneer bhurji + whole wheat roti + milk"),
        ("Lunch",        0.35, "Dal + rice + curd + sabzi + salad"),
        ("Pre-Workout",  0.10, "Banana + peanut butter"),
        ("Post-Workout", 0.15, "Whey protein shake + fruits"),
        ("Dinner",       0.20, "Tofu stir fry + quinoa/roti + vegetables"),
        ("Before Bed",   0.05, "Paneer or Greek yogurt"),
    ],
    "eggetarian": [
        ("Breakfast",    0.25, "4 eggs (2 whole + 2 whites) + oats + fruit"),
        ("Lunch",        0.35, "Rice + dal + egg curry + salad"),
        ("Pre-Workout",  0.10, "Banana + boiled eggs"),
        ("Post-Workout", 0.15, "Whey protein + fruits"),
        ("Dinner",       0.20, "Egg omelette + roti + vegetables"),
        ("Before Bed",   0.05, "Greek yogurt or cottage cheese"),
    ],
    "non_vegetarian": [
        ("Breakfast",    0.25, "Eggs + oats + fruit + milk"),
        ("Lunch",        0.35, "Rice + chicken curry + dal + salad"),
        ("Pre-Workout",  0.10, "Banana + peanut butter"),
        ("Post-Workout", 0.15, "Whey protein shake + fruits"),
        ("Dinner",       0.20, "Grilled chicken/fish + roti + vegetables"),
        ("Before Bed",   0.05, "Greek yogurt or cottage cheese"),
    ],
}


def _draw_page(canvas, doc):
    """Draws the dark background, header bar, and footer on every page."""
    canvas.saveState()

    # Dark full-page background
    canvas.setFillColor(_BG)
    canvas.rect(0, 0, _W, _H, fill=1, stroke=0)

    # Subtle corner glows
    canvas.setFillColor(HexColor("#1E0A12"))
    canvas.ellipse(_W * 0.6, _H - 80, _W + 180, _H + 180, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#08121A"))
    canvas.ellipse(-180, -180, _W * 0.35, 80, fill=1, stroke=0)

    # Header bar
    canvas.setFillColor(_CARD)
    canvas.rect(0, _H - 68, _W, 68, fill=1, stroke=0)

    # Pink accent line at very top
    canvas.setFillColor(_PRIMARY)
    canvas.rect(0, _H - 4, _W, 4, fill=1, stroke=0)

    # Brand name
    canvas.setFillColor(_PRIMARY)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(40, _H - 40, "365 DAYS OF DISCIPLINE")

    # Tagline
    canvas.setFillColor(_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, _H - 56, "Your Personalized Protocol Blueprint")

    # Page number
    canvas.setFillColor(_GRAY)
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(_W - 40, _H - 44, f"Page {doc.page}")

    # Footer bar
    canvas.setFillColor(_CARD)
    canvas.rect(0, 0, _W, 32, fill=1, stroke=0)
    canvas.setFillColor(_PRIMARY)
    canvas.rect(0, 30, _W, 2, fill=1, stroke=0)
    canvas.setFillColor(_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(_W / 2, 11,
        "365 Days of Discipline  \u2022  Your Personalized Protocol  \u2022  Stay Consistent")

    canvas.restoreState()


def _style(name, **kw):
    """Helper to create a ParagraphStyle with sensible defaults."""
    base = dict(fontName="Helvetica", fontSize=10, textColor=_TEXT, spaceAfter=4, leading=14)
    base.update(kw)
    return ParagraphStyle(name, **base)


def _cell(text, color=None, bold=False, size=9, align=TA_LEFT):
    """Quick Paragraph cell for tables."""
    if color is None:
        color = _TEXT
    fn = "Helvetica-Bold" if bold else "Helvetica"
    # Unique style name avoids ReportLab "duplicate style" warnings
    sname = f"cell_{abs(hash(text + str(color) + str(bold) + str(size)))}"
    return Paragraph(
        text,
        _style(sname, fontSize=size, textColor=color,
               fontName=fn, alignment=align, leading=size + 4)
    )


def _tbl_style(header_bg=None):
    """Standard dark-themed TableStyle."""
    if header_bg is None:
        header_bg = _PRIMARY
    return TableStyle([
        ("BACKGROUND",     (0,  0), (-1,  0), header_bg),
        ("TEXTCOLOR",      (0,  0), (-1,  0), _WHITE),
        ("FONTNAME",       (0,  0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",       (0,  0), (-1,  0), 9),
        ("ROWBACKGROUNDS", (0,  1), (-1, -1), [_CARD, _CARD2]),
        ("TEXTCOLOR",      (0,  1), (-1, -1), _TEXT),
        ("FONTSIZE",       (0,  1), (-1, -1), 9),
        ("ALIGN",          (0,  0), (-1, -1), "CENTER"),
        ("VALIGN",         (0,  0), (-1, -1), "MIDDLE"),
        ("PADDING",        (0,  0), (-1, -1), 10),
        ("GRID",           (0,  0), (-1, -1), 0.5, _BORDER),
    ])


def generate_pdf(answers: dict, macros: dict, user_email: str) -> io.BytesIO:
    """
    Generate a premium dark-themed PDF blueprint.

    Parameters
    ----------
    answers : dict
        Quiz answers from the user (age, weight, height, gender, goal,
        training_days, dietary_preference, experience_level, …)
    macros : dict
        Calculated macros: {calories, protein, carbs, fats}
    user_email : str
        Customer email shown in the footer.

    Returns
    -------
    io.BytesIO  — ready to upload to Cloudinary or stream as response.
    """
    buffer = io.BytesIO()

    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=88, bottomMargin=48,
    )
    frame = Frame(40, 48, _W - 80, _H - 136, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=_draw_page)])

    # ── Derived values ────────────────────────────────────────────────
    goal_labels = {
        "gain_muscle":  "Gain Muscle",
        "lose_fat":     "Lose Fat",
        "recomposition":"Body Recomposition",
    }
    goal_label = goal_labels.get(answers.get("goal", ""), "Custom Goal")

    training_labels = {
        3: "Full Body 3-Day Split (Mon / Wed / Fri)",
        4: "Upper / Lower 4-Day Split",
        5: "Push / Pull / Legs + Upper / Lower",
        6: "Bro Split \u2014 Chest / Back / Shoulders / Arms / Legs",
    }
    training_label = training_labels.get(answers.get("training_days", 4), "Custom Training Split")

    diet_key = answers.get("dietary_preference", "non_vegetarian").lower().strip()
    if diet_key in ("eggetarian", "eggitarian"):
        diet_key = "eggetarian"
    if diet_key not in _MEAL_PLANS:
        diet_key = "non_vegetarian"

    # ── Shared styles ─────────────────────────────────────────────────
    title_s   = _style("title",   fontSize=28, textColor=_PRIMARY, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, spaceAfter=4, leading=32)
    sub_s     = _style("sub",     fontSize=11, textColor=_GRAY, alignment=TA_CENTER, spaceAfter=18)
    section_s = _style("sec",     fontSize=13, textColor=_PRIMARY, fontName="Helvetica-Bold",
                        spaceAfter=10, spaceBefore=14)
    label_s   = _style("lbl",     fontSize=8,  textColor=_WHITE, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, spaceAfter=2)
    big_pink  = _style("bigp",    fontSize=22, textColor=_PRIMARY, fontName="Helvetica-Bold",
                        alignment=TA_CENTER, leading=26)
    small_lbl = _style("slbl",    fontSize=7,  textColor=_GRAY, alignment=TA_CENTER, spaceAfter=1)
    footer_s  = _style("ftr",     fontSize=8,  textColor=_GRAY, alignment=TA_CENTER)

    story = []

    # ══════════════════════════════════════════════════════════════════
    # PAGE 1 — PROFILE + MACROS + TRAINING SPLIT
    # ══════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 8))
    story.append(Paragraph("YOUR PERSONALIZED", sub_s))
    story.append(Paragraph("PROTOCOL BLUEPRINT", title_s))
    story.append(HRFlowable(width="100%", thickness=2, color=_PRIMARY, spaceAfter=14))

    # ── Profile stats ─────────────────────────────────────────────────
    story.append(Paragraph("YOUR PROFILE", section_s))

    p_data = [
        [Paragraph("AGE", label_s),            Paragraph("WEIGHT", label_s),
         Paragraph("HEIGHT", label_s),          Paragraph("GENDER", label_s)],
        [Paragraph(str(answers.get("age", "")), big_pink),
         Paragraph(str(answers.get("weight", "")), big_pink),
         Paragraph(str(answers.get("height", "")), big_pink),
         Paragraph(str(answers.get("gender", "")).upper(), big_pink)],
        [Paragraph("years", small_lbl), Paragraph("kg", small_lbl),
         Paragraph("cm", small_lbl),    Paragraph("", small_lbl)],
    ]
    p_table = Table(p_data, colWidths=[118, 118, 118, 118])
    p_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _HEADER),
        ("BACKGROUND", (0, 1), (-1, 2), _CARD),
        ("GRID",       (0, 0), (-1,-1), 0.5, _BORDER),
        ("ALIGN",      (0, 0), (-1,-1), "CENTER"),
        ("VALIGN",     (0, 0), (-1,-1), "MIDDLE"),
        ("PADDING",    (0, 0), (-1,-1), 8),
        ("LINEAFTER",  (0, 0), (2, -1), 0.5, _BORDER),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 6))

    g_data = [
        [Paragraph("GOAL", label_s),             Paragraph("TRAINING DAYS", label_s),
         Paragraph("EXPERIENCE", label_s),        Paragraph("DIET", label_s)],
        [_cell(goal_label, _PRIMARY, bold=True,  size=10, align=TA_CENTER),
         _cell(f"{answers.get('training_days', 4)} days/week", _TEAL, bold=True, size=10, align=TA_CENTER),
         _cell(str(answers.get("experience_level", "")).capitalize(), _TEXT, size=10, align=TA_CENTER),
         _cell(diet_key.replace("_", " ").capitalize(), _TEXT, size=10, align=TA_CENTER)],
    ]
    g_table = Table(g_data, colWidths=[118, 118, 118, 118])
    g_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _HEADER),
        ("BACKGROUND", (0, 1), (-1, 1), _CARD2),
        ("GRID",       (0, 0), (-1,-1), 0.5, _BORDER),
        ("ALIGN",      (0, 0), (-1,-1), "CENTER"),
        ("VALIGN",     (0, 0), (-1,-1), "MIDDLE"),
        ("PADDING",    (0, 0), (-1,-1), 10),
    ]))
    story.append(g_table)
    story.append(Spacer(1, 6))

    # ── Daily macros ─────────────────────────────────────────────────
    story.append(Paragraph("DAILY NUTRITION TARGETS", section_s))

    m_data = [
        [Paragraph("CALORIES", label_s), Paragraph("PROTEIN", label_s),
         Paragraph("CARBS", label_s),    Paragraph("FATS", label_s)],
        [Paragraph(str(macros["calories"]), big_pink),
         Paragraph(f"{macros['protein']}g", big_pink),
         Paragraph(f"{macros['carbs']}g", big_pink),
         Paragraph(f"{macros['fats']}g", big_pink)],
        [Paragraph("kcal / day", small_lbl), Paragraph("daily target", small_lbl),
         Paragraph("daily target", small_lbl), Paragraph("daily target", small_lbl)],
    ]
    m_table = Table(m_data, colWidths=[118, 118, 118, 118])
    m_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
        ("BACKGROUND", (0, 1), (-1, 1), _CARD),
        ("BACKGROUND", (0, 2), (-1, 2), _HEADER),
        ("GRID",       (0, 0), (-1,-1), 0.5, _BORDER),
        ("ALIGN",      (0, 0), (-1,-1), "CENTER"),
        ("VALIGN",     (0, 0), (-1,-1), "MIDDLE"),
        ("PADDING",    (0, 0), (-1,-1), 10),
        ("LINEAFTER",  (0, 0), (2, -1), 0.5, _BORDER),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 6))

    # ── Training split ───────────────────────────────────────────────
    story.append(Paragraph("YOUR TRAINING STRUCTURE", section_s))
    story.append(Paragraph(
        f"<b>{training_label}</b>",
        _style("tl", fontSize=10, textColor=_TEAL, fontName="Helvetica-Bold", spaceAfter=8)
    ))

    split = _WORKOUT_SPLITS.get(answers.get("training_days", 4), _WORKOUT_SPLITS[4])
    w_data = [[Paragraph("DAY", label_s), Paragraph("FOCUS", label_s), Paragraph("EXERCISES", label_s)]]
    for day, focus, exs in split:
        fc = _TEAL if focus not in ("REST",) else _GRAY
        w_data.append([
            _cell(day,   _TEXT, bold=True, size=9, align=TA_CENTER),
            _cell(focus, fc,    bold=True, size=9, align=TA_CENTER),
            _cell(exs,   _TEXT, size=8,    align=TA_LEFT),
        ])
    w_table = Table(w_data, colWidths=[75, 85, 312])
    w_table.setStyle(_tbl_style(header_bg=_TEAL))
    story.append(w_table)

    # ══════════════════════════════════════════════════════════════════
    # PAGE 2 — NUTRITION + RECOVERY + DISCIPLINE CODE
    # ══════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    # ── Meal plan ────────────────────────────────────────────────────
    story.append(Paragraph("NUTRITION GUIDE", section_s))

    meals = _MEAL_PLANS[diet_key]
    meal_data = [[Paragraph("MEAL", label_s), Paragraph("CALORIES", label_s), Paragraph("WHAT TO EAT", label_s)]]
    for name, pct, food in meals:
        kcal = int(macros["calories"] * pct)
        meal_data.append([
            _cell(name,            _PRIMARY, bold=True, size=9, align=TA_CENTER),
            _cell(f"~{kcal} kcal", _TEAL,   bold=True, size=9, align=TA_CENTER),
            _cell(food,            _TEXT,    size=8,    align=TA_LEFT),
        ])
    meal_table = Table(meal_data, colWidths=[90, 90, 292])
    meal_table.setStyle(_tbl_style(header_bg=_PRIMARY))
    story.append(meal_table)
    story.append(Spacer(1, 6))

    # ── Recovery protocol ────────────────────────────────────────────
    story.append(Paragraph("RECOVERY PROTOCOL", section_s))

    recovery = [
        ("Sleep",     "7-9 hours every night \u2014 non-negotiable for muscle growth and hormone regulation"),
        ("Hydration", "3-4 litres of water daily \u2014 more on training days"),
        ("Rest Days", "20-30 min walk + full body stretching on off days"),
        ("Deload",    "Every 8-10 weeks \u2014 reduce weight by 40% for one full week"),
        ("Alcohol",   "Avoid completely \u2014 directly impairs protein synthesis and recovery"),
        ("Creatine",  "5g monohydrate daily \u2014 the only supplement with solid evidence"),
    ]
    rec_data = [[Paragraph("FOCUS", label_s), Paragraph("GUIDANCE", label_s)]]
    for lbl, detail in recovery:
        rec_data.append([
            _cell(lbl,    _TEAL, bold=True, size=9, align=TA_CENTER),
            _cell(detail, _TEXT, size=8,    align=TA_LEFT),
        ])
    rec_table = Table(rec_data, colWidths=[90, 382])
    rec_table.setStyle(_tbl_style(header_bg=_TEAL))
    story.append(rec_table)
    story.append(Spacer(1, 6))

    # ── Discipline rules ─────────────────────────────────────────────
    story.append(Paragraph("THE 365 DISCIPLINE CODE", section_s))

    rules = [
        ("01", "Never miss a Monday \u2014 momentum is built at the start of the week"),
        ("02", "Track your food for at least the first 4 weeks \u2014 awareness is everything"),
        ("03", "Progressive overload every week \u2014 add weight or reps, no exceptions"),
        ("04", "Do not change the program for at least 12 weeks \u2014 trust the process"),
        ("05", "Consistency beats intensity \u2014 showing up matters more than perfect workouts"),
        ("06", "Take progress photos every 4 weeks \u2014 the mirror lies, photos don't"),
    ]
    rules_data = [[Paragraph("#", label_s), Paragraph("THE RULE", label_s)]]
    for num, rule in rules:
        rules_data.append([
            Paragraph(num, _style(f"rn{num}", fontSize=16, textColor=_PRIMARY,
                                   fontName="Helvetica-Bold", alignment=TA_CENTER)),
            _cell(rule, _TEXT, size=9, align=TA_LEFT),
        ])
    rules_table = Table(rules_data, colWidths=[50, 422])
    rules_table.setStyle(TableStyle([
        ("BACKGROUND",     (0,  0), (-1,  0), _PRIMARY),
        ("TEXTCOLOR",      (0,  0), (-1,  0), _WHITE),
        ("FONTNAME",       (0,  0), (-1,  0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,  1), (-1, -1), [_CARD, _CARD2]),
        ("GRID",           (0,  0), (-1, -1), 0.5, _BORDER),
        ("ALIGN",          (0,  0), (0,  -1), "CENTER"),
        ("VALIGN",         (0,  0), (-1, -1), "MIDDLE"),
        ("PADDING",        (0,  0), (-1, -1), 10),
        ("LINEBEFORE",     (1,  0), (1,  -1), 2, _PRIMARY),
    ]))
    story.append(rules_table)
    story.append(Spacer(1, 20))

    # ── Sign-off ──────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=_BORDER, spaceAfter=8))
    story.append(Paragraph(
        f"Generated for: <b>{user_email}</b>  |  "
        f"{datetime.now().strftime('%d %b %Y')}  |  365 Days of Discipline",
        footer_s
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# =====================================================================
# EMAIL + CLOUDINARY HELPERS
# =====================================================================

async def send_emailjs(template_params: dict, template_id: str = None):
    """Send via EmailJS HTTP API — works on Render free tier."""
    payload = {
        "service_id":    EMAILJS_SERVICE_ID,
        "template_id":   template_id or EMAILJS_ADMIN_TMPL,
        "user_id":       EMAILJS_PUBLIC_KEY,
        "template_params": template_params,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post("https://api.emailjs.com/api/v1.0/email/send", json=payload)
        if resp.status_code != 200:
            raise Exception(f"EmailJS error {resp.status_code}: {resp.text}")
    print(f"EmailJS sent -> {template_params.get('to_email') or template_params.get('customer_email')}")


async def upload_pdf_to_cloudinary(pdf_buffer: io.BytesIO, filename: str) -> str:
    """Upload PDF to Cloudinary, return a browser-friendly download URL."""
    timestamp  = str(int(time_module.time()))
    public_id  = f"365discipline/{filename}"

    # Signature must include params in alphabetical order
    params_str = f"public_id={public_id}&timestamp={timestamp}"
    signature  = hashlib.sha1(f"{params_str}{CLOUDINARY_API_SECRET}".encode()).hexdigest()

    pdf_b64  = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    data_uri = f"data:application/pdf;base64,{pdf_b64}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD}/raw/upload",
            data={
                "file":      data_uri,
                "public_id": public_id,
                "timestamp": timestamp,
                "api_key":   CLOUDINARY_API_KEY,
                "signature": signature,
            }
        )
        if resp.status_code != 200:
            raise Exception(f"Cloudinary upload failed: {resp.text}")

        secure_url = resp.json()["secure_url"]

        # Force browser to treat the file as a downloadable PDF.
        # Cloudinary raw uploads don't set Content-Type automatically,
        # so we append fl_attachment to trigger a proper download.
        # Replace the base URL part to inject the transformation flag.
        download_url = secure_url.replace(
            "/raw/upload/",
            "/raw/upload/fl_attachment:" + filename.replace(".pdf", "") + "/"
        )
        return download_url


async def send_pdf_email(email: str, quiz_data: dict):
    """Generate PDF, upload to Cloudinary, send link via EmailJS."""
    pdf_buffer = generate_pdf(quiz_data["answers"], quiz_data["macros"], email)
    email_prefix = email.split('@')[0].replace('.', '_').replace('+', '_')
    filename     = f"365_discipline_{email_prefix}_{uuid.uuid4().hex[:8]}.pdf"
    pdf_url    = await upload_pdf_to_cloudinary(pdf_buffer, filename)

    m = quiz_data["macros"]
    await send_emailjs({
        "to_email":     email,
        "to_name":      email.split("@")[0],
        "calories":     str(m["calories"]),
        "protein":      str(m["protein"]),
        "carbs":        str(m["carbs"]),
        "fats":         str(m["fats"]),
        "training_plan": quiz_data.get("training_plan", ""),
        "pdf_url":      pdf_url,
    }, template_id=EMAILJS_PDF_TMPL)


# =====================================================================
# ROUTES
# =====================================================================

@app.get("/")
async def root():
    return {"message": "365 Days of Discipline API Ready"}

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "emailjs_configured": bool(EMAILJS_PUBLIC_KEY),
        "cloudinary_configured": bool(CLOUDINARY_API_KEY),
    }

@app.post("/api/quiz/submit", response_model=QuizResponse)
async def submit_quiz(answers: QuizAnswers):
    try:
        macros = calculate_macros(answers)
        print(f"Macros: {macros}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Macro calculation failed: {str(e)}")

    quiz_id       = str(uuid.uuid4())
    training_plan = get_training_plan(answers.training_days, answers.experience_level)
    data = {
        "answers":       answers.dict(),
        "macros":        macros,
        "training_plan": training_plan,
        "created_at":    datetime.now().isoformat(),
    }
    try:
        await save_quiz(quiz_id, data)
        print(f"Quiz saved: {quiz_id}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")

    return QuizResponse(quiz_id=quiz_id, calories=macros["calories"],
                        protein=macros["protein"], training_plan=training_plan)


@app.post("/api/payment/submit")
async def submit_payment(
    quiz_id:    str        = Form(...),
    email:      str        = Form(...),
    screenshot: UploadFile = File(...),
):
    if screenshot.content_type and not screenshot.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
    screenshot_data = await screenshot.read()
    if len(screenshot_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Screenshot too large. Max 10MB.")

    quiz_data = await get_quiz(quiz_id)
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz session not found. Please retake the quiz.")

    payment_id = str(uuid.uuid4())
    await save_payment(payment_id, {
        "payment_id":   payment_id,
        "quiz_id":      quiz_id,
        "email":        email,
        "status":       "pending",
        "submitted_at": datetime.now().isoformat(),
        "quiz_data":    quiz_data,
    })
    print(f"Payment saved: {payment_id} for {email}")

    try:
        a = quiz_data["answers"]
        m = quiz_data["macros"]
        approve_link = f"https://workout-h4i4.onrender.com/api/admin/approve/{payment_id}?secret={ADMIN_SECRET}"
        await send_emailjs({
            "to_email":       NOTIFY_EMAIL,
            "customer_email": email,
            "payment_id":     payment_id,
            "time":           datetime.now().strftime("%d %b %Y %H:%M"),
            "goal":           a.get("goal", ""),
            "calories":       str(m["calories"]),
            "protein":        str(m["protein"]),
            "approve_link":   approve_link,
        })
        print(f"Admin notified at {NOTIFY_EMAIL}")
    except Exception as e:
        print(f"Admin email failed (payment still saved): {e}")

    return {
        "status":     "success",
        "payment_id": payment_id,
        "message":    "Payment submitted. You'll receive your PDF within 24 hours after verification.",
    }


@app.get("/api/admin/payments")
async def list_payments(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return {"payments": await get_all_payments()}


@app.get("/api/admin/approve/{payment_id}")
async def approve_payment(payment_id: str, secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")

    store   = _load_store()
    payment = store.get(f"payment_{payment_id}")
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.get("status") == "approved":
        return {"status": "already_approved", "message": f"PDF already sent to {payment.get('email')}."}

    email     = payment["email"]
    quiz_data = payment.get("quiz_data") or await get_quiz(payment["quiz_id"])
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz data not found. Cannot generate PDF.")

    await update_payment_status(payment_id, "approved")
    try:
        await send_pdf_email(email, quiz_data)
        print(f"PDF sent to {email}")
        return {"status": "success", "message": f"PDF sent to {email} successfully!"}
    except Exception as e:
        await update_payment_status(payment_id, "send_failed")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF send failed: {str(e)}")
