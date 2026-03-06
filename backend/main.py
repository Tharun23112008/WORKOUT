from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Workout API")

# Allow your frontend (Vercel) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you should restrict this to your Vercel domain
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
