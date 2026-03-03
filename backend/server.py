from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from fastapi.responses import StreamingResponse

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe
stripe_api_key = os.environ['STRIPE_API_KEY']

app = FastAPI()
api_router = APIRouter(prefix="/api")

logger = logging.getLogger(__name__)

# ============= MODELS =============

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

class CheckoutRequest(BaseModel):
    quiz_id: str
    origin_url: str

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    quiz_id: str
    amount: float
    currency: str
    payment_status: str
    metadata: Dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============= CALCULATION LOGIC =============

def calculate_bmr(weight: float, height: int, age: int, gender: str) -> int:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return int(bmr)

def calculate_tdee(bmr: int, training_days: int) -> int:
    """Calculate Total Daily Energy Expenditure based on training frequency"""
    # Map training days to activity level
    if training_days <= 2:
        multiplier = 1.375  # Light
    elif training_days <= 4:
        multiplier = 1.55   # Moderate
    elif training_days <= 5:
        multiplier = 1.725  # Active
    else:
        multiplier = 1.9    # Very active
    return int(bmr * multiplier)

def calculate_macros(answers: QuizAnswers) -> CalculationResult:
    """Calculate personalized nutrition and training"""
    bmr = calculate_bmr(answers.weight, answers.height, answers.age, answers.gender)
    tdee = calculate_tdee(bmr, answers.training_days)
    
    # Adjust calories based on goal
    goal_adjustments = {
        "lose_fat": -500,
        "gain_muscle": 300,
        "recomposition": -200
    }
    
    calories = tdee + goal_adjustments.get(answers.goal, 0)
    
    # Protein calculation based on goal
    if answers.goal == "gain_muscle":
        protein_per_kg = 2.0
    elif answers.goal == "lose_fat":
        protein_per_kg = 2.2
    else:  # recomposition
        protein_per_kg = 2.0
    
    protein = int(answers.weight * protein_per_kg)
    
    # Adjust slightly for vegetarians
    if answers.dietary_preference == "vegetarian":
        protein = int(protein * 0.95)
    
    # Fats: 25% of total calories
    fats = int((calories * 0.25) / 9)
    
    # Carbs: remaining calories
    carbs = int((calories - (protein * 4) - (fats * 9)) / 4)
    
    # Training plan - bro split with modifications
    training_plan = get_training_plan(answers.training_days, answers.experience_level)
    
    return CalculationResult(
        quiz_id="",  # Will be set in route
        calories=calories,
        protein=protein,
        carbs=carbs,
        fats=fats,
        training_plan=training_plan,
        bmr=bmr,
        tdee=tdee
    )

def get_training_plan(training_days: int, experience: str) -> str:
    """Generate training plan structure - based on bro split"""
    if training_days >= 6:
        return "6-day Bro Split: Chest, Back, Shoulders, Biceps, Triceps, Legs + Active Rest"
    elif training_days == 5:
        return "5-day Bro Split: Chest, Back, Shoulders, Arms (Bi+Tri), Legs"
    elif training_days == 4:
        return "4-day Modified Split: Chest+Biceps, Back+Triceps, Shoulders, Legs"
    else:
        return "3-day Full Body: Upper Push/Pull, Lower, Full Body"

# ============= PDF GENERATION =============

