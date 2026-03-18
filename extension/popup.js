/**
 * popup.js — VeriFact AI Extension
 * Handles UI state transitions, text extraction, and API communication.
 */

const API_URL = "http://localhost:8000/api/v1/analyze";

// ── DOM Refs ────────────────────────────────────────────────────────────────
const states = {
  idle:    document.getElementById("idle-state"),
  loading: document.getElementById("loading-state"),
  error:   document.getElementById("error-state"),
  result:  document.getElementById("result-state"),
};

const analyzeBtn  = document.getElementById("analyze-btn");
const retryBtn    = document.getElementById("retry-btn");
const resetBtn    = document.getElementById("reset-btn");
const errorMsg    = document.getElementById("error-message");
const scoreValue  = document.getElementById("score-value");
const ringProgress = document.getElementById("ring-progress");
const riskBadge   = document.getElementById("risk-badge");
const flagsList   = document.getElementById("flags-list");
const sourceLabel = document.getElementById("source-label");

// Circumference = 2π × r = 2π × 52 ≈ 326.726
const RING_CIRCUMFERENCE = 2 * Math.PI * 52;

// ── State Machine ────────────────────────────────────────────────────────────
function showState(name) {
  Object.values(states).forEach(el => el.classList.add("hidden"));
  states[name].classList.remove("hidden");
}

// ── Score Ring Animation ─────────────────────────────────────────────────────
function animateScore(score) {
  // Map score (0–100) to stroke-dashoffset
  const offset = RING_CIRCUMFERENCE * (1 - score / 100);

  // Color thresholds
  let color;
  if (score >= 70) color = "#48bb78";       // green
  else if (score >= 40) color = "#ed8936";  // amber
  else color = "#f56565";                   // red

  // Trigger animation (small delay lets CSS transition pick up)
  requestAnimationFrame(() => {
    ringProgress.style.strokeDashoffset = offset;
    ringProgress.style.stroke = color;
    scoreValue.style.color = color;
  });

  scoreValue.textContent = score;
}

// ── Render Result ─────────────────────────────────────────────────────────────
function renderResult(data, source) {
  showState("result");

  // Reset ring to empty before animating
  ringProgress.style.transition = "none";
  ringProgress.style.strokeDashoffset = RING_CIRCUMFERENCE;
  void ringProgress.offsetWidth; // force reflow
  ringProgress.style.transition = "";

  animateScore(data.credibility_score);

  // Risk badge
  const level = (data.risk_level || "").toLowerCase();
  riskBadge.textContent = `${data.risk_level} Risk`;
  riskBadge.className = `risk-badge ${level}`;

  // Flags
  flagsList.innerHTML = "";
  (data.flags || []).forEach(flag => {
    const li = document.createElement("li");
    li.textContent = flag;
    // Mark "all clear" flags differently
    if (flag.toLowerCase().includes("no major")) li.classList.add("ok");
    flagsList.appendChild(li);
  });

  // Source
  sourceLabel.textContent =
    source === "selection"
      ? "📌 Analyzed: highlighted text"
      : "📄 Analyzed: full page content";
}

// ── API Call ──────────────────────────────────────────────────────────────────
async function analyzeText(text, source) {
  showState("loading");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${response.status}`);
    }

    const data = await response.json();
    renderResult(data, source);

  } catch (err) {
    showState("error");
    if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
      errorMsg.textContent =
        "⚡ Cannot reach backend. Make sure the FastAPI server is running on http://localhost:8000";
    } else {
      errorMsg.textContent = `Error: ${err.message}`;
    }
  }
}

// ── Extract Text from Active Tab ──────────────────────────────────────────────
async function getTabText() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0) {
        return reject(new Error("No active tab found."));
      }
      const tabId = tabs[0].id;

      // Inject content script if not already present (safe to call multiple times)
      chrome.scripting.executeScript(
        { target: { tabId }, files: ["content.js"] },
        () => {
          // Ignore injection errors (already injected is fine)
          chrome.runtime.lastError;
          chrome.tabs.sendMessage(tabId, { action: "getSelectedText" }, (resp) => {
            if (chrome.runtime.lastError) {
              return reject(new Error(chrome.runtime.lastError.message));
            }
            if (!resp || !resp.text || resp.text.trim().length === 0) {
              return reject(new Error("No text found on this page."));
            }
            resolve(resp);
          });
        }
      );
    });
  });
}

// ── Button Handlers ───────────────────────────────────────────────────────────
analyzeBtn.addEventListener("click", async () => {
  try {
    const { text, source } = await getTabText();
    await analyzeText(text, source);
  } catch (err) {
    showState("error");
    errorMsg.textContent = err.message;
  }
});

retryBtn.addEventListener("click", () => showState("idle"));
resetBtn.addEventListener("click", () => showState("idle"));
