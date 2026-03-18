"""
VeriFact AI - Mock NLP Analyzer
Uses advanced rule-based string analysis and regex to evaluate
text credibility without heavy ML model dependencies.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalysisResult:
    credibility_score: int
    risk_level: str
    flags: List[str] = field(default_factory=list)


# Sensationalist / clickbait keyword patterns
SENSATIONALIST_KEYWORDS = [
    r"\bshocking\b", r"\bblasting\b", r"\bbombshell\b", r"\bexposed\b",
    r"\bbreaking\b", r"\burgent\b", r"\bcrisis\b", r"\balert\b",
    r"\bscandal\b", r"\boutrage\b", r"\bconspiracy\b", r"\bhoax\b",
    r"\btruth\s+revealed\b", r"\bthey\s+don'?t\s+want\s+you\s+to\s+know\b",
    r"\bwake\s+up\b", r"\bdo\s+this\s+now\b", r"\bacts?\s+of\s+god\b",
    r"\bmiracle\b", r"\bcure\b", r"\bsecret\b", r"\bhidden\s+agenda\b",
    r"\bcensored\b", r"\bsuppressed\b", r"\bproof\b", r"\bclickbait\b",
    r"\bviral\b", r"\bunbelievable\b", r"\bincredible\b", r"\bamazing\b",
    r"\bstunning\b", r"\bdevastating\b", r"\bdisgusting\b", r"\bfuming\b",
    r"\brage\b", r"\bhate\b", r"\bdestroy\b", r"\beliminate\b",
    r"\bmarks?\s+end\b", r"\bwill\s+shock\b", r"\bcan'?t\s+believe\b",
    r"\bmust\s+see\b", r"\bmust\s+watch\b", r"\bshare\s+before\s+deleted\b",
    r"\bfake\s+news\b", r"\bdeep\s+state\b", r"\bnew\s+world\s+order\b",
    r"\bplandemic\b", r"\bpsy-?op\b",
]

# Emotional superlatives / absolutes
ABSOLUTE_PHRASES = [
    r"\beveryone\s+knows\b", r"\bno\s+one\s+is\s+talking\b",
    r"\ball\s+scientists\s+agree\b", r"\bproven\s+fact\b",
    r"\b100\s*%\s+(guaranteed|proven|confirmed)\b",
    r"\bcompletely\s+(false|true|proven|debunked)\b",
    r"\bdefinitely\b", r"\bwithout\s+a\s+doubt\b",
    r"\(MUST\s+READ\)", r"\(MUST\s+WATCH\)",
]

# Source-undermining patterns
CREDIBILITY_UNDERMINING = [
    r"\bmainstream\s+media\s+(lie|lied|lying|hides|hiding)\b",
    r"\bgovernment\s+(lie|cover.?up|hiding)\b",
    r"\bfact.?checker[s]?\s+(are\s+wrong|lied|paid)\b",
    r"\bdo\s+your\s+own\s+research\b",
    r"\bdoyo[u]?r\s+own\s+research\b",
    r"\bwake\s+up\s+sheeple\b",
]


class FakeNewsAnalyzer:
    """
    Rule-based credibility analyzer that checks text for common
    patterns associated with misinformation and sensationalism.
    """

    def __init__(self):
        self._sensationalist_patterns = [
            re.compile(p, re.IGNORECASE) for p in SENSATIONALIST_KEYWORDS
        ]
        self._absolute_patterns = [
            re.compile(p, re.IGNORECASE) for p in ABSOLUTE_PHRASES
        ]
        self._credibility_patterns = [
            re.compile(p, re.IGNORECASE) for p in CREDIBILITY_UNDERMINING
        ]

    def analyze(self, text: str) -> AnalysisResult:
        flags: List[str] = []
        penalty = 0

        # --- Rule 1: Excessive ALL-CAPS words ---
        words = text.split()
        if words:
            caps_words = [w for w in words if w.isupper() and len(w) > 2]
            caps_ratio = len(caps_words) / len(words)
            if caps_ratio > 0.3:
                flags.append("Heavy use of ALL-CAPS — often signals sensationalism or emotional manipulation")
                penalty += 30
            elif caps_ratio > 0.1:
                flags.append("Elevated ALL-CAPS usage detected")
                penalty += 15

        # --- Rule 2: Excessive punctuation (!!! / ???) ---
        exclamation_count = text.count("!")
        question_count = text.count("?")
        if exclamation_count >= 3:
            flags.append(f"Excessive exclamation marks ({exclamation_count}×'!') — common in clickbait content")
            penalty += min(exclamation_count * 5, 25)
        if question_count >= 3:
            flags.append(f"Excessive question marks ({question_count}×'?') — may indicate rhetorical manipulation")
            penalty += min(question_count * 3, 15)

        # --- Rule 3: Sensationalist keywords ---
        matched_keywords = []
        for pattern in self._sensationalist_patterns:
            m = pattern.search(text)
            if m:
                matched_keywords.append(m.group(0).lower())
        if matched_keywords:
            unique_kw = list(dict.fromkeys(matched_keywords))[:5]  # cap at 5
            flags.append(
                f"Sensationalist / clickbait language detected: '{', '.join(unique_kw)}'"
            )
            penalty += min(len(matched_keywords) * 8, 35)

        # --- Rule 4: Absolute / superlative claims ---
        matched_absolutes = []
        for pattern in self._absolute_patterns:
            m = pattern.search(text)
            if m:
                matched_absolutes.append(m.group(0).strip())
        if matched_absolutes:
            flags.append("Absolute/superlative claims detected — credible sources acknowledge nuance")
            penalty += min(len(matched_absolutes) * 10, 20)

        # --- Rule 5: Source-undermining language ---
        matched_undermine = []
        for pattern in self._credibility_patterns:
            m = pattern.search(text)
            if m:
                matched_undermine.append(m.group(0).strip())
        if matched_undermine:
            flags.append("Text undermines credible sources or fact-checkers — a common misinformation tactic")
            penalty += 25

        # --- Rule 6: Very short text (unreliable sample) ---
        if len(text.strip()) < 40:
            flags.append("Text is very short — analysis may be less reliable")
            penalty += 5

        # --- Rule 7: Repeating characters (e.g. "omggggg", "!!!!!!") ---
        if re.search(r"(.)\1{3,}", text):
            flags.append("Repeated characters detected — informal or emotionally charged writing style")
            penalty += 10

        # --- Calculate final score ---
        credibility_score = max(0, min(100, 100 - penalty))

        if credibility_score >= 70:
            risk_level = "Low"
        elif credibility_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "High"

        if not flags:
            flags.append("No major credibility concerns detected in the analyzed text")

        return AnalysisResult(
            credibility_score=credibility_score,
            risk_level=risk_level,
            flags=flags,
        )
