import streamlit as st
import google.generativeai as genai
import json, re, os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Smart Calculator", page_icon="🧮", layout="centered")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; background-color: #0d0d14; color: #e8e4f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 1.5rem 4rem; max-width: 680px; }
.hero-title { font-size: 2.8rem; font-weight: 700; letter-spacing: -0.04em; line-height: 1.1;
    background: linear-gradient(135deg, #c084fc 0%, #818cf8 60%, #38bdf8 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.2rem; }
.hero-sub { font-size: 0.95rem; color: #6b7280; font-weight: 400; margin-bottom: 2rem; }
.stTextInput > div > div > input { background: #15151f !important; border: 1.5px solid #2a2a3d !important;
    border-radius: 12px !important; color: #e8e4f0 !important; font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important; padding: 0.85rem 1.1rem !important; }
.stTextInput > div > div > input:focus { border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129,140,248,0.15) !important; }
.stTextInput > div > div > input::placeholder { color: #3d3d55 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: #fff !important;
    border: none !important; border-radius: 10px !important; font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important; font-size: 0.95rem !important; padding: 0.7rem 2rem !important; }
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.result-card { background: #15151f; border: 1.5px solid #2a2a3d; border-radius: 14px; padding: 1.4rem 1.6rem; margin-top: 1.4rem; }
.result-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #4f46e5; margin-bottom: 0.4rem; }
.result-value { font-family: 'JetBrains Mono', monospace; font-size: 2.4rem; font-weight: 600; color: #c084fc; line-height: 1.2; }
.result-expr { font-size: 0.85rem; color: #4b5563; margin-top: 0.35rem; font-family: 'JetBrains Mono', monospace; }
.error-card { background: #1a0f1f; border: 1.5px solid #5b1f3c; border-radius: 14px; padding: 1.1rem 1.4rem;
    margin-top: 1.4rem; color: #f87171; font-size: 0.9rem; }
.history-title { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #374151; margin: 2rem 0 0.8rem; }
.history-item { display: flex; justify-content: space-between; align-items: baseline; padding: 0.6rem 0; border-bottom: 1px solid #1c1c2a; gap: 1rem; }
.history-q { color: #6b7280; font-size: 0.88rem; flex: 1; }
.history-a { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600; color: #818cf8; white-space: nowrap; }
.api-box { background: #15151f; border: 1.5px solid #2a2a3d; border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem; }
.api-box a { color: #818cf8; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Smart Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Type math in plain English — powered by Google Gemini.</div>', unsafe_allow_html=True)

# ── API Key input ─────────────────────────────────────────────────────────────
# Check secrets first (for Streamlit Cloud deployment), then env, then manual input
api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.markdown("""
    <div class="api-box">
        🔑 <strong>Enter your free Gemini API key</strong> to get started.<br>
        <small>Get one free at <a href="https://aistudio.google.com" target="_blank">aistudio.google.com</a> → Get API Key</small>
    </div>
    """, unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")

# ── Gemini helper ─────────────────────────────────────────────────────────────
PROMPT = """You are a math computation engine.
Parse the user's natural language math question, compute the answer, and reply ONLY in this JSON format (no markdown, no extra text):
{"expression": "<concise math expression>", "result": <numeric answer as a number>, "steps": "<one-line explanation>"}
If not a math question, set result to null and steps to "Not a math question."
Examples:
- "Add 25 and 30" → {"expression": "25 + 30", "result": 55, "steps": "Simple addition."}
- "15% of 200" → {"expression": "15% × 200", "result": 30, "steps": "15/100 × 200 = 30"}
- "square root of 144" → {"expression": "√144", "result": 12, "steps": "√144 = 12"}
"""

def ask_gemini(query: str, key: str) -> dict:
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(PROMPT + f"\nUser: {query}")
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ── Example pills ─────────────────────────────────────────────────────────────
examples = ["Add 25 and 30", "15% of 200", "Square root of 144", "2 to the power of 10", "Factorial of 7", "1000 divided by 8"]
cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    if cols[i].button(ex, key=f"pill_{i}"):
        st.session_state.input_value = ex

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.text_input("", placeholder="e.g.  What is 12% of 850?",
    value=st.session_state.input_value, key="main_input", label_visibility="collapsed")
calculate = st.button("Calculate →")

# ── Compute ───────────────────────────────────────────────────────────────────
if calculate and user_input.strip():
    if not api_key:
        st.markdown('<div class="error-card">⚠️ Please enter your Gemini API key above.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Thinking…"):
            try:
                data = ask_gemini(user_input.strip(), api_key)
                if data.get("result") is None:
                    st.markdown(f'<div class="error-card">⚠️ {data.get("steps", "Not a math question.")}</div>', unsafe_allow_html=True)
                else:
                    r = data["result"]
                    result_display = f"{r:,}" if isinstance(r, int) else f"{r:,.10g}"
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-label">Result</div>
                        <div class="result-value">{result_display}</div>
                        <div class="result-expr">{data.get('expression','')} &nbsp;·&nbsp; {data.get('steps','')}</div>
                    </div>""", unsafe_allow_html=True)
                    st.session_state.history.insert(0, {"q": user_input.strip(), "result": result_display})
                    st.session_state.history = st.session_state.history[:10]
            except Exception as e:
                st.markdown(f'<div class="error-card">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown('<div class="history-title">History</div>', unsafe_allow_html=True)
    for item in st.session_state.history:
        st.markdown(f"""<div class="history-item">
            <span class="history-q">{item['q']}</span>
            <span class="history-a">{item['result']}</span>
        </div>""", unsafe_allow_html=True)
    if st.button("Clear history"):
        st.session_state.history = []
        st.rerun()
