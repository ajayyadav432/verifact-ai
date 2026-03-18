# VeriFact AI 🛡️
> **AI-Based Fake News Detection System** — Hackathon Prototype

VeriFact AI is a lightweight browser extension + Python backend that detects sensationalist and potentially misleading content in real time. Highlight any text on a webpage, click the extension, and receive an instant credibility score.

---

## 📁 Project Structure

```
MNIT/
├── backend/
│   ├── main.py            # FastAPI app — CORS, routing
│   ├── analyzer.py        # Mock NLP rule-based analyzer
│   └── requirements.txt
└── extension/
    ├── manifest.json      # Manifest V3
    ├── popup.html         # Extension popup UI
    ├── popup.css          # Styling
    ├── popup.js           # UI logic & API calls
    ├── content.js         # Text extraction from page
    └── icons/             # Extension icons (16, 48, 128px)
```

---

## 🚀 Quick Start

### 1. Backend Setup (FastAPI)

```bash
# Navigate to the backend folder
cd MNIT/backend

# (Recommended) Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at **http://localhost:8000**  
Interactive docs available at **http://localhost:8000/docs**

---

### 2. Test the API (optional)

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"SHOCKING TRUTH!!! They don't want you to know this secret conspiracy!!!\"}"
```

---

### 3. Load the Extension in Chrome / Edge

1. Open your browser and go to: `chrome://extensions` (or `edge://extensions`)
2. Enable **Developer Mode** (toggle in the top-right corner)
3. Click **"Load unpacked"**
4. Select the `MNIT/extension/` folder
5. The **VeriFact AI** extension will appear in your toolbar 🎉

---

## 🧠 How the AI Works

The analyzer scores text from **0 (not credible) to 100 (credible)** using 7 rule-based heuristics:

| Rule | Penalty |
|------|---------|
| Heavy ALL-CAPS usage (>30% of words) | −30 pts |
| Moderate ALL-CAPS usage (>10%) | −15 pts |
| Excessive exclamation marks (≥3) | Up to −25 pts |
| Excessive question marks (≥3) | Up to −15 pts |
| Sensationalist / clickbait keywords | Up to −35 pts |
| Absolute/superlative claims | Up to −20 pts |
| Source-undermining language | −25 pts |
| Repeated characters (e.g., "omgggg") | −10 pts |

**Risk Levels:**
- 🟢 **Low** — Score ≥ 70
- 🟡 **Medium** — Score 40–69
- 🔴 **High** — Score < 40

---

## 🔌 API Reference

**POST** `/api/v1/analyze`

**Request:**
```json
{ "text": "string" }
```

**Response:**
```json
{
  "credibility_score": 42,
  "risk_level": "Medium",
  "flags": [
    "Sensationalist / clickbait language detected: 'shocking, secret'",
    "Excessive exclamation marks (3×'!') — common in clickbait content"
  ]
}
```

---

## ✨ Features

- ⚡ Zero ML model downloads — runs entirely on rule-based NLP
- 🎨 Animated credibility score ring (color-coded)
- 📌 Analyzes highlighted text **or** full page content
- 🔍 Detailed explainable flags for each detected issue
- 🌙 Sleek dark-mode UI

---

*Built for hackathon purposes. Extend `analyzer.py` to plug in a real transformer model (e.g., `transformers` + `distilbert-base-uncased`) for production use.*
