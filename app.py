import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Smart Calculator", page_icon="🧮", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
body,.stApp{
  background-color:#f0f2f8;
  background-image:linear-gradient(rgba(99,102,241,0.07) 1px,transparent 1px),
    linear-gradient(90deg,rgba(99,102,241,0.07) 1px,transparent 1px);
  background-size:32px 32px;
}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 1.5rem 4rem;max-width:640px;}
.hero-wrap{text-align:center;margin-bottom:1.8rem;}
.hero-title{font-size:2.4rem;font-weight:700;letter-spacing:-0.04em;color:#1a1a2e;line-height:1.1;margin-bottom:0.3rem;}
.hero-title span{color:#6366f1;}
.hero-sub{font-size:0.9rem;color:#6b7280;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
  <div class="hero-title">AI Smart <span>Calculator</span></div>
  <div class="hero-sub">Type or speak — works instantly, no API needed.</div>
</div>
""", unsafe_allow_html=True)

# ── Single self-contained component: all math + voice in JS, no Streamlit round-trip ──
CALCULATOR_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Inter',sans-serif;background:transparent;color:#1a1a2e;padding:0 2px 16px;}

.result-card{background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:14px;
  padding:1.4rem 1.6rem;margin-bottom:1.2rem;box-shadow:0 6px 24px rgba(99,102,241,0.3);
  animation:popIn .3s cubic-bezier(.34,1.56,.64,1) both;}
.result-label{font-size:.68rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:rgba(255,255,255,.7);margin-bottom:.3rem;}
.result-value{font-family:'JetBrains Mono',monospace;font-size:2.4rem;font-weight:700;color:#fff;line-height:1.1;}
.result-expr{font-size:.8rem;color:rgba(255,255,255,.65);margin-top:.4rem;font-family:'JetBrains Mono',monospace;}
.error-card{background:#fff5f5;border:1px solid #fecaca;border-radius:12px;
  padding:.9rem 1.2rem;margin-bottom:1rem;color:#dc2626;font-size:.88rem;}

.calc-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;padding:1.4rem 1.6rem;
  box-shadow:0 4px 24px rgba(99,102,241,0.08);}
.section-label{font-size:.72rem;font-weight:600;color:#9ca3af;text-transform:uppercase;
  letter-spacing:.08em;margin-bottom:.55rem;}

.voice-row{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin-bottom:.5rem;}
.btn-mic{background:#6366f1;color:#fff;border:none;border-radius:9px;padding:.5rem 1.2rem;
  font-size:.88rem;font-family:'Inter',sans-serif;font-weight:600;cursor:pointer;
  box-shadow:0 2px 8px rgba(99,102,241,.25);transition:background .15s;}
.btn-mic:hover{background:#4f46e5;}
.btn-mic.listening{background:#dc2626;}
.btn-use{background:#fff;color:#6366f1;border:1.5px solid #6366f1;border-radius:7px;
  padding:.32rem .85rem;font-size:.82rem;font-family:'Inter',sans-serif;font-weight:600;
  cursor:pointer;display:none;transition:background .15s;}
.btn-use:hover{background:#f5f3ff;}
.status{font-size:.78rem;color:#6b7280;}
.transcript{display:none;margin-top:.5rem;background:#f5f3ff;border:1.5px solid #c4b5fd;
  border-radius:9px;padding:.5rem .9rem;font-size:.9rem;color:#4f46e5;
  font-family:'JetBrains Mono',monospace;word-break:break-word;}

.input-row{display:flex;gap:.6rem;margin:1rem 0 .8rem;}
.main-input{flex:1;background:#f8f9fc;border:1.5px solid #e0e2ef;border-radius:10px;
  color:#1a1a2e;font-family:'Inter',sans-serif;font-size:1rem;padding:.75rem 1rem;outline:none;
  transition:border-color .15s,box-shadow .15s;}
.main-input:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.12);background:#fff;}
.main-input::placeholder{color:#a0a8c0;}
.btn-calc{background:#6366f1;color:#fff;border:none;border-radius:9px;
  font-family:'Inter',sans-serif;font-weight:600;font-size:.9rem;padding:.75rem 1.4rem;
  cursor:pointer;box-shadow:0 2px 8px rgba(99,102,241,.25);white-space:nowrap;transition:background .15s;}
.btn-calc:hover{background:#4f46e5;}

.pills{display:flex;flex-wrap:wrap;gap:.4rem;}
.pill{background:#f5f3ff;color:#6366f1;border:1px solid #e0dbff;border-radius:7px;
  padding:.28rem .7rem;font-size:.78rem;font-weight:500;cursor:pointer;
  font-family:'Inter',sans-serif;transition:background .15s;}
.pill:hover{background:#ede9fe;}

.history-section{margin-top:1.2rem;}
.history-title{font-size:.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  color:#9ca3af;margin-bottom:.55rem;}
.history-item{display:flex;justify-content:space-between;align-items:center;
  padding:.5rem .8rem;border-radius:8px;margin-bottom:.22rem;
  background:#fff;border:1px solid #f0f0f8;transition:background .15s;}
.history-item:hover{background:#f5f3ff;}
.history-q{color:#6b7280;font-size:.85rem;flex:1;margin-right:.5rem;word-break:break-word;}
.history-a{font-family:'JetBrains Mono',monospace;font-size:.9rem;font-weight:700;color:#6366f1;white-space:nowrap;}
.btn-clear{margin-top:.8rem;background:#fff;color:#9ca3af;border:1px solid #e5e7eb;
  border-radius:8px;padding:.35rem .9rem;font-size:.8rem;font-family:'Inter',sans-serif;
  cursor:pointer;transition:all .15s;}
.btn-clear:hover{background:#fff5f5;color:#dc2626;border-color:#fecaca;}

@keyframes popIn{from{opacity:0;transform:scale(.93)}to{opacity:1;transform:scale(1)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>

<div id="resultArea"></div>

<div class="calc-card">
  <div class="section-label">🎤 Voice Input <span style="font-weight:400;text-transform:none;letter-spacing:0">(Chrome / Edge only)</span></div>
  <div class="voice-row">
    <button class="btn-mic" id="micBtn" onclick="toggleMic()">🎤 Speak</button>
    <button class="btn-use" id="useBtn" onclick="useTranscript()">✓ Use this</button>
    <span class="status" id="statusMsg"></span>
  </div>
  <div class="transcript" id="transcript"></div>

  <div class="input-row">
    <input class="main-input" id="mainInput" type="text" placeholder="e.g. What is 15% of 850?"
      onkeydown="if(event.key==='Enter')runCalc()">
    <button class="btn-calc" onclick="runCalc()">Calculate →</button>
  </div>

  <div class="section-label">Try an example</div>
  <div class="pills" id="pillsRow"></div>
</div>

<div class="history-section" id="historySection" style="display:none">
  <div class="history-title">Recent calculations</div>
  <div id="historyList"></div>
  <button class="btn-clear" onclick="clearHistory()">Clear history</button>
</div>

<script>
// ── Math engine (JS port) ────────────────────────────────────────────────────
const WORD_NUMS={zero:0,one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,
  ten:10,eleven:11,twelve:12,thirteen:13,fourteen:14,fifteen:15,sixteen:16,seventeen:17,
  eighteen:18,nineteen:19,twenty:20,thirty:30,forty:40,fifty:50,sixty:60,seventy:70,
  eighty:80,ninety:90,hundred:100,thousand:1000,million:1e6,billion:1e9};

function wordsToNum(text){
  const ws=text.toLowerCase().split(/\\s+/);
  let result=0,current=0;
  for(const w of ws){
    if(w in WORD_NUMS){
      const n=WORD_NUMS[w];
      if(n===100) current=(current||1)*100;
      else if(n>=1000){result=(result+(current||1))*n;current=0;}
      else current+=n;
    }
  }
  return result+current;
}

function extractNumbers(text){
  text=text.toLowerCase();
  const wordPat=/\\b(?:(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion)(?:\\s+(?:and\\s+)?(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion))*)\\b/g;
  text=text.replace(wordPat,m=>{try{const v=wordsToNum(m);return String(v);}catch(e){return m;}});
  const ms=[...text.matchAll(/-?\\d+\\.?\\d*/g)];
  return ms.map(m=>m[0].includes('.')?parseFloat(m[0]):parseInt(m[0]));
}

function fmt(r){
  if(Number.isInteger(r)) return r.toLocaleString();
  const s=parseFloat(r.toPrecision(10));
  return s.toLocaleString(undefined,{maximumSignificantDigits:10});
}

function smartCalc(text){
  const original=text;
  let t=text.toLowerCase().trim()
    .replace(/\\b(what is|what's|calculate|compute|find|tell me|give me|please|the|value of|result of|equals?)\\b/g,'').trim();
  const nums=extractNumbers(t);

  if(/square\\s*root|sqrt|√/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0];
    if(n<0) return err('Cannot sqrt a negative number.');
    const r=Math.sqrt(n);
    return ok(`√${n}`,r,`√${n} = ${fmt(r)}`);
  }
  if(/cube\\s*root|cbrt/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0],r=Math.cbrt(n);
    return ok(`∛${n}`,r,`∛${n} = ${fmt(r)}`);
  }
  if(/factorial|fact\\b/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=Math.floor(nums[0]);
    if(n<0) return err('Factorial undefined for negatives.');
    if(n>20) return err('Too large (max 20).');
    let r=1; for(let i=2;i<=n;i++) r*=i;
    return ok(`${n}!`,r,`${n}! = ${fmt(r)}`);
  }
  if(/power|raised to|exponent|\\^|\\*\\*|to the/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[b,e]=nums,r=Math.pow(b,e);
    return ok(`${b}^${e}`,r,`${b}^${e} = ${fmt(r)}`);
  }
  if(/percent\\s*of|%\\s*of/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[p,total]=nums,r=(p/100)*total;
    return ok(`${p}% of ${total}`,r,`${p}/100 × ${total} = ${fmt(r)}`);
  }
  if(/what percent|percentage/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[part,whole]=nums;
    if(whole===0) return err('Cannot divide by zero.');
    const r=(part/whole)*100;
    return ok(`(${part}/${whole})×100`,r,`${part} is ${fmt(r)}% of ${whole}`);
  }
  if(/log\\s*base\\s*2|log\\s*2\\b|log₂/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0];
    if(n<=0) return err('Log undefined for ≤ 0.');
    return ok(`log₂(${n})`,Math.log2(n),`log₂(${n}) = ${fmt(Math.log2(n))}`);
  }
  if(/\\bln\\b|natural\\s*log/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0];
    if(n<=0) return err('ln undefined for ≤ 0.');
    return ok(`ln(${n})`,Math.log(n),`ln(${n}) = ${fmt(Math.log(n))}`);
  }
  if(/\\blog\\b/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0];
    if(n<=0) return err('Log undefined for ≤ 0.');
    return ok(`log₁₀(${n})`,Math.log10(n),`log₁₀(${n}) = ${fmt(Math.log10(n))}`);
  }
  if(/\\bsin\\b|sine/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0],r=Math.sin(n*Math.PI/180);
    return ok(`sin(${n}°)`,r,`sin(${n}°) = ${fmt(r)}`);
  }
  if(/\\bcos\\b|cosine/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0],r=Math.cos(n*Math.PI/180);
    return ok(`cos(${n}°)`,r,`cos(${n}°) = ${fmt(r)}`);
  }
  if(/\\btan\\b|tangent/.test(t)){
    if(!nums.length) return err('No number found.');
    const n=nums[0],r=Math.tan(n*Math.PI/180);
    return ok(`tan(${n}°)`,r,`tan(${n}°) = ${fmt(r)}`);
  }
  if(/\\bgcd\\b|greatest common/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[a,b]=nums.map(Math.floor);
    const g=(x,y)=>y===0?x:g(y,x%y);
    const r=g(Math.abs(a),Math.abs(b));
    return ok(`GCD(${a},${b})`,r,`GCD(${a},${b}) = ${r}`);
  }
  if(/\\blcm\\b|least common multiple/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[a,b]=nums.map(Math.floor);
    const g=(x,y)=>y===0?x:g(y,x%y);
    const r=Math.abs(a*b)/g(Math.abs(a),Math.abs(b));
    return ok(`LCM(${a},${b})`,r,`LCM(${a},${b}) = ${r}`);
  }
  if(/mod(ulo)?|remainder/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[a,b]=nums;
    if(b===0) return err('Cannot mod by zero.');
    return ok(`${a} mod ${b}`,a%b,`${a} mod ${b} = ${a%b}`);
  }
  if(/average|mean|\\bavg\\b/.test(t)){
    if(!nums.length) return err('No numbers found.');
    const s=nums.reduce((a,b)=>a+b,0),r=s/nums.length;
    return ok(`avg(${nums.join(', ')})`,r,`Sum(${s}) ÷ ${nums.length} = ${fmt(r)}`);
  }
  if(/absolute|\\babs\\b/.test(t)){
    if(!nums.length) return err('No number found.');
    return ok(`|${nums[0]}|`,Math.abs(nums[0]),`|${nums[0]}| = ${Math.abs(nums[0])}`);
  }
  if(/\\bpi\\b|π/.test(t)){
    return ok('π',Math.PI,`π ≈ ${Math.PI.toPrecision(9)}`);
  }
  if(/divid|÷|over\\b|\\bper\\b|\\bby\\b/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const[a,b]=nums;
    if(b===0) return err('Cannot divide by zero.');
    return ok(`${a} ÷ ${b}`,a/b,`${a} ÷ ${b} = ${fmt(a/b)}`);
  }
  if(/multi|times|product|×/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const r=nums.reduce((a,b)=>a*b,1);
    return ok(nums.join(' × '),r,`Product = ${fmt(r)}`);
  }
  if(/subtract|minus|deduct|less|difference|take away/.test(t)){
    if(nums.length<2) return err('Need two numbers.');
    const r=nums.slice(1).reduce((a,b)=>a-b,nums[0]);
    return ok(nums.join(' − '),r,`Difference = ${fmt(r)}`);
  }
  if(/add|plus|\\bsum\\b|total/.test(t)||nums.length>=2){
    if(!nums.length) return err('No numbers found.');
    const r=nums.reduce((a,b)=>a+b,0);
    return ok(nums.join(' + '),r,`Sum = ${fmt(r)}`);
  }
  if(nums.length===1) return ok(String(nums[0]),nums[0],'Single value.');
  return err("Couldn't parse. Try: 'add 5 and 3', 'sqrt 16', '20% of 500'");
}

function ok(expr,result,steps){return{ok:true,expression:expr,result,steps};}
function err(msg){return{ok:false,steps:msg};}

// ── History (localStorage) ───────────────────────────────────────────────────
let history=[];
try{ history=JSON.parse(localStorage.getItem('calc_history')||'[]'); }catch(e){}

function saveHistory(){
  try{localStorage.setItem('calc_history',JSON.stringify(history));}catch(e){}
  renderHistory();
}

function renderHistory(){
  const sec=document.getElementById('historySection');
  const list=document.getElementById('historyList');
  if(!history.length){sec.style.display='none';return;}
  sec.style.display='block';
  list.innerHTML=history.map(h=>`
    <div class="history-item">
      <span class="history-q">${h.q}</span>
      <span class="history-a">${h.r}</span>
    </div>`).join('');
}

function clearHistory(){history=[];saveHistory();}

// ── Render result ─────────────────────────────────────────────────────────────
function showResult(data, query){
  const area=document.getElementById('resultArea');
  if(!data.ok){
    area.innerHTML=`<div class="error-card">⚠️ ${data.steps}</div>`;
    return;
  }
  const rd=typeof data.result==='number'&&Number.isInteger(data.result)
    ?data.result.toLocaleString()
    :fmt(data.result);
  area.innerHTML=`<div class="result-card">
    <div class="result-label">Result</div>
    <div class="result-value">${rd}</div>
    <div class="result-expr">${data.expression} &nbsp;·&nbsp; ${data.steps}</div>
  </div>`;
  if(query&&(!history.length||history[0].q!==query)){
    history.unshift({q:query,r:rd});
    if(history.length>10) history.pop();
    saveHistory();
  }
}

// ── Calculate ─────────────────────────────────────────────────────────────────
function runCalc(){
  const q=document.getElementById('mainInput').value.trim();
  if(!q) return;
  const data=smartCalc(q);
  showResult(data,q);
  // Scroll result into view smoothly
  document.getElementById('resultArea').scrollIntoView({behavior:'smooth',block:'nearest'});
}

// ── Pills ────────────────────────────────────────────────────────────────────
const EXAMPLES=["Add 25 and 30","15% of 200","sqrt of 144","2 to the power 10",
  "factorial of 7","sin 30","GCD 12 and 18","average of 10 20 30"];
document.getElementById('pillsRow').innerHTML=
  EXAMPLES.map(e=>`<span class="pill" onclick="usePill('${e}')">${e}</span>`).join('');

function usePill(text){
  document.getElementById('mainInput').value=text;
  runCalc();
}

// ── Voice ────────────────────────────────────────────────────────────────────
let rec=null,listening=false,lastT='';

function toggleMic(){
  if(!('webkitSpeechRecognition' in window||'SpeechRecognition' in window)){
    document.getElementById('statusMsg').textContent='⚠️ Use Chrome/Edge';return;
  }
  if(listening){rec.stop();return;}
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  rec=new SR();rec.lang='en-US';rec.interimResults=true;rec.maxAlternatives=1;
  rec.onstart=()=>{
    listening=true;
    const mb=document.getElementById('micBtn');
    mb.textContent='⏹ Stop';mb.classList.add('listening');
    document.getElementById('statusMsg').textContent='🔴 Listening…';
    document.getElementById('transcript').style.display='none';
    document.getElementById('transcript').textContent='';
    document.getElementById('useBtn').style.display='none';
    lastT='';
  };
  rec.onresult=(e)=>{
    let fin='',interim='';
    for(let i=e.resultIndex;i<e.results.length;i++){
      const tx=e.results[i][0].transcript;
      e.results[i].isFinal?fin+=tx:interim+=tx;
    }
    lastT=fin||interim;
    const tr=document.getElementById('transcript');
    tr.style.display='block';tr.textContent=lastT;
    if(fin) document.getElementById('useBtn').style.display='inline-block';
  };
  rec.onerror=(e)=>{
    document.getElementById('statusMsg').textContent='❌ '+e.error;
    resetMic();
  };
  rec.onend=()=>{
    if(lastT) document.getElementById('useBtn').style.display='inline-block';
    document.getElementById('statusMsg').textContent=lastT?'✅ Click "Use this"':'No speech detected.';
    resetMic();
  };
  rec.start();
}

function resetMic(){
  listening=false;
  const mb=document.getElementById('micBtn');
  mb.textContent='🎤 Speak';mb.classList.remove('listening');
}

function useTranscript(){
  if(!lastT) return;
  document.getElementById('mainInput').value=lastT;
  document.getElementById('useBtn').style.display='none';
  document.getElementById('statusMsg').textContent='';
  document.getElementById('transcript').style.display='none';
  runCalc();
}

// ── Init ─────────────────────────────────────────────────────────────────────
renderHistory();
</script>
</body></html>
"""

components.html(CALCULATOR_HTML, height=620, scrolling=True)