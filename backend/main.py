"""
VeriFact AI — FastAPI Backend
Exposes /api/v1/analyze endpoint for credibility analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from analyzer import FakeNewsAnalyzer

# ── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="VeriFact AI",
    description="AI-Based Fake News Detection API",
    version="1.0.0",
)

# Allow requests from browser extensions (chrome-extension:// or any origin
# during local development). Do NOT use wildcard in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

analyzer = FakeNewsAnalyzer()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze for credibility")


class AnalyzeResponse(BaseModel):
    credibility_score: int
    risk_level: str
    flags: list[str]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "VeriFact AI is running", "docs": "/docs"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_text(payload: AnalyzeRequest):
    """
    Analyze a piece of text for credibility using rule-based NLP heuristics.

    Returns:
    - **credibility_score**: Integer 0-100 (higher = more credible)
    - **risk_level**: "Low" | "Medium" | "High"
    - **flags**: List of human-readable explanations for detected issues
    """
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Text must not be blank.")

    result = analyzer.analyze(payload.text)
    return AnalyzeResponse(
        credibility_score=result.credibility_score,
        risk_level=result.risk_level,
        flags=result.flags,
    )