def generate_pdf(quiz_data: QuizResponse) -> io.BytesIO:
    """Generate personalized PDF report - 365 Days of Discipline"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles - minimalist, professional
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#444444'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.black,
        spaceAfter=16,
        spaceBefore=24,
        fontName='Helvetica-Bold'
    )
    
    # === COVER PAGE ===
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("365 DAYS OF DISCIPLINE", title_style))
    story.append(Paragraph("A Personalized Training & Nutrition Blueprint", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Built from a real one-year transformation — tailored to you.", styles['Normal']))
    story.append(PageBreak())
    
    # Personal Info
    story.append(Paragraph("YOUR PROFILE", heading_style))
    profile_data = [
        ['Age:', f"{quiz_data.answers.age} years"],
        ['Weight:', f"{quiz_data.answers.weight} kg"],
        ['Height:', f"{quiz_data.answers.height} cm"],
        ['Gender:', quiz_data.answers.gender.title()],
        ['Activity Level:', quiz_data.answers.activity_level.replace('_', ' ').title()],
        ['Goal:', quiz_data.answers.goal.replace('_', ' ').title()],
        ['Experience:', quiz_data.answers.experience_level.title()],
    ]
    profile_table = Table(profile_data, colWidths=[2*inch, 4*inch])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Nutrition Plan
    story.append(Paragraph("NUTRITION TARGETS", heading_style))
    macro_data = [
        ['Daily Calories:', f"{quiz_data.calories} kcal"],
        ['Protein:', f"{quiz_data.protein}g (Priority #1)"],
        ['Carbohydrates:', f"{quiz_data.carbs}g"],
        ['Fats:', f"{quiz_data.fats}g"],
    ]
    macro_table = Table(macro_data, colWidths=[2.5*inch, 3.5*inch])
    macro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E6F2FF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#007AFF'))
    ]))
    story.append(macro_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Meal timing
    story.append(Paragraph("Meal Timing Strategy", styles['Heading3']))
    if quiz_data.answers.goal == "gain_muscle":
        meal_text = "• Eat 4-5 meals spread throughout the day<br/>• Pre-workout: Carbs + Protein 1-2 hours before<br/>• Post-workout: Protein shake within 30 minutes<br/>• Before bed: Casein protein or Greek yogurt"
    else:
        meal_text = "• Eat 3-4 balanced meals per day<br/>• Front-load calories earlier in the day<br/>• Post-workout nutrition within 2 hours<br/>• Light dinner 2-3 hours before sleep"
    story.append(Paragraph(meal_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Training Plan
    story.append(PageBreak())
    story.append(Paragraph("TRAINING PROTOCOL", heading_style))
    story.append(Paragraph(f"<b>Your Program:</b> {quiz_data.training_plan}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Detailed workout structure
    if "full body" in quiz_data.training_plan.lower():
        workout_structure = """
        <b>FULL BODY ROUTINE (3x per week)</b><br/><br/>
        <b>Day 1, 3, 5:</b><br/>
        • Squat or Leg Press: 3 sets x 8-12 reps<br/>
        • Bench Press or Push-ups: 3 sets x 8-12 reps<br/>
        • Rows or Pull-ups: 3 sets x 8-12 reps<br/>
        • Overhead Press: 3 sets x 8-12 reps<br/>
        • Romanian Deadlift: 3 sets x 10-12 reps<br/>
        • Plank: 3 sets x 30-60 seconds<br/><br/>
        Rest 48 hours between sessions
        """
    elif "upper/lower" in quiz_data.training_plan.lower():
        workout_structure = """
        <b>UPPER/LOWER SPLIT (4x per week)</b><br/><br/>
        <b>Upper Day 1 & 3:</b><br/>
        • Bench Press: 4x6-8<br/>
        • Rows: 4x8-10<br/>
        • Overhead Press: 3x8-10<br/>
        • Pull-ups: 3x8-12<br/>
        • Bicep Curls: 3x10-12<br/>
        • Tricep Extensions: 3x10-12<br/><br/>
        <b>Lower Day 2 & 4:</b><br/>
        • Squats: 4x6-8<br/>
        • Romanian Deadlift: 3x8-10<br/>
        • Leg Press: 3x10-12<br/>
        • Leg Curls: 3x10-12<br/>
        • Calf Raises: 4x12-15<br/>
        • Abs: 3 sets
        """
    else:
        workout_structure = """
        <b>PUSH/PULL/LEGS SPLIT</b><br/><br/>
        <b>Push Day:</b> Chest, Shoulders, Triceps<br/>
        <b>Pull Day:</b> Back, Biceps<br/>
        <b>Leg Day:</b> Quads, Hamstrings, Glutes, Calves<br/><br/>
        4-6 exercises per session, 3-4 sets each<br/>
        Rep ranges: 6-12 for compounds, 10-15 for isolation<br/>
        Progressive overload: Add weight or reps weekly
        """
    
    story.append(Paragraph(workout_structure, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Recovery
    story.append(Paragraph("Recovery Guidelines", styles['Heading3']))
    recovery_text = "• Sleep 7-9 hours per night<br/>• Rest days: 2-3 per week<br/>• Active recovery: Light walking, stretching<br/>• Hydration: 3-4 liters water daily"
    story.append(Paragraph(recovery_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Sample meal plan
    story.append(PageBreak())
    story.append(Paragraph("SAMPLE MEAL PLAN", heading_style))
    
    if quiz_data.answers.dietary_preference == "vegetarian":
        meal_plan = """
        <b>Breakfast:</b> Oatmeal with protein powder, berries, nuts<br/>
        <b>Snack:</b> Greek yogurt with granola<br/>
        <b>Lunch:</b> Quinoa bowl with chickpeas, veggies, tahini<br/>
        <b>Pre-Workout:</b> Banana with peanut butter<br/>
        <b>Post-Workout:</b> Protein shake with spinach<br/>
        <b>Dinner:</b> Tofu stir-fry with brown rice and vegetables<br/>
        <b>Evening:</b> Cottage cheese with berries
        """
    elif quiz_data.answers.dietary_preference == "vegan":
        meal_plan = """
        <b>Breakfast:</b> Smoothie bowl with plant protein, chia seeds<br/>
        <b>Snack:</b> Hummus with veggie sticks<br/>
        <b>Lunch:</b> Lentil curry with quinoa<br/>
        <b>Pre-Workout:</b> Rice cakes with almond butter<br/>
        <b>Post-Workout:</b> Pea protein shake with oat milk<br/>
        <b>Dinner:</b> Tempeh with sweet potato and broccoli<br/>
        <b>Evening:</b> Mixed nuts and seeds
        """
    else:
        meal_plan = """
        <b>Breakfast:</b> Eggs with whole grain toast and avocado<br/>
        <b>Snack:</b> Protein shake with banana<br/>
        <b>Lunch:</b> Grilled chicken breast with rice and vegetables<br/>
        <b>Pre-Workout:</b> Oatmeal with berries<br/>
        <b>Post-Workout:</b> Whey protein shake<br/>
        <b>Dinner:</b> Salmon with sweet potato and asparagus<br/>
        <b>Evening:</b> Greek yogurt or casein protein
        """
    
    story.append(Paragraph(meal_plan, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Supplements
    story.append(Paragraph("Recommended Supplements (Optional)", styles['Heading3']))
    supplements = "• Whey/Plant Protein Powder<br/>• Creatine Monohydrate (5g daily)<br/>• Vitamin D3<br/>• Omega-3 Fish Oil<br/>• Multivitamin"
    story.append(Paragraph(supplements, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Closing
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("YOUR PROTOCOL STARTS NOW", title_style))
    story.append(Paragraph("Consistency beats perfection. Track your progress weekly and adjust as needed.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============= API ROUTES =============

@api_router.post("/quiz/submit")
async def submit_quiz(answers: QuizAnswers):
    """Submit quiz and get calculations"""
    try:
        # Create quiz response first to get ID
        quiz_data = QuizResponse(
            answers=answers,
            calories=0,
            protein=0,
            carbs=0,
            fats=0,
            training_plan=""
        )
        
        # Calculate macros
        result = calculate_macros(answers)
        
        # Update quiz data with calculations
        quiz_data.calories = result.calories
        quiz_data.protein = result.protein
        quiz_data.carbs = result.carbs
        quiz_data.fats = result.fats
        quiz_data.training_plan = result.training_plan
        
        # Store in database
        doc = quiz_data.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.quiz_responses.insert_one(doc)
        
        # Return with quiz_id
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
        logger.error(f"Error submitting quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/checkout/session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CheckoutRequest, http_request: Request):
    """Create Stripe checkout session"""
    try:
        # Fixed package pricing - NEVER from frontend (₹499 = ~$6 USD)
        PACKAGE_PRICE = 6.00
        
        # Get quiz data to validate
        quiz = await db.quiz_responses.find_one({"id": request.quiz_id}, {"_id": 0})
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Build URLs from origin
        success_url = f"{request.origin_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/results?quiz_id={request.quiz_id}"
        
        # Initialize Stripe
        host_url = str(http_request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=PACKAGE_PRICE,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "quiz_id": request.quiz_id,
                "product": "full_protocol_pdf"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction
        transaction = PaymentTransaction(
            session_id=session.session_id,
            quiz_id=request.quiz_id,
            amount=PACKAGE_PRICE,
            currency="usd",
            payment_status="pending",
            metadata={"quiz_id": request.quiz_id}
        )
        
        doc = transaction.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.payment_transactions.insert_one(doc)
        
        return session
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/checkout/status/{session_id}", response_model=CheckoutStatusResponse)
async def get_checkout_status(session_id: str, http_request: Request):
    """Get checkout session status"""
    try:
        host_url = str(http_request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction in database
        if status.payment_status == "paid":
            # Check if already processed
            existing = await db.payment_transactions.find_one(
                {"session_id": session_id, "payment_status": "paid"},
                {"_id": 0}
            )
            
            if not existing:
                await db.payment_transactions.update_one(
                    {"session_id": session_id},
                    {"$set": {"payment_status": "paid"}}
                )
        
        return status
    except Exception as e:
        logger.error(f"Error getting checkout status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        host_url = str(request.base_url)
        webhook_url = f"{host_url}api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction
        if webhook_response.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {"payment_status": "paid"}}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/pdf/download/{quiz_id}")
async def download_pdf(quiz_id: str):
    """Download personalized PDF (requires payment verification)"""
    try:
        # Check payment status
        payment = await db.payment_transactions.find_one(
            {"quiz_id": quiz_id, "payment_status": "paid"},
            {"_id": 0}
        )
        
        if not payment:
            raise HTTPException(status_code=403, detail="Payment required")
        
        # Get quiz data
        quiz_doc = await db.quiz_responses.find_one({"id": quiz_id}, {"_id": 0})
        if not quiz_doc:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Convert timestamp back to datetime
        if isinstance(quiz_doc['timestamp'], str):
            quiz_doc['timestamp'] = datetime.fromisoformat(quiz_doc['timestamp'])
        
        quiz_data = QuizResponse(**quiz_doc)
        
        # Generate PDF
        pdf_buffer = generate_pdf(quiz_data)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=protocol_{quiz_id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class PaymentSubmission(BaseModel):
    quiz_id: str
    email: str
    screenshot_filename: str

@api_router.post("/payment/submit")
async def submit_payment_proof(submission: PaymentSubmission):
    """Store payment submission with email for manual verification"""
    try:
        # Store payment submission
        payment_doc = {
            "id": str(uuid.uuid4()),
            "quiz_id": submission.quiz_id,
            "email": submission.email,
            "screenshot_filename": submission.screenshot_filename,
            "status": "pending_verification",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payment_method": "fampay_upi"
        }
        
        await db.payment_submissions.insert_one(payment_doc)
        
        return {
            "success": True,
            "message": "Payment proof submitted. You'll receive your PDF within 24 hours.",
            "email": submission.email
        }
    except Exception as e:
        logger.error(f"Error submitting payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/payments/pending")
async def get_pending_payments():
    """Get all pending payment verifications"""
    try:
        payments = await db.payment_submissions.find(
            {"status": "pending_verification"},
            {"_id": 0}
        ).to_list(100)
        return {"payments": payments}
    except Exception as e:
        logger.error(f"Error fetching pending payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/payment/verify/{submission_id}")
async def verify_payment_and_send_pdf(submission_id: str):
    """Admin endpoint to verify payment and send PDF"""
    try:
        # Get payment submission
        submission = await db.payment_submissions.find_one({"id": submission_id}, {"_id": 0})
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get quiz data
        quiz_doc = await db.quiz_responses.find_one({"id": submission["quiz_id"]}, {"_id": 0})
        if not quiz_doc:
            raise HTTPException(status_code=404, detail="Quiz data not found")
        
        # Convert timestamp back to datetime
        if isinstance(quiz_doc['timestamp'], str):
            quiz_doc['timestamp'] = datetime.fromisoformat(quiz_doc['timestamp'])
        
        quiz_data = QuizResponse(**quiz_doc)
        
        # Generate personalized PDF
        pdf_buffer = generate_pdf(quiz_data)
        
        # Mark as verified
        await db.payment_submissions.update_one(
            {"id": submission_id},
            {"$set": {"status": "verified", "verified_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "success": True,
            "message": f"Payment verified. PDF generated for {submission['email']}",
            "email": submission["email"]
        }
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def root():
    return {"message": "PROTOCOL API Ready"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()