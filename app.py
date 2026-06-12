import streamlit as st
import streamlit.components.v1 as components
import math
import re
from word2number import w2n

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
.history-title { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
    color: #374151; margin: 2rem 0 0.8rem; }
.history-item { display: flex; justify-content: space-between; align-items: baseline;
    padding: 0.6rem 0; border-bottom: 1px solid #1c1c2a; gap: 1rem; }
.history-q { color: #6b7280; font-size: 0.88rem; flex: 1; }
.history-a { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; font-weight: 600; color: #818cf8; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ── NLP Math Engine ───────────────────────────────────────────────────────────
def extract_numbers(text: str) -> list:
    """Extract all numbers from text, converting words to numbers."""
    text = text.lower().strip()

    # Replace word numbers with digits
    word_num_pattern = r'\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|point|and)+(\s+(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|point|and))*\b'

    def replace_word_num(m):
        try:
            return str(w2n.word_to_num(m.group(0)))
        except:
            return m.group(0)

    text = re.sub(word_num_pattern, replace_word_num, text)

    # Find all numeric values (including decimals and negatives)
    nums = re.findall(r'-?\d+\.?\d*', text)
    return [float(n) if '.' in n else int(n) for n in nums]


def smart_calculate(text: str) -> dict:
    """Parse natural language and compute result."""
    original = text
    text = text.lower().strip()
    # remove filler words
    text = re.sub(r'\b(what is|what\'s|calculate|compute|find|tell me|give me|please|the|value of|result of|equals?|=)\b', '', text)
    text = text.strip()

    nums = extract_numbers(text)

    # ── Patterns ──────────────────────────────────────────────────────────────

    # Square root
    if re.search(r'square\s*root|sqrt|√', text):
        if nums:
            n = nums[0]
            if n < 0:
                return {"expression": f"√{n}", "result": None, "steps": "Cannot take square root of a negative number."}
            r = math.sqrt(n)
            return {"expression": f"√{n}", "result": round(r, 6), "steps": f"√{n} = {round(r,6)}"}

    # Cube root
    if re.search(r'cube\s*root|cbrt', text):
        if nums:
            n = nums[0]
            r = round(n ** (1/3), 6)
            return {"expression": f"∛{n}", "result": r, "steps": f"∛{n} = {r}"}

    # Factorial
    if re.search(r'factorial|fact\b|!', text):
        if nums:
            n = int(nums[0])
            if n < 0:
                return {"expression": f"{n}!", "result": None, "steps": "Factorial not defined for negative numbers."}
            if n > 20:
                return {"expression": f"{n}!", "result": None, "steps": "Number too large for factorial (max 20)."}
            r = math.factorial(n)
            return {"expression": f"{n}!", "result": r, "steps": f"{n}! = {r}"}

    # Power / exponent
    if re.search(r'power|raised to|exponent|\^|\*\*|to the', text):
        if len(nums) >= 2:
            base, exp = nums[0], nums[1]
            r = base ** exp
            r = round(r, 6) if isinstance(r, float) else r
            return {"expression": f"{base}^{exp}", "result": r, "steps": f"{base} raised to power {exp} = {r}"}

    # Percentage of
    if re.search(r'percent\s*of|%\s*of', text):
        if len(nums) >= 2:
            pct, total = nums[0], nums[1]
            r = round((pct / 100) * total, 6)
            return {"expression": f"{pct}% of {total}", "result": r, "steps": f"{pct}/100 × {total} = {r}"}

    # Percentage (what percent is X of Y)
    if re.search(r'what percent|percentage', text):
        if len(nums) >= 2:
            part, whole = nums[0], nums[1]
            if whole == 0:
                return {"expression": f"{part}/{whole}×100", "result": None, "steps": "Cannot divide by zero."}
            r = round((part / whole) * 100, 4)
            return {"expression": f"({part}/{whole})×100", "result": r, "steps": f"{part} is {r}% of {whole}"}

    # Log base 10
    if re.search(r'\blog\b(?!\s*base|\s*2)', text):
        if nums:
            n = nums[0]
            if n <= 0:
                return {"expression": f"log({n})", "result": None, "steps": "Log undefined for non-positive numbers."}
            r = round(math.log10(n), 6)
            return {"expression": f"log₁₀({n})", "result": r, "steps": f"log₁₀({n}) = {r}"}

    # Log base 2
    if re.search(r'log\s*2|log\s*base\s*2|log₂', text):
        if nums:
            n = nums[0]
            if n <= 0:
                return {"expression": f"log₂({n})", "result": None, "steps": "Log undefined for non-positive numbers."}
            r = round(math.log2(n), 6)
            return {"expression": f"log₂({n})", "result": r, "steps": f"log₂({n}) = {r}"}

    # Natural log
    if re.search(r'\bln\b|natural\s*log', text):
        if nums:
            n = nums[0]
            if n <= 0:
                return {"expression": f"ln({n})", "result": None, "steps": "ln undefined for non-positive numbers."}
            r = round(math.log(n), 6)
            return {"expression": f"ln({n})", "result": r, "steps": f"ln({n}) = {r}"}

    # Sine
    if re.search(r'\bsin\b|sine', text):
        if nums:
            n = nums[0]
            r = round(math.sin(math.radians(n)), 6)
            return {"expression": f"sin({n}°)", "result": r, "steps": f"sin({n}°) = {r}"}

    # Cosine
    if re.search(r'\bcos\b|cosine', text):
        if nums:
            n = nums[0]
            r = round(math.cos(math.radians(n)), 6)
            return {"expression": f"cos({n}°)", "result": r, "steps": f"cos({n}°) = {r}"}

    # Tangent
    if re.search(r'\btan\b|tangent', text):
        if nums:
            n = nums[0]
            r = round(math.tan(math.radians(n)), 6)
            return {"expression": f"tan({n}°)", "result": r, "steps": f"tan({n}°) = {r}"}

    # GCD
    if re.search(r'\bgcd\b|greatest common', text):
        if len(nums) >= 2:
            a, b = int(nums[0]), int(nums[1])
            r = math.gcd(a, b)
            return {"expression": f"GCD({a},{b})", "result": r, "steps": f"GCD of {a} and {b} = {r}"}

    # LCM
    if re.search(r'\blcm\b|least common multiple', text):
        if len(nums) >= 2:
            a, b = int(nums[0]), int(nums[1])
            r = (a * b) // math.gcd(a, b)
            return {"expression": f"LCM({a},{b})", "result": r, "steps": f"LCM of {a} and {b} = {r}"}

    # Modulo / remainder
    if re.search(r'mod(ulo)?|remainder|%(?!\s*of)', text):
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
            if b == 0:
                return {"expression": f"{a} mod {b}", "result": None, "steps": "Cannot mod by zero."}
            r = a % b
            return {"expression": f"{a} mod {b}", "result": r, "steps": f"{a} mod {b} = {r}"}

    # Average / mean
    if re.search(r'average|mean|avg', text):
        if nums:
            r = round(sum(nums) / len(nums), 6)
            return {"expression": f"avg({', '.join(str(n) for n in nums)})", "result": r,
                    "steps": f"Sum {sum(nums)} ÷ {len(nums)} = {r}"}

    # Absolute value
    if re.search(r'absolute|abs\b|\|', text):
        if nums:
            n = nums[0]
            return {"expression": f"|{n}|", "result": abs(n), "steps": f"|{n}| = {abs(n)}"}

    # Pi
    if re.search(r'\bpi\b|π', text):
        r = round(math.pi, 6)
        return {"expression": "π", "result": r, "steps": f"π ≈ {r}"}

    # Division
    if re.search(r'divid|÷|over\b|per\b|by\b|/', text):
        if len(nums) >= 2:
            a, b = nums[0], nums[1]
            if b == 0:
                return {"expression": f"{a} ÷ {b}", "result": None, "steps": "Cannot divide by zero."}
            r = a / b
            r = round(r, 6)
            return {"expression": f"{a} ÷ {b}", "result": r, "steps": f"{a} divided by {b} = {r}"}

    # Multiplication
    if re.search(r'multi|times|product|\*|×', text):
        if len(nums) >= 2:
            r = nums[0]
            for n in nums[1:]:
                r *= n
            r = round(r, 6) if isinstance(r, float) else r
            return {"expression": " × ".join(str(n) for n in nums), "result": r,
                    "steps": f"Product of {nums} = {r}"}

    # Subtraction
    if re.search(r'subtract|minus|deduct|less|difference|take away|−|-', text):
        if len(nums) >= 2:
            r = nums[0]
            for n in nums[1:]:
                r -= n
            return {"expression": " − ".join(str(n) for n in nums), "result": r,
                    "steps": f"{nums[0]} minus {' minus '.join(str(n) for n in nums[1:])} = {r}"}

    # Addition (default if numbers exist)
    if re.search(r'add|plus|sum|total|\+', text) or len(nums) >= 2:
        if nums:
            r = sum(nums)
            r = round(r, 6) if isinstance(r, float) else r
            return {"expression": " + ".join(str(n) for n in nums), "result": r,
                    "steps": f"Sum of {nums} = {r}"}

    # Single number entered
    if len(nums) == 1:
        return {"expression": str(nums[0]), "result": nums[0], "steps": "Single value returned."}

    return {"expression": original, "result": None, "steps": "Sorry, I couldn't understand that. Try: 'add 5 and 3', 'sqrt of 16', '20% of 500'."}


# ── Voice Component ───────────────────────────────────────────────────────────
def voice_input_component():
    voice_html = """
    <div style="margin-bottom: 1rem;">
        <button id="micBtn" onclick="toggleMic()" style="
            background: linear-gradient(135deg, #7c3aed, #4f46e5);
            color: white; border: none; border-radius: 10px;
            padding: 0.6rem 1.4rem; font-size: 0.95rem;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600; cursor: pointer; display: flex;
            align-items: center; gap: 0.5rem; transition: opacity 0.2s;">
            🎤 Speak
        </button>
        <div id="statusMsg" style="margin-top: 0.5rem; font-size: 0.82rem; color: #6b7280; min-height: 1.2rem;"></div>
        <div id="transcript" style="
            margin-top: 0.5rem; background: #15151f; border: 1.5px solid #2a2a3d;
            border-radius: 10px; padding: 0.6rem 1rem; font-size: 0.95rem;
            color: #c084fc; font-family: 'JetBrains Mono', monospace;
            min-height: 2rem; display: none;"></div>
        <button id="useBtn" onclick="useTranscript()" style="
            display: none; margin-top: 0.5rem;
            background: #1a1a2e; color: #818cf8;
            border: 1px solid #818cf8; border-radius: 8px;
            padding: 0.4rem 1rem; font-size: 0.85rem;
            font-family: 'Space Grotesk', sans-serif; cursor: pointer;">
            ✓ Use this
        </button>
    </div>

    <script>
    let recognition = null;
    let listening = false;
    let lastTranscript = "";

    function toggleMic() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            document.getElementById('statusMsg').innerHTML =
                '⚠️ Speech not supported. Use Chrome or Edge.';
            return;
        }
        if (listening) {
            recognition.stop();
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            listening = true;
            document.getElementById('micBtn').innerHTML = '⏹ Stop';
            document.getElementById('micBtn').style.background = 'linear-gradient(135deg,#dc2626,#b91c1c)';
            document.getElementById('statusMsg').innerHTML = '🔴 Listening…';
            document.getElementById('transcript').style.display = 'none';
            document.getElementById('useBtn').style.display = 'none';
        };

        recognition.onresult = (e) => {
            let interim = '';
            let final = '';
            for (let i = e.resultIndex; i < e.results.length; i++) {
                const t = e.results[i][0].transcript;
                if (e.results[i].isFinal) final += t;
                else interim += t;
            }
            const display = final || interim;
            lastTranscript = display;
            document.getElementById('transcript').style.display = 'block';
            document.getElementById('transcript').innerText = display;
            if (final) {
                document.getElementById('useBtn').style.display = 'inline-block';
            }
        };

        recognition.onerror = (e) => {
            document.getElementById('statusMsg').innerHTML = '❌ Error: ' + e.error;
            resetMic();
        };

        recognition.onend = () => {
            if (lastTranscript) {
                document.getElementById('statusMsg').innerHTML = '✅ Done — click "Use this" to calculate.';
                document.getElementById('useBtn').style.display = 'inline-block';
            } else {
                document.getElementById('statusMsg').innerHTML = 'No speech detected. Try again.';
            }
            resetMic();
        };

        recognition.start();
    }

    function resetMic() {
        listening = false;
        document.getElementById('micBtn').innerHTML = '🎤 Speak';
        document.getElementById('micBtn').style.background = 'linear-gradient(135deg,#7c3aed,#4f46e5)';
    }

    function useTranscript() {
        if (lastTranscript) {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: lastTranscript}, '*');
        }
    }
    </script>
    """
    return components.html(voice_html, height=160)

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Smart Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Type or speak your math query — no API, works offline.</div>', unsafe_allow_html=True)

# Voice component
st.markdown("**🎤 Voice Input** *(Chrome/Edge only)*")
voice_result = voice_input_component()

# Check if voice sent a value
if voice_result and isinstance(voice_result, str) and voice_result.strip():
    st.session_state.voice_text = voice_result.strip()

# Example pills
examples = ["Add 25 and 30", "15% of 200", "sqrt of 144", "2 to the power 10",
            "factorial of 7", "sin 30", "GCD of 12 and 18", "average of 10 20 30"]
cols = st.columns(4)
for i, ex in enumerate(examples):
    if cols[i % 4].button(ex, key=f"pill_{i}"):
        st.session_state.voice_text = ex

# Main input
user_input = st.text_input("", placeholder="e.g. What is 12% of 850?",
    value=st.session_state.voice_text, key="main_input", label_visibility="collapsed")
calculate = st.button("Calculate →")

if calculate and user_input.strip():
    data = smart_calculate(user_input.strip())
    if data["result"] is None:
        st.markdown(f'<div class="error-card">⚠️ {data["steps"]}</div>', unsafe_allow_html=True)
    else:
        r = data["result"]
        result_display = f"{r:,}" if isinstance(r, int) else f"{r:,.10g}"
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Result</div>
            <div class="result-value">{result_display}</div>
            <div class="result-expr">{data['expression']} &nbsp;·&nbsp; {data['steps']}</div>
        </div>""", unsafe_allow_html=True)
        st.session_state.history.insert(0, {"q": user_input.strip(), "result": result_display})
        st.session_state.history = st.session_state.history[:10]
        st.session_state.voice_text = ""

# History
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
