"""
SchemeSathi – Python/Flask port of the React application.
Run:  python schemesathi.py
Then open http://localhost:5000 in your browser.
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import urllib.request, urllib.error, json, os

app = Flask(__name__)
app.secret_key = "schemesathi-secret-2024"

# ─────────────────────────────────────────────
# DATA  (mirrors the JS const arrays)
# ─────────────────────────────────────────────
SCHEMES = [
    {"id":1,"name":"PM Scholarship Scheme","category":"Student","minAge":18,"maxAge":25,"maxIncome":600000,"gender":"all","states":["all"],"benefit":"₹36,000/year for professional courses","documents":["Aadhaar","10th/12th Marksheet","Income Certificate","Bank Passbook"],"link":"https://scholarships.gov.in","tag":"Education","color":"#818cf8"},
    {"id":2,"name":"Skill India (PMKVY)","category":"Student","minAge":15,"maxAge":45,"maxIncome":800000,"gender":"all","states":["all"],"benefit":"Free skill training + ₹8,000 stipend","documents":["Aadhaar","Age Proof","Bank Account"],"link":"https://www.skillindia.gov.in","tag":"Skills","color":"#34d399"},
    {"id":3,"name":"PM Internship Scheme 2024","category":"Student","minAge":21,"maxAge":24,"maxIncome":800000,"gender":"all","states":["all"],"benefit":"₹5,000/month + ₹6,000 one-time grant","documents":["Aadhaar","Degree Certificate","Bank Account"],"link":"https://pminternship.mca.gov.in","tag":"Internship","color":"#a78bfa"},
    {"id":4,"name":"Karnataka Sandhya Suraksha","category":"Elderly","minAge":60,"maxAge":99,"maxIncome":200000,"gender":"all","states":["Karnataka"],"benefit":"₹600–₹800/month pension","documents":["Aadhaar","Age Proof","BPL Card","Bank Passbook"],"link":"https://sspr.karnataka.gov.in","tag":"Pension","color":"#f472b6"},
    {"id":5,"name":"PM Jan Dhan Yojana","category":"General","minAge":10,"maxAge":99,"maxIncome":9999999,"gender":"all","states":["all"],"benefit":"Zero-balance bank account + ₹2 lakh insurance","documents":["Aadhaar","Address Proof","PAN (optional)"],"link":"https://pmjdy.gov.in","tag":"Banking","color":"#38bdf8"},
    {"id":6,"name":"Beti Bachao Beti Padhao","category":"Student","minAge":0,"maxAge":25,"maxIncome":500000,"gender":"female","states":["all"],"benefit":"Education support + savings scheme for girl child","documents":["Birth Certificate","Aadhaar","Income Certificate"],"link":"https://wcd.nic.in/bbbp-schemes","tag":"Women","color":"#fb7185"},
    {"id":7,"name":"PM Mudra Loan Yojana","category":"Entrepreneur","minAge":18,"maxAge":65,"maxIncome":9999999,"gender":"all","states":["all"],"benefit":"Loan up to ₹10 lakh for small businesses","documents":["Aadhaar","Business Plan","Bank Statement","Address Proof"],"link":"https://mudra.org.in","tag":"Loan","color":"#fb923c"},
    {"id":8,"name":"Ayushman Bharat (PMJAY)","category":"General","minAge":0,"maxAge":99,"maxIncome":300000,"gender":"all","states":["all"],"benefit":"₹5 lakh health coverage per family/year","documents":["Aadhaar","Ration Card","Income Certificate"],"link":"https://pmjay.gov.in","tag":"Health","color":"#2dd4bf"},
    {"id":9,"name":"PM Kisan Samman Nidhi","category":"Farmer","minAge":18,"maxAge":99,"maxIncome":9999999,"gender":"all","states":["all"],"benefit":"₹6,000/year directly to farmer's bank account","documents":["Aadhaar","Land Records","Bank Passbook"],"link":"https://pmkisan.gov.in","tag":"Farming","color":"#86efac"},
    {"id":10,"name":"Startup India Seed Fund","category":"Entrepreneur","minAge":18,"maxAge":45,"maxIncome":9999999,"gender":"all","states":["all"],"benefit":"Up to ₹20 lakh grant for early-stage startups","documents":["Aadhaar","DPIIT Registration","Business Plan","PAN"],"link":"https://startupindia.gov.in","tag":"Startup","color":"#c084fc"},
]

STATE_LIST = ["All India","Karnataka","Maharashtra","Tamil Nadu","Uttar Pradesh","West Bengal","Rajasthan","Gujarat","Bihar","Andhra Pradesh","Telangana","Kerala"]
OCCUPATION_OPTIONS = ["Student","Farmer","Entrepreneur","Salaried","Self-employed","Unemployed","Other"]
TAG_LIST = ["All","Education","Skills","Internship","Pension","Banking","Women","Loan","Health","Farming","Startup"]

TRANSLATIONS = {
    "English": {"home":"Home","search":"Search","schemes":"Schemes","aiChat":"AI Chat","settings":"Settings","welcome":"Welcome back","findSchemes":"Find Government Schemes Made for You","searchPlaceholder":"Search schemes, benefits, categories...","activeSchemes":"Active Schemes","statesCovered":"States Covered","beneficiaries":"Beneficiaries","savedSchemes":"Saved Schemes","browseAll":"Browse All Schemes","askAI":"Ask AI Advisor","applyNow":"Apply Now","editProfile":"Edit Profile","saveChanges":"Save Changes","preferences":"Preferences","account":"Account","signOut":"Sign Out","notifications":"Push Notifications","darkMode":"Dark Mode","language":"Language","results":"results","requiredDocs":"Required Documents","profile":"Profile","name":"Full Name","email":"Email","phone":"Phone","age":"Age","income":"Annual Income (₹)","state":"State","occupation":"Occupation","cancel":"Cancel"},
    "Hindi":   {"home":"होम","search":"खोज","schemes":"योजनाएं","aiChat":"AI चैट","settings":"सेटिंग्स","welcome":"वापस स्वागत है","findSchemes":"आपके लिए सरकारी योजनाएं खोजें","searchPlaceholder":"योजनाएं, लाभ, श्रेणियां खोजें...","activeSchemes":"सक्रिय योजनाएं","statesCovered":"राज्य शामिल","beneficiaries":"लाभार्थी","savedSchemes":"सहेजी योजनाएं","browseAll":"सभी योजनाएं देखें","askAI":"AI सलाहकार","applyNow":"अभी आवेदन करें","editProfile":"प्रोफ़ाइल संपादित करें","saveChanges":"बदलाव सहेजें","preferences":"प्राथमिकताएं","account":"खाता","signOut":"साइन आउट","notifications":"पुश नोटिफिकेशन","darkMode":"डार्क मोड","language":"भाषा","results":"परिणाम","requiredDocs":"आवश्यक दस्तावेज़","profile":"प्रोफ़ाइल","name":"पूरा नाम","email":"ईमेल","phone":"फ़ोन","age":"आयु","income":"वार्षिक आय (₹)","state":"राज्य","occupation":"व्यवसाय","cancel":"रद्द करें"},
    "Kannada": {"home":"ಮನೆ","search":"ಹುಡುಕಿ","schemes":"ಯೋಜನೆಗಳು","aiChat":"AI ಚಾಟ್","settings":"ಸೆಟ್ಟಿಂಗ್ಸ್","welcome":"ಮರಳಿ ಸ್ವಾಗತ","findSchemes":"ನಿಮಗಾಗಿ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು","searchPlaceholder":"ಯೋಜನೆಗಳು ಹುಡುಕಿ...","activeSchemes":"ಸಕ್ರಿಯ ಯೋಜನೆಗಳು","statesCovered":"ರಾಜ್ಯಗಳು","beneficiaries":"ಫಲಾನುಭವಿಗಳು","savedSchemes":"ಉಳಿಸಿದ ಯೋಜನೆಗಳು","browseAll":"ಎಲ್ಲ ಯೋಜನೆಗಳು","askAI":"AI ಸಲಹೆಗಾರ","applyNow":"ಈಗ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ","editProfile":"ಪ್ರೊಫೈಲ್ ಸಂಪಾದಿಸಿ","saveChanges":"ಬದಲಾವಣೆಗಳನ್ನು ಉಳಿಸಿ","preferences":"ಆದ್ಯತೆಗಳು","account":"ಖಾತೆ","signOut":"ಸೈನ್ ಔಟ್","notifications":"ನೋಟಿಫಿಕೇಶನ್","darkMode":"ಡಾರ್ಕ್ ಮೋಡ್","language":"ಭಾಷೆ","results":"ಫಲಿತಾಂಶಗಳು","requiredDocs":"ಅಗತ್ಯ ದಾಖಲೆಗಳು","profile":"ಪ್ರೊಫೈಲ್","name":"ಪೂರ್ಣ ಹೆಸರು","email":"ಇಮೇಲ್","phone":"ಫೋನ್","age":"ವಯಸ್ಸು","income":"ವಾರ್ಷಿಕ ಆದಾಯ (₹)","state":"ರಾಜ್ಯ","occupation":"ವೃತ್ತಿ","cancel":"ರದ್ದು ಮಾಡಿ"},
    "Tamil":   {"home":"முகப்பு","search":"தேடு","schemes":"திட்டங்கள்","aiChat":"AI அரட்டை","settings":"அமைப்புகள்","welcome":"மீண்டும் வரவேற்கிறோம்","findSchemes":"உங்களுக்கான அரசு திட்டங்கள்","searchPlaceholder":"திட்டங்கள் தேடுங்கள்...","activeSchemes":"செயலில் திட்டங்கள்","statesCovered":"மாநிலங்கள்","beneficiaries":"பயனாளிகள்","savedSchemes":"சேமித்த திட்டங்கள்","browseAll":"அனைத்து திட்டங்கள்","askAI":"AI ஆலோசகர்","applyNow":"இப்போது விண்ணப்பிக்கவும்","editProfile":"சுயவிவரம் திருத்து","saveChanges":"மாற்றங்களை சேமி","preferences":"விருப்பங்கள்","account":"கணக்கு","signOut":"வெளியேறு","notifications":"அறிவிப்புகள்","darkMode":"இருண்ட பயன்முறை","language":"மொழி","results":"முடிவுகள்","requiredDocs":"தேவையான ஆவணங்கள்","profile":"சுயவிவரம்","name":"முழு பெயர்","email":"மின்னஞ்சல்","phone":"தொலைபேசி","age":"வயது","income":"வருடாந்திர வருமானம் (₹)","state":"மாநிலம்","occupation":"தொழில்","cancel":"ரத்து செய்"},
    "Telugu":  {"home":"హోమ్","search":"శోధన","schemes":"పథకాలు","aiChat":"AI చాట్","settings":"సెట్టింగ్స్","welcome":"తిరిగి స్వాగతం","findSchemes":"మీకోసం ప్రభుత్వ పథకాలు","searchPlaceholder":"పథకాలు వెతకండి...","activeSchemes":"క్రియాశీల పథకాలు","statesCovered":"రాష్ట్రాలు","beneficiaries":"లబ్ధిదారులు","savedSchemes":"సేవ్ చేసిన పథకాలు","browseAll":"అన్ని పథకాలు","askAI":"AI సలహాదారు","applyNow":"ఇప్పుడే దరఖాస్తు","editProfile":"ప్రొఫైల్ సవరించు","saveChanges":"మార్పులు సేవ్ చేయి","preferences":"ప్రాధాన్యతలు","account":"ఖాతా","signOut":"సైన్ అవుట్","notifications":"నోటిఫికేషన్లు","darkMode":"డార్క్ మోడ్","language":"భాష","results":"ఫలితాలు","requiredDocs":"అవసరమైన పత్రాలు","profile":"ప్రొఫైల్","name":"పూర్తి పేరు","email":"ఇమెయిల్","phone":"ఫోన్","age":"వయసు","income":"వార్షిక ఆదాయం (₹)","state":"రాష్ట్రం","occupation":"వృత్తి","cancel":"రద్దు చేయి"},
    "Marathi": {"home":"मुख्यपृष्ठ","search":"शोधा","schemes":"योजना","aiChat":"AI चॅट","settings":"सेटिंग्ज","welcome":"परत स्वागत","findSchemes":"तुमच्यासाठी सरकारी योजना","searchPlaceholder":"योजना शोधा...","activeSchemes":"सक्रिय योजना","statesCovered":"राज्ये","beneficiaries":"लाभार्थी","savedSchemes":"जतन केलेल्या योजना","browseAll":"सर्व योजना","askAI":"AI सल्लागार","applyNow":"आत्ता अर्ज करा","editProfile":"प्रोफाइल संपादित करा","saveChanges":"बदल जतन करा","preferences":"प्राधान्ये","account":"खाते","signOut":"साइन आउट","notifications":"पुश नोटिफिकेशन","darkMode":"डार्क मोड","language":"भाषा","results":"निकाल","requiredDocs":"आवश्यक कागदपत्रे","profile":"प्रोफाइल","name":"पूर्ण नाव","email":"ईमेल","phone":"फोन","age":"वय","income":"वार्षिक उत्पन्न (₹)","state":"राज्य","occupation":"व्यवसाय","cancel":"रद्द करा"},
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts)[:2].upper() if parts else "U"

def filter_schemes(query="", tag="All", age=None, income=None, gender="all", occupation="Student", state="All India"):
    result = []
    for s in SCHEMES:
        q = query.lower()
        match_q = (not q or q in s["name"].lower() or q in s["benefit"].lower()
                   or q in s["tag"].lower() or q in s["category"].lower())
        match_t = (tag == "All" or s["tag"] == tag)
        match_age = (age is None or (s["minAge"] <= age <= s["maxAge"]))
        match_inc = (income is None or income <= s["maxIncome"])
        match_g = (s["gender"] == "all" or s["gender"] == gender)
        match_st = ("all" in s["states"] or state in s["states"])
        occ = occupation.lower()
        match_o = (s["category"] == "General"
                   or (occ in ("student",) and s["category"] == "Student")
                   or (occ in ("farmer",) and s["category"] == "Farmer")
                   or (occ in ("entrepreneur", "self-employed") and s["category"] == "Entrepreneur"))
        if match_q and match_t and match_age and match_inc and match_g and match_st and match_o:
            result.append(s)
    return result

# ─────────────────────────────────────────────
# HTML TEMPLATE  (single-string, mirrors the React JSX layout exactly)
# ─────────────────────────────────────────────
BASE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SchemeSathi</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#030712;color:#e2e8f0;font-family:'Inter',sans-serif;min-height:100vh}
a{text-decoration:none}
input,select,textarea{outline:none;font-family:inherit;color:#f1f5f9}
input::placeholder{color:#4b5563}
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-track{background:#0d1117}
::-webkit-scrollbar-thumb{background:#1f2937;border-radius:4px}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
@keyframes spin{to{transform:rotate(360deg)}}
.fade{animation:fadeUp .45s ease both}
.fade2{animation:fadeUp .45s .1s ease both;opacity:0;animation-fill-mode:both}
.fade3{animation:fadeUp .45s .2s ease both;opacity:0;animation-fill-mode:both}
.card{background:#0d1117;border:1px solid #1f2937;border-radius:16px;overflow:hidden;transition:box-shadow .2s}
.card:hover{box-shadow:0 0 0 1px #818cf844,0 8px 32px #00000066}
.accent-btn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;border-radius:11px;padding:12px 24px;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 6px 20px #6366f128;transition:transform .2s,box-shadow .2s}
.accent-btn:hover{transform:translateY(-2px);box-shadow:0 10px 28px #6366f140}
.ghost-btn{background:#0d1117;color:#9ca3af;border:1px solid #1f2937;padding:12px 24px;border-radius:11px;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s}
.ghost-btn:hover{background:#111827;color:#f1f5f9}
.tag{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px}
.nav-item{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:transparent;border:none;cursor:pointer;padding:6px 4px;transition:all .2s;text-decoration:none}
.nav-icon{width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center;transition:all .2s}
.nav-label{font-size:10px;font-weight:500;color:#4b5563;letter-spacing:.02em}
.nav-item.active .nav-icon{background:#6366f122}
.nav-item.active .nav-label,.nav-item.active svg{color:#818cf8 !important}
.input-field{width:100%;background:#111827;border:1px solid #1f2937;border-radius:10px;padding:12px 14px;color:#f1f5f9;font-size:14px;transition:border-color .2s;font-family:inherit}
.input-field:focus{border-color:#6366f1}
select.input-field{cursor:pointer}
.toggle-wrap{width:46px;height:26px;border-radius:13px;cursor:pointer;position:relative;transition:background .25s;flex-shrink:0}
.toggle-knob{position:absolute;top:3px;width:20px;height:20px;border-radius:50%;background:#fff;transition:left .25s;box-shadow:0 2px 6px rgba(0,0,0,.4)}
.scheme-expand{display:none}
.scheme-expand.open{display:block}
.tag-btn{background:#0d1117;border:1px solid #1f2937;color:#6b7280;padding:6px 13px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;transition:all .18s}
.tag-btn.active{background:#6366f122;border-color:#6366f155;color:#818cf8}
.stat-card{background:#0d1117;border:1px solid #1f2937;border-radius:14px;padding:22px 16px;text-align:center}
.section-label{font-size:12px;color:#4b5563;font-weight:700;letter-spacing:.08em;margin-bottom:16px}
.pref-row{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #111827}
.pref-row:last-child{border-bottom:none;padding-bottom:0}
.pref-icon{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center}
.account-row{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-bottom:1px solid #111827;cursor:pointer;transition:opacity .2s}
.account-row:hover{opacity:.65}
.account-row:last-child{border-bottom:none}
.chat-bubble-ai{max-width:78%;padding:12px 15px;border-radius:16px 16px 16px 4px;background:#0d1117;border:1px solid #1f2937;color:#e2e8f0;font-size:14px;line-height:1.6}
.chat-bubble-user{max-width:78%;padding:12px 15px;border-radius:16px 16px 4px 16px;background:#1e1b4b;border:1px solid #3730a3;color:#e2e8f0;font-size:14px;line-height:1.6}
.auth-tab{flex:1;padding:10px;border-radius:9px;border:none;font-size:14px;font-weight:700;cursor:pointer;transition:all .2s}
.chip-btn{background:#0d1117;border:1px solid #1f2937;color:#6b7280;padding:6px 11px;border-radius:20px;cursor:pointer;font-size:11px;font-weight:500;transition:all .18s;white-space:nowrap}
.chip-btn:hover{color:#9ca3af;border-color:#374151}
</style>
</head>
<body>
{% block body %}{% endblock %}
<script>
// ── Scheme card expand/collapse ──
function toggleCard(id){
  const el=document.getElementById('exp-'+id);
  const arr=document.getElementById('arr-'+id);
  if(el){el.classList.toggle('open');}
  if(arr){arr.style.transform=el.classList.contains('open')?'rotate(180deg)':'rotate(0deg)';}
}
// ── Toggle switches (preferences) ──
function uiToggle(name,el){
  const knob=el.querySelector('.toggle-knob');
  const isOn=el.dataset.on==='1';
  const next=isOn?'0':'1';
  el.dataset.on=next;
  el.style.background=next==='1'?'#6366f1':'#1f2937';
  knob.style.left=next==='1'?'22px':'3px';
  // persist via hidden form field
  const inp=document.getElementById('pref_'+name);
  if(inp) inp.value=next;
}
// ── Chat AJAX ──
async function sendChat(){
  const inp=document.getElementById('chat-input');
  const msg=inp.value.trim();
  if(!msg) return;
  inp.value='';
  appendBubble('user',msg);
  showTyping(true);
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const d=await r.json();
    showTyping(false);
    appendBubble('ai',d.reply||'Sorry, try again!');
  }catch{showTyping(false);appendBubble('ai','Connection issue. Please try again!');}
}
function appendBubble(role,text){
  const box=document.getElementById('chat-box');
  const wrap=document.createElement('div');
  wrap.style.cssText='display:flex;justify-content:'+(role==='user'?'flex-end':'flex-start')+';animation:fadeUp .3s ease both;margin-bottom:12px';
  if(role==='ai'){
    wrap.innerHTML='<div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;margin-right:9px;flex-shrink:0;margin-top:2px">🤖</div><div class="chat-bubble-ai">'+escHtml(text)+'</div>';
  }else{
    wrap.innerHTML='<div class="chat-bubble-user">'+escHtml(text)+'</div>';
  }
  box.appendChild(wrap);
  box.scrollTop=box.scrollHeight;
}
function showTyping(v){
  const t=document.getElementById('typing-ind');
  if(t) t.style.display=v?'flex':'none';
}
function escHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function fillChat(q){document.getElementById('chat-input').value=q;}
document.addEventListener('keydown',function(e){
  const inp=document.getElementById('chat-input');
  if(inp&&document.activeElement===inp&&e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChat();}
});
</script>
</body>
</html>
"""

# ─── Scheme card snippet (reused across pages) ─────────────────────────────
def render_scheme_cards(scheme_list, saved_ids, t):
    html = ""
    for i, s in enumerate(scheme_list):
        docs = "".join(
            f'<span style="background:#1f2937;color:#9ca3af;font-size:12px;padding:4px 10px;border-radius:6px;display:inline-flex;align-items:center;gap:5px;margin:3px 2px">'
            f'<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg>'
            f'{d}</span>'
            for d in s["documents"]
        )
        state_tag = "" if s["states"][0] == "all" else f'<span class="tag" style="background:#64748b1a;color:#64748b;border:1px solid #64748b33">{s["states"][0]}</span>'
        star_style = ("background:#fbbf2418;border:1px solid #fbbf24" if s["id"] in saved_ids
                      else "background:transparent;border:1px solid #374151")
        star_stroke = "#fbbf24" if s["id"] in saved_ids else "#6b7280"
        save_url = f"/save/{s['id']}?next={request.path}"
        html += f"""
<div class="card fade" style="animation-delay:{i*0.05}s">
  <div style="height:3px;background:linear-gradient(90deg,{s['color']},{s['color']}55)"></div>
  <div style="padding:18px 20px;cursor:pointer" onclick="toggleCard({s['id']})">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
      <div style="flex:1">
        <div style="display:flex;gap:7px;margin-bottom:8px;flex-wrap:wrap">
          <span class="tag" style="background:{s['color']}1a;color:{s['color']};border:1px solid {s['color']}33">{s['tag']}</span>
          {state_tag}
        </div>
        <div style="font-size:15px;font-weight:700;color:#f1f5f9;margin-bottom:5px;line-height:1.3">{s['name']}</div>
        <div style="font-size:13px;color:#6b7280;line-height:1.5">{s['benefit']}</div>
      </div>
      <div style="display:flex;gap:8px;flex-shrink:0;align-items:center;margin-top:2px">
        <a href="{save_url}" style="{star_style};border-radius:8px;padding:6px 8px;cursor:pointer;transition:all .2s;display:flex;align-items:center">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{star_stroke}" stroke-width="{'2.5' if s['id'] in saved_ids else '1.5'}" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </a>
        <div id="arr-{s['id']}" style="transition:transform .25s">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 9l-7 7-7-7"/></svg>
        </div>
      </div>
    </div>
  </div>
  <div id="exp-{s['id']}" class="scheme-expand" style="padding:0 20px 20px;border-top:1px solid #1f2937">
    <div style="padding-top:16px;margin-bottom:14px">
      <div style="font-size:11px;color:#4b5563;font-weight:700;letter-spacing:.1em;margin-bottom:8px">{t['requiredDocs'].upper()}</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px">{docs}</div>
    </div>
    <a href="{s['link']}" target="_blank" rel="noopener noreferrer"
      style="display:inline-flex;align-items:center;gap:8px;background:{s['color']};color:#fff;font-size:13px;font-weight:700;padding:9px 20px;border-radius:10px">
      {t['applyNow']}
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
    </a>
  </div>
</div>"""
    return html

# ─── Shared shell (header + nav + content) ─────────────────────────────────
def shell(content_html, step, profile, t, prefs):
    initials = get_initials(profile.get("name", ""))
    saved = session.get("saved", [1, 8])
    nav_items = [
        ("home",     t["home"],     "M3 12l9-9 9 9M5 10v9a1 1 0 001 1h4v-5h4v5h4a1 1 0 001-1v-9"),
        ("search",   t["search"],   "M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"),
        ("schemes",  t["schemes"],  "M4 6h16M7 10h10M10 14h4M12 18h0"),
        ("chat",     t["aiChat"],   "M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.9 9.9 0 01-4-.83L3 20l1.17-3.76A7.97 7.97 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"),
        ("settings", t["settings"], "M12 15a3 3 0 100-6 3 3 0 000 6zM19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"),
    ]
    nav_html = ""
    for nid, nlabel, npath in nav_items:
        active = "active" if step == nid else ""
        sw = "2.2" if step == nid else "1.7"
        stroke = "#818cf8" if step == nid else "#4b5563"
        nav_html += f"""
<a href="/{nid if nid!='home' else ''}" class="nav-item {active}">
  <div class="nav-icon">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"><path d="{npath}"/></svg>
  </div>
  <span class="nav-label">{nlabel}</span>
</a>"""
    settings_border = "2px solid #6366f1" if step == "settings" else "2px solid transparent"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SchemeSathi</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#030712;color:#e2e8f0;font-family:'Inter',sans-serif;min-height:100vh;display:flex;flex-direction:column}}
a{{text-decoration:none}} input,select,textarea{{outline:none;font-family:inherit;color:#f1f5f9}}
input::placeholder{{color:#4b5563}}
::-webkit-scrollbar{{width:5px}}::-webkit-scrollbar-track{{background:#0d1117}}::-webkit-scrollbar-thumb{{background:#1f2937;border-radius:4px}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.fade{{animation:fadeUp .45s ease both}}.fade2{{animation:fadeUp .45s .1s ease both;opacity:0;animation-fill-mode:both}}.fade3{{animation:fadeUp .45s .2s ease both;opacity:0;animation-fill-mode:both}}
.card{{background:#0d1117;border:1px solid #1f2937;border-radius:16px;overflow:hidden;transition:box-shadow .2s}}.card:hover{{box-shadow:0 0 0 1px #818cf844,0 8px 32px #00000066}}
.accent-btn{{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;border-radius:11px;padding:12px 24px;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 6px 20px #6366f128;transition:transform .2s,box-shadow .2s;display:inline-block}}
.accent-btn:hover{{transform:translateY(-2px);box-shadow:0 10px 28px #6366f140}}
.ghost-btn{{background:#0d1117;color:#9ca3af;border:1px solid #1f2937;padding:12px 24px;border-radius:11px;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s;display:inline-block}}
.ghost-btn:hover{{background:#111827;color:#f1f5f9}}
.tag{{font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px}}
.nav-item{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:transparent;border:none;cursor:pointer;padding:6px 4px;text-decoration:none}}
.nav-icon{{width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center}}
.nav-label{{font-size:10px;font-weight:500;color:#4b5563;letter-spacing:.02em}}
.nav-item.active .nav-icon{{background:#6366f122}}.nav-item.active .nav-label{{color:#818cf8}}
.input-field{{width:100%;background:#111827;border:1px solid #1f2937;border-radius:10px;padding:12px 14px;color:#f1f5f9;font-size:14px;transition:border-color .2s;font-family:inherit}}
.input-field:focus{{border-color:#6366f1}}
select.input-field{{cursor:pointer}}
.toggle-wrap{{width:46px;height:26px;border-radius:13px;cursor:pointer;position:relative;flex-shrink:0;display:inline-block}}
.toggle-knob{{position:absolute;top:3px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.4);transition:left .25s}}
.scheme-expand{{display:none}}.scheme-expand.open{{display:block}}
.tag-btn{{background:#0d1117;border:1px solid #1f2937;color:#6b7280;padding:6px 13px;border-radius:20px;font-size:12px;font-weight:600;cursor:pointer;transition:all .18s;text-decoration:none;display:inline-block}}
.tag-btn.active{{background:#6366f122;border-color:#6366f155;color:#818cf8}}
.stat-card{{background:#0d1117;border:1px solid #1f2937;border-radius:14px;padding:22px 16px;text-align:center}}
.section-label{{font-size:12px;color:#4b5563;font-weight:700;letter-spacing:.08em;margin-bottom:16px}}
.pref-row{{display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #111827}}
.pref-row:last-child{{border-bottom:none;padding-bottom:0}}
.pref-icon{{width:36px;height:36px;border-radius:9px;display:flex;align-items:center;justify-content:center}}
.account-row{{display:flex;justify-content:space-between;align-items:center;padding:13px 0;border-bottom:1px solid #111827;cursor:pointer;transition:opacity .2s;text-decoration:none;color:inherit}}
.account-row:hover{{opacity:.65}}.account-row:last-child{{border-bottom:none}}
.chat-bubble-ai{{max-width:78%;padding:12px 15px;border-radius:16px 16px 16px 4px;background:#0d1117;border:1px solid #1f2937;color:#e2e8f0;font-size:14px;line-height:1.6}}
.chat-bubble-user{{max-width:78%;padding:12px 15px;border-radius:16px 16px 4px 16px;background:#1e1b4b;border:1px solid #3730a3;color:#e2e8f0;font-size:14px;line-height:1.6}}
.chip-btn{{background:#0d1117;border:1px solid #1f2937;color:#6b7280;padding:6px 11px;border-radius:20px;cursor:pointer;font-size:11px;font-weight:500;white-space:nowrap;text-decoration:none;display:inline-block}}
.chip-btn:hover{{color:#9ca3af;border-color:#374151}}
</style>
</head>
<body>
<header style="position:sticky;top:0;z-index:100;background:rgba(3,7,18,.93);backdrop-filter:blur(16px);border-bottom:1px solid #1f2937;padding:0 20px;display:flex;align-items:center;justify-content:space-between;height:58px;flex-shrink:0">
  <a href="/" style="display:flex;align-items:center;gap:9px;text-decoration:none">
    <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 3px 12px #6366f133">🇮🇳</div>
    <span style="font-weight:800;font-size:18px;letter-spacing:-.03em;color:#f9fafb">Scheme<span style="color:#6366f1">Sathi</span></span>
  </a>
  <div style="display:flex;align-items:center;gap:8px">
    <button style="background:transparent;border:none;padding:7px;border-radius:8px;cursor:pointer;opacity:.55">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>
    </button>
    <a href="/settings" style="width:33px;height:33px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;color:#fff;box-shadow:0 2px 8px #6366f133;border:{settings_border};transition:border .2s">
      {initials or "U"}
    </a>
  </div>
</header>
<main style="flex:1;overflow-y:auto;padding-bottom:72px">{content_html}</main>
<nav style="position:fixed;bottom:0;left:0;right:0;background:rgba(3,7,18,.97);backdrop-filter:blur(16px);border-top:1px solid #1f2937;display:flex;z-index:100;height:64px">
  {nav_html}
</nav>
<script>
function toggleCard(id){{
  const el=document.getElementById('exp-'+id);
  const arr=document.getElementById('arr-'+id);
  if(el)el.classList.toggle('open');
  if(arr)arr.style.transform=el.classList.contains('open')?'rotate(180deg)':'rotate(0deg)';
}}
function uiToggle(name,el){{
  const knob=el.querySelector('.toggle-knob');
  const isOn=el.dataset.on==='1';
  const next=isOn?'0':'1';
  el.dataset.on=next;
  el.style.background=next==='1'?'#6366f1':'#1f2937';
  knob.style.left=next==='1'?'22px':'3px';
  const inp=document.getElementById('pref_'+name);
  if(inp)inp.value=next;
}}
async function sendChat(){{
  const inp=document.getElementById('chat-input');
  const msg=inp.value.trim();
  if(!msg)return;
  inp.value='';
  appendBubble('user',msg);
  showTyping(true);
  try{{
    const r=await fetch('/api/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:msg}})}});
    const d=await r.json();
    showTyping(false);
    appendBubble('ai',d.reply||'Sorry, try again!');
  }}catch{{showTyping(false);appendBubble('ai','Connection issue. Please try again!');}}
}}
function appendBubble(role,text){{
  const box=document.getElementById('chat-box');
  const wrap=document.createElement('div');
  wrap.style.cssText='display:flex;justify-content:'+(role==='user'?'flex-end':'flex-start')+';margin-bottom:12px;animation:fadeUp .3s ease both';
  if(role==='ai'){{
    wrap.innerHTML='<div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;margin-right:9px;flex-shrink:0;margin-top:2px">🤖</div><div class="chat-bubble-ai">'+escHtml(text)+'</div>';
  }}else{{
    wrap.innerHTML='<div class="chat-bubble-user">'+escHtml(text)+'</div>';
  }}
  box.appendChild(wrap);
  box.scrollTop=box.scrollHeight;
}}
function showTyping(v){{const t=document.getElementById('typing-ind');if(t)t.style.display=v?'flex':'none';}}
function escHtml(s){{return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}
function fillChat(q){{document.getElementById('chat-input').value=q;}}
document.addEventListener('keydown',function(e){{
  const inp=document.getElementById('chat-input');
  if(inp&&document.activeElement===inp&&e.key==='Enter'&&!e.shiftKey){{e.preventDefault();sendChat();}}
}});
</script>
</body>
</html>"""

# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────
AUTH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SchemeSathi – Sign In</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#030712;font-family:'Inter',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
.wrap{width:100%;max-width:420px;animation:fadeUp .5s ease both}
.logo-box{width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto 14px;box-shadow:0 8px 28px #6366f140}
.card{background:#0d1117;border:1px solid #1f2937;border-radius:20px;padding:32px 28px}
.tabs{display:flex;background:#111827;border-radius:12px;padding:4px;margin-bottom:28px;gap:4px}
.tab{flex:1;padding:10px;border-radius:9px;border:none;font-size:14px;font-weight:700;cursor:pointer;transition:all .2s}
.tab.active{background:#1e1b4b;color:#818cf8}
.tab.inactive{background:transparent;color:#6b7280}
.field{margin-bottom:16px}
label{display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px}
input,select{width:100%;background:#111827;border:1px solid #1f2937;border-radius:10px;padding:12px 14px;color:#f1f5f9;font-size:14px;font-family:inherit;transition:border-color .2s}
input:focus,select:focus{outline:none;border-color:#6366f1}
input::placeholder{color:#4b5563}
.err{margin-top:14px;background:#7f1d1d22;border:1px solid #7f1d1d;border-radius:10px;padding:10px 14px;color:#fca5a5;font-size:13px}
.submit-btn{width:100%;margin-top:22px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;color:#fff;padding:14px;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 6px 20px #6366f130;font-family:inherit}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
</style>
</head>
<body>
<div class="wrap">
  <div style="text-align:center;margin-bottom:32px">
    <div class="logo-box">🇮🇳</div>
    <div style="font-weight:800;font-size:26px;letter-spacing:-.03em;color:#f9fafb">Scheme<span style="color:#6366f1">Sathi</span></div>
    <div style="color:#6b7280;font-size:13px;margin-top:4px">India's Scheme Discovery Platform</div>
  </div>
  <div class="card">
    <div class="tabs">
      <button class="tab {{'active' if mode=='login' else 'inactive'}}" onclick="window.location='/login'">Sign In</button>
      <button class="tab {{'active' if mode=='signup' else 'inactive'}}" onclick="window.location='/signup'">Create Account</button>
    </div>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
    <form method="POST">
      {% if mode=='signup' %}
      <div class="field"><label>FULL NAME *</label><input name="name" placeholder="Arjun Sharma" value="{{ form.name }}"/></div>
      <div class="field"><label>PHONE NUMBER</label><input name="phone" placeholder="+91 98765 43210" value="{{ form.phone }}"/></div>
      <div class="grid2">
        <div class="field"><label>STATE</label><select name="state">{% for s in states %}<option {{'selected' if form.state==s else ''}}>{{ s }}</option>{% endfor %}</select></div>
        <div class="field"><label>OCCUPATION</label><select name="occupation">{% for o in occupations %}<option {{'selected' if form.occupation==o else ''}}>{{ o }}</option>{% endfor %}</select></div>
      </div>
      {% endif %}
      <div class="field"><label>EMAIL ADDRESS *</label><input name="email" type="email" placeholder="you@example.com" value="{{ form.email }}"/></div>
      <div class="field"><label>PASSWORD *</label><input name="password" type="password" placeholder="{{ 'Min. 6 characters' if mode=='signup' else 'Enter your password' }}"/></div>
      {% if mode=='signup' %}
      <div class="field"><label>CONFIRM PASSWORD *</label><input name="confirm_password" type="password" placeholder="Re-enter password"/></div>
      {% endif %}
      <button type="submit" class="submit-btn">{{ 'Sign In →' if mode=='login' else 'Create Account →' }}</button>
      {% if mode=='login' %}<div style="text-align:center;margin-top:16px;font-size:13px;color:#6b7280">Demo: use any email + password to sign in</div>{% endif %}
    </form>
  </div>
  <div style="text-align:center;margin-top:20px;font-size:12px;color:#374151">By continuing, you agree to our Terms &amp; Privacy Policy</div>
</div>
</body>
</html>"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    form = {"name": "", "email": "", "phone": "", "state": "All India", "occupation": "Student"}
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not email or not password:
            error = "Please enter email and password."
        else:
            session["logged_in"] = True
            session["profile"] = {"name": "User", "email": email, "phone": "", "state": "All India", "occupation": "Student", "age": "", "income": ""}
            session["saved"] = [1, 8]
            session["prefs"] = {"notifications": True, "darkMode": True, "language": "English"}
            session["chat"] = [{"role": "assistant", "text": "Namaste! 🙏 I'm SchemeSathi. Tell me about yourself — your age, state, occupation, or income — and I'll find the right government schemes for you."}]
            return redirect("/")
    return render_template_string(AUTH_HTML, mode="login", error=error, form=form,
                                  states=STATE_LIST, occupations=OCCUPATION_OPTIONS)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    form = {"name": "", "email": "", "phone": "", "state": "All India", "occupation": "Student"}
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        state = request.form.get("state", "All India")
        occupation = request.form.get("occupation", "Student")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        form = {"name": name, "email": email, "phone": phone, "state": state, "occupation": occupation}
        if not name or not email or not password:
            error = "Please fill all required fields."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            session["logged_in"] = True
            session["profile"] = {"name": name, "email": email, "phone": phone, "state": state, "occupation": occupation, "age": "", "income": ""}
            session["saved"] = [1, 8]
            session["prefs"] = {"notifications": True, "darkMode": True, "language": "English"}
            session["chat"] = [{"role": "assistant", "text": "Namaste! 🙏 I'm SchemeSathi. Tell me about yourself — your age, state, occupation, or income — and I'll find the right government schemes for you."}]
            return redirect("/")
    return render_template_string(AUTH_HTML, mode="signup", error=error, form=form,
                                  states=STATE_LIST, occupations=OCCUPATION_OPTIONS)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def require_login():
    if not session.get("logged_in"):
        return redirect("/login")
    return None

# ─────────────────────────────────────────────
# SAVE/UNSAVE
# ─────────────────────────────────────────────
@app.route("/save/<int:scheme_id>")
def save_scheme(scheme_id):
    redir = require_login()
    if redir: return redir
    saved = session.get("saved", [1, 8])
    if scheme_id in saved:
        saved.remove(scheme_id)
    else:
        saved.append(scheme_id)
    session["saved"] = saved
    next_url = request.args.get("next", "/")
    return redirect(next_url)

# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────
@app.route("/")
def home():
    redir = require_login()
    if redir: return redir
    profile = session.get("profile", {})
    prefs = session.get("prefs", {"language": "English"})
    t = TRANSLATIONS.get(prefs.get("language", "English"), TRANSLATIONS["English"])
    saved = session.get("saved", [1, 8])
    first_name = profile.get("name", "User").split()[0] if profile.get("name") else "User"
    saved_cards = ""
    for s in SCHEMES:
        if s["id"] in saved:
            saved_cards += f"""
<div style="background:#0d1117;border:1px solid {s['color']}22;border-radius:12px;padding:12px 15px;flex:1;min-width:160px">
  <span class="tag" style="background:{s['color']}1a;color:{s['color']};border:1px solid {s['color']}33">{s['tag']}</span>
  <div style="font-size:13px;font-weight:600;color:#f1f5f9;margin-top:8px;margin-bottom:2px">{s['name']}</div>
  <div style="font-size:12px;color:#6b7280">{s['benefit'][:40]}...</div>
</div>"""
    saved_section = ""
    if saved:
        saved_section = f"""
<div class="fade3" style="margin-top:32px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <div style="font-size:12px;color:#4b5563;font-weight:700;letter-spacing:.08em">⭐ {t['savedSchemes'].upper()}</div>
    <a href="/schemes" style="background:transparent;border:none;color:#6366f1;font-size:12px;font-weight:600;cursor:pointer;text-decoration:none">View all →</a>
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap">{saved_cards}</div>
</div>"""
    content = f"""
<div style="max-width:800px;margin:0 auto;padding:44px 20px 28px">
  <div class="fade">
    <div style="display:inline-flex;align-items:center;gap:7px;background:#6366f111;border:1px solid #6366f133;border-radius:20px;padding:5px 13px;margin-bottom:22px;font-size:12px;color:#818cf8;font-weight:600;letter-spacing:.04em">
      <span style="animation:pulse 2s infinite;color:#6366f1;font-size:10px">●</span> INDIA'S SCHEME DISCOVERY PLATFORM
    </div>
    <h1 style="font-size:clamp(28px,5vw,48px);font-weight:800;line-height:1.1;letter-spacing:-.03em;margin-bottom:14px;color:#f9fafb">
      {t['welcome']}, {first_name}! 👋<br/>
      <span style="background:linear-gradient(90deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{t['findSchemes']}</span>
    </h1>
    <p style="font-size:15px;color:#6b7280;max-width:460px;line-height:1.65;margin-bottom:32px">Discover scholarships, loans, subsidies &amp; benefits from 1500+ central &amp; state schemes.</p>
    <form action="/search" method="GET" style="position:relative;max-width:520px;margin-bottom:36px">
      <div style="position:absolute;left:15px;top:50%;transform:translateY(-50%);opacity:.5">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.8"><path d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"/></svg>
      </div>
      <input name="q" placeholder="{t['searchPlaceholder']}" style="width:100%;background:#0d1117;border:1px solid #1f2937;border-radius:13px;padding:13px 15px 13px 44px;color:#f1f5f9;font-size:14px"/>
      <button type="submit" style="position:absolute;right:7px;top:50%;transform:translateY(-50%);background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;border-radius:9px;padding:7px 14px;color:#fff;font-size:13px;font-weight:600;cursor:pointer">{t['search']}</button>
    </form>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:48px">
      <a href="/schemes" class="accent-btn">{t['browseAll']} →</a>
      <a href="/chat" class="ghost-btn">{t['askAI']}</a>
    </div>
  </div>
  <div class="fade2" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
    <div class="stat-card"><div style="font-size:26px;font-weight:800;color:#818cf8;margin-bottom:4px">1500+</div><div style="font-size:12px;color:#6b7280;font-weight:500">{t['activeSchemes']}</div></div>
    <div class="stat-card"><div style="font-size:26px;font-weight:800;color:#34d399;margin-bottom:4px">28</div><div style="font-size:12px;color:#6b7280;font-weight:500">{t['statesCovered']}</div></div>
    <div class="stat-card"><div style="font-size:26px;font-weight:800;color:#f472b6;margin-bottom:4px">10Cr+</div><div style="font-size:12px;color:#6b7280;font-weight:500">{t['beneficiaries']}</div></div>
  </div>
  {saved_section}
</div>"""
    return shell(content, "home", profile, t, prefs)

# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────
@app.route("/search")
def search():
    redir = require_login()
    if redir: return redir
    profile = session.get("profile", {})
    prefs = session.get("prefs", {"language": "English"})
    t = TRANSLATIONS.get(prefs.get("language", "English"), TRANSLATIONS["English"])
    saved = session.get("saved", [1, 8])
    q = request.args.get("q", "")
    active_tag = request.args.get("tag", "All")
    results = filter_schemes(query=q, tag=active_tag)
    tag_btns = "".join(
        f'<a href="/search?q={q}&tag={tg}" class="tag-btn {"active" if active_tag==tg else ""}">{tg}</a>'
        for tg in TAG_LIST
    )
    cards = render_scheme_cards(results, saved, t) if results else """
<div style="text-align:center;padding:56px 0;color:#4b5563">
  <div style="font-size:36px;margin-bottom:10px">🔍</div>
  <div style="font-size:15px;font-weight:600">No schemes found</div>
  <div style="font-size:13px;margin-top:4px">Try a different keyword or filter</div>
</div>"""
    content = f"""
<div style="max-width:760px;margin:0 auto;padding:32px 20px">
  <div class="fade" style="margin-bottom:24px">
    <h2 style="font-size:22px;font-weight:800;color:#f9fafb;margin-bottom:3px">{t['search']}</h2>
    <p style="color:#6b7280;font-size:13px">Search by name, benefit, or category</p>
  </div>
  <form action="/search" method="GET" style="position:relative;margin-bottom:16px">
    <div style="position:absolute;left:14px;top:50%;transform:translateY(-50%)">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="1.8"><path d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"/></svg>
    </div>
    <input autofocus name="q" value="{q}" placeholder="{t['searchPlaceholder']}"
      style="width:100%;background:#0d1117;border:1px solid #1f2937;border-radius:13px;padding:13px 15px 13px 44px;color:#f1f5f9;font-size:14px"/>
  </form>
  <div style="display:flex;gap:7px;flex-wrap:wrap;margin-bottom:20px">{tag_btns}</div>
  <div style="font-size:12px;color:#4b5563;margin-bottom:14px;font-weight:600">{len(results)} {t['results'].upper()}</div>
  <div style="display:flex;flex-direction:column;gap:10px">{cards}</div>
</div>"""
    return shell(content, "search", profile, t, prefs)

# ─────────────────────────────────────────────
# SCHEMES  (with profile-filter strip)
# ─────────────────────────────────────────────
@app.route("/schemes", methods=["GET", "POST"])
def schemes_page():
    redir = require_login()
    if redir: return redir
    profile = session.get("profile", {})
    prefs = session.get("prefs", {"language": "English"})
    t = TRANSLATIONS.get(prefs.get("language", "English"), TRANSLATIONS["English"])
    saved = session.get("saved", [1, 8])
    age_val = request.form.get("age", "") if request.method == "POST" else ""
    income_val = request.form.get("income", "") if request.method == "POST" else ""
    gender_val = request.form.get("gender", "all") if request.method == "POST" else "all"
    occupation_val = request.form.get("occupation", "Student") if request.method == "POST" else "Student"
    filtered = None
    if request.method == "POST" and (age_val or income_val):
        filtered = filter_schemes(
            age=int(age_val) if age_val else None,
            income=int(income_val) if income_val else None,
            gender=gender_val,
            occupation=occupation_val,
        )
        if not filtered:
            filtered = [s for s in SCHEMES if "all" in s["states"]][:5]
    display = filtered if filtered is not None else SCHEMES
    desc = f"{len(display)} matched from your profile" if filtered else "All available schemes"
    gender_opts = "".join(
        f'<option value="{v}" {"selected" if gender_val==v else ""}>{l}</option>'
        for v, l in [("all","Any Gender"),("male","Male"),("female","Female")]
    )
    occ_opts = "".join(
        f'<option {"selected" if occupation_val==o else ""}>{o}</option>'
        for o in OCCUPATION_OPTIONS
    )
    cards = render_scheme_cards(display, saved, t)
    content = f"""
<div style="max-width:760px;margin:0 auto;padding:32px 20px">
  <div class="fade" style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:22px">
    <div>
      <h2 style="font-size:22px;font-weight:800;color:#f9fafb;margin-bottom:3px">{t['schemes']}</h2>
      <p style="color:#6b7280;font-size:13px">{desc}</p>
    </div>
    <a href="/search" style="background:#0d1117;border:1px solid #1f2937;color:#9ca3af;padding:8px 14px;border-radius:9px;font-size:13px;font-weight:600;display:inline-flex;align-items:center;gap:6px">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.8"><path d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z"/></svg>{t['search']}
    </a>
  </div>
  <form method="POST" style="background:#0d1117;border:1px solid #1f2937;border-radius:13px;padding:14px 18px;margin-bottom:20px;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
    <span style="font-size:12px;color:#6b7280;font-weight:600">Filter:</span>
    <input name="age" placeholder="Age" value="{age_val}" style="background:#111827;border:1px solid #1f2937;border-radius:8px;padding:7px 11px;color:#f1f5f9;font-size:13px;width:70px"/>
    <input name="income" placeholder="Income" value="{income_val}" style="background:#111827;border:1px solid #1f2937;border-radius:8px;padding:7px 11px;color:#f1f5f9;font-size:13px;width:100px"/>
    <select name="gender" style="background:#111827;border:1px solid #1f2937;border-radius:8px;padding:7px 11px;color:#f1f5f9;font-size:13px">{gender_opts}</select>
    <select name="occupation" style="background:#111827;border:1px solid #1f2937;border-radius:8px;padding:7px 11px;color:#f1f5f9;font-size:13px">{occ_opts}</select>
    <button type="submit" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;color:#fff;padding:7px 16px;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer">Apply</button>
    {('<a href="/schemes" style="background:transparent;border:1px solid #1f2937;color:#6b7280;padding:7px 12px;border-radius:8px;font-size:12px;cursor:pointer;text-decoration:none">Clear</a>') if filtered else ''}
  </form>
  <div style="display:flex;flex-direction:column;gap:10px">{cards}</div>
</div>"""
    return shell(content, "schemes", profile, t, prefs)

# ─────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────
@app.route("/chat")
def chat_page():
    redir = require_login()
    if redir: return redir
    profile = session.get("profile", {})
    prefs = session.get("prefs", {"language": "English"})
    t = TRANSLATIONS.get(prefs.get("language", "English"), TRANSLATIONS["English"])
    messages = session.get("chat", [{"role": "assistant", "text": "Namaste! 🙏 I'm SchemeSathi. Tell me about yourself — your age, state, occupation, or income — and I'll find the right government schemes for you."}])
    bubbles = ""
    for m in messages:
        if m["role"] == "assistant":
            bubbles += f"""
<div style="display:flex;justify-content:flex-start;margin-bottom:12px">
  <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px;margin-right:9px;flex-shrink:0;margin-top:2px;box-shadow:0 2px 8px #6366f133">🤖</div>
  <div class="chat-bubble-ai">{m['text']}</div>
</div>"""
        else:
            bubbles += f'<div style="display:flex;justify-content:flex-end;margin-bottom:12px"><div class="chat-bubble-user">{m["text"]}</div></div>'
    prompts = ["Schemes for farmers in UP", "Scholarship for girl students", "PMJAY eligibility"]
    chips = "".join(f'<a href="#" class="chip-btn" onclick="fillChat(\'{p}\');return false">{p}</a>' for p in prompts)
    content = f"""
<div style="max-width:660px;margin:0 auto;padding:32px 20px 0;display:flex;flex-direction:column;height:calc(100vh - 130px)">
  <div class="fade" style="margin-bottom:18px">
    <h2 style="font-size:22px;font-weight:800;color:#f9fafb;margin-bottom:3px">{t['aiChat']}</h2>
    <p style="color:#6b7280;font-size:13px">Ask about any scheme in plain language or Hinglish</p>
  </div>
  <div id="chat-box" style="flex:1;overflow-y:auto;display:flex;flex-direction:column;padding-bottom:14px">
    {bubbles}
    <div id="typing-ind" style="display:none;align-items:center;gap:9px;margin-bottom:12px">
      <div style="width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:14px">🤖</div>
      <div style="background:#0d1117;border:1px solid #1f2937;padding:12px 16px;border-radius:16px 16px 16px 4px;display:flex;gap:5px;align-items:center">
        <div style="width:7px;height:7px;border-radius:50%;background:#6366f1;animation:pulse 1.2s 0s infinite"></div>
        <div style="width:7px;height:7px;border-radius:50%;background:#6366f1;animation:pulse 1.2s .15s infinite"></div>
        <div style="width:7px;height:7px;border-radius:50%;background:#6366f1;animation:pulse 1.2s .3s infinite"></div>
      </div>
    </div>
  </div>
  <div style="padding-bottom:14px">
    <div style="display:flex;gap:7px;margin-bottom:9px;flex-wrap:wrap">{chips}</div>
    <div style="display:flex;gap:8px">
      <input id="chat-input" placeholder="e.g. I'm a 21-year-old student from Karnataka..."
        style="flex:1;background:#0d1117;border:1px solid #1f2937;border-radius:12px;padding:12px 15px;color:#f1f5f9;font-size:14px"/>
      <button onclick="sendChat()" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;color:#fff;padding:12px 17px;border-radius:12px;cursor:pointer;font-size:16px">→</button>
    </div>
  </div>
</div>
<script>
  const box=document.getElementById('chat-box');
  if(box) box.scrollTop=box.scrollHeight;
</script>"""
    return shell(content, "chat", profile, t, prefs)

# ─────────────────────────────────────────────
# CHAT API  (AJAX endpoint, calls Anthropic)
# ─────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not session.get("logged_in"):
        return jsonify({"reply": "Please log in first."})
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": ""})
    history = session.get("chat", [])
    history.append({"role": "user", "text": user_msg})
    scheme_list = "\n".join(f'{s["name"]}: {s["benefit"]} ({s["tag"]})' for s in SCHEMES)
    api_messages = [
        {"role": ("assistant" if m["role"] == "assistant" else "user"), "content": m["text"]}
        for m in history
    ]
    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": f"You are SchemeSathi, a friendly Indian government scheme advisor. Schemes:\n{scheme_list}\nBe warm, concise (3-5 sentences), recommend 2-3 specific schemes. Use Hinglish if user does.",
            "messages": api_messages,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        reply = "".join(c.get("text", "") for c in result.get("content", []))
    except Exception as e:
        reply = f"Could not reach the AI right now. ({e})"
    history.append({"role": "assistant", "text": reply})
    session["chat"] = history[-30:]  # keep last 30 messages
    return jsonify({"reply": reply})

# ─────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────
@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    redir = require_login()
    if redir: return redir
    profile = session.get("profile", {})
    prefs = session.get("prefs", {"notifications": True, "darkMode": True, "language": "English"})
    saved = session.get("saved", [])
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "save_profile":
            session["profile"] = {
                "name": request.form.get("name", profile.get("name", "")),
                "email": request.form.get("email", profile.get("email", "")),
                "phone": request.form.get("phone", profile.get("phone", "")),
                "state": request.form.get("state", profile.get("state", "All India")),
                "occupation": request.form.get("occupation", profile.get("occupation", "Student")),
                "age": request.form.get("age", profile.get("age", "")),
                "income": request.form.get("income", profile.get("income", "")),
            }
            profile = session["profile"]
        elif action == "save_prefs":
            lang = request.form.get("language", "English")
            notifs = request.form.get("pref_notifications", "0") == "1"
            dark = request.form.get("pref_darkMode", "1") == "1"
            session["prefs"] = {"notifications": notifs, "darkMode": dark, "language": lang}
            prefs = session["prefs"]
        return redirect("/settings")
    t = TRANSLATIONS.get(prefs.get("language", "English"), TRANSLATIONS["English"])
    initials = get_initials(profile.get("name", ""))
    notif_on = "1" if prefs.get("notifications", True) else "0"
    dark_on = "1" if prefs.get("darkMode", True) else "0"
    notif_bg = "#6366f1" if prefs.get("notifications") else "#1f2937"
    notif_left = "22px" if prefs.get("notifications") else "3px"
    dark_bg = "#6366f1" if prefs.get("darkMode") else "#1f2937"
    dark_left = "22px" if prefs.get("darkMode") else "3px"
    state_opts = "".join(f'<option {"selected" if profile.get("state")==s else ""}>{s}</option>' for s in STATE_LIST)
    occ_opts = "".join(f'<option {"selected" if profile.get("occupation")==o else ""}>{o}</option>' for o in OCCUPATION_OPTIONS)
    lang_opts = "".join(f'<option {"selected" if prefs.get("language")==l else ""}>{l}</option>' for l in TRANSLATIONS)
    content = f"""
<div style="max-width:680px;margin:0 auto;padding:32px 20px">
  <div class="fade">

    <!-- Profile card -->
    <div style="background:#0d1117;border:1px solid #1f2937;border-radius:18px;padding:24px;margin-bottom:16px;position:relative;overflow:hidden">
      <div style="position:absolute;top:-30px;right:-30px;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,#6366f115 0%,transparent 70%);pointer-events:none"></div>
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px">
        <div style="width:64px;height:64px;border-radius:16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:22px;color:#fff;flex-shrink:0;box-shadow:0 6px 20px #6366f130">
          {initials or "U"}
        </div>
        <div style="flex:1;min-width:0">
          <div style="font-size:18px;font-weight:800;color:#f9fafb;margin-bottom:3px">{profile.get('name','User')}</div>
          <div style="font-size:13px;color:#6b7280;margin-bottom:7px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{profile.get('email','')}</div>
          <div style="display:flex;gap:7px;flex-wrap:wrap">
            <span class="tag" style="background:#818cf81a;color:#818cf8;border:1px solid #818cf833">{profile.get('occupation','User')}</span>
            <span class="tag" style="background:#34d3991a;color:#34d399;border:1px solid #34d39933">{profile.get('state','India')}</span>
          </div>
        </div>
        <a href="#edit-profile" style="background:#0d1117;border:1px solid #1f2937;border-radius:9px;padding:8px 14px;color:#9ca3af;font-size:13px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:6px;flex-shrink:0">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          Edit
        </a>
      </div>
      <div style="display:flex;gap:10px">
        <div style="flex:1;background:#111827;border-radius:10px;padding:12px;text-align:center"><div style="font-size:20px;font-weight:800;color:#fbbf24;margin-bottom:2px">{len(saved)}</div><div style="font-size:10px;color:#4b5563;font-weight:600;letter-spacing:.05em">{t['savedSchemes'].upper()}</div></div>
        <div style="flex:1;background:#111827;border-radius:10px;padding:12px;text-align:center"><div style="font-size:20px;font-weight:800;color:#34d399;margin-bottom:2px">3</div><div style="font-size:10px;color:#4b5563;font-weight:600;letter-spacing:.05em">APPLIED</div></div>
        <div style="flex:1;background:#111827;border-radius:10px;padding:12px;text-align:center"><div style="font-size:20px;font-weight:800;color:#818cf8;margin-bottom:2px">{profile.get('age') or '—'}</div><div style="font-size:10px;color:#4b5563;font-weight:600;letter-spacing:.05em">{t['age'].upper()}</div></div>
      </div>
    </div>

    <!-- Edit Profile form -->
    <div id="edit-profile" style="background:#0d1117;border:1px solid #1f2937;border-radius:18px;padding:22px 24px;margin-bottom:16px">
      <div class="section-label">{t['editProfile'].upper()}</div>
      <form method="POST">
        <input type="hidden" name="action" value="save_profile"/>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
          <div style="grid-column:1/-1"><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['name'].upper()}</label><input name="name" class="input-field" value="{profile.get('name','')}"/></div>
          <div style="grid-column:1/-1"><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['email'].upper()}</label><input name="email" type="email" class="input-field" value="{profile.get('email','')}"/></div>
          <div><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['phone'].upper()}</label><input name="phone" class="input-field" value="{profile.get('phone','')}"/></div>
          <div><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['age'].upper()}</label><input name="age" type="number" class="input-field" value="{profile.get('age','')}"/></div>
          <div style="grid-column:1/-1"><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['income'].upper()}</label><input name="income" type="number" class="input-field" value="{profile.get('income','')}"/></div>
          <div><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['state'].upper()}</label><select name="state" class="input-field">{state_opts}</select></div>
          <div><label style="display:block;font-size:11px;color:#6b7280;font-weight:700;letter-spacing:.08em;margin-bottom:7px">{t['occupation'].upper()}</label><select name="occupation" class="input-field">{occ_opts}</select></div>
        </div>
        <button type="submit" style="margin-top:18px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;color:#fff;padding:12px 26px;border-radius:11px;font-size:14px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:7px;box-shadow:0 4px 16px #6366f128">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2zM17 21v-8H7v8M7 3v5h8"/></svg>
          {t['saveChanges']}
        </button>
      </form>
    </div>

    <!-- Preferences -->
    <div style="background:#0d1117;border:1px solid #1f2937;border-radius:18px;padding:22px 24px;margin-bottom:16px">
      <div class="section-label">{t['preferences'].upper()}</div>
      <form method="POST" id="prefs-form">
        <input type="hidden" name="action" value="save_prefs"/>
        <input type="hidden" id="pref_notifications" name="pref_notifications" value="{notif_on}"/>
        <input type="hidden" id="pref_darkMode" name="pref_darkMode" value="{dark_on}"/>
        <div class="pref-row">
          <div style="display:flex;align-items:center;gap:12px">
            <div class="pref-icon" style="background:#818cf815"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.8"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg></div>
            <span style="font-size:14px;color:#d1d5db;font-weight:500">{t['notifications']}</span>
          </div>
          <div class="toggle-wrap" data-on="{notif_on}" style="background:{notif_bg}" onclick="uiToggle('notifications',this);document.getElementById('prefs-form').submit()">
            <div class="toggle-knob" style="left:{notif_left}"></div>
          </div>
        </div>
        <div class="pref-row">
          <div style="display:flex;align-items:center;gap:12px">
            <div class="pref-icon" style="background:#fbbf2415;font-size:16px">🌙</div>
            <span style="font-size:14px;color:#d1d5db;font-weight:500">{t['darkMode']}</span>
          </div>
          <div class="toggle-wrap" data-on="{dark_on}" style="background:{dark_bg}" onclick="uiToggle('darkMode',this);document.getElementById('prefs-form').submit()">
            <div class="toggle-knob" style="left:{dark_left}"></div>
          </div>
        </div>
        <div class="pref-row" style="border-bottom:none;padding-bottom:0">
          <div style="display:flex;align-items:center;gap:12px">
            <div class="pref-icon" style="background:#34d39915;font-size:16px">🌐</div>
            <div>
              <div style="font-size:14px;color:#d1d5db;font-weight:500">{t['language']}</div>
              <div style="font-size:11px;color:#4b5563;margin-top:2px">Currently: {prefs.get('language','English')}</div>
            </div>
          </div>
          <select name="language" onchange="document.getElementById('prefs-form').submit()" style="background:#111827;border:1px solid #1f2937;border-radius:9px;padding:9px 13px;color:#f1f5f9;font-size:13px;cursor:pointer;font-family:inherit">{lang_opts}</select>
        </div>
      </form>
    </div>

    <!-- Account -->
    <div style="background:#0d1117;border:1px solid #1f2937;border-radius:18px;padding:22px 24px;margin-bottom:16px">
      <div class="section-label">{t['account'].upper()}</div>
      <a href="#" class="account-row">
        <div style="display:flex;align-items:center;gap:12px">
          <div class="pref-icon" style="background:#818cf815"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
          <span style="font-size:14px;color:#d1d5db;font-weight:500">Privacy &amp; Security</span>
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.8"><path d="M9 18l6-6-6-6"/></svg>
      </a>
      <a href="/schemes" class="account-row">
        <div style="display:flex;align-items:center;gap:12px">
          <div class="pref-icon" style="background:#fbbf2415"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.8"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg></div>
          <span style="font-size:14px;color:#d1d5db;font-weight:500">{t['savedSchemes']}</span>
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.8"><path d="M9 18l6-6-6-6"/></svg>
      </a>
      <a href="#" class="account-row">
        <div style="display:flex;align-items:center;gap:12px">
          <div class="pref-icon" style="background:#34d39915"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="1.8"><path d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.9 9.9 0 01-4-.83L3 20l1.17-3.76A7.97 7.97 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg></div>
          <span style="font-size:14px;color:#d1d5db;font-weight:500">Help &amp; Support</span>
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.8"><path d="M9 18l6-6-6-6"/></svg>
      </a>
      <a href="/logout" class="account-row" style="border-bottom:none">
        <div style="display:flex;align-items:center;gap:12px">
          <div class="pref-icon" style="background:#ef444415"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.8"><path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg></div>
          <span style="font-size:14px;color:#ef4444;font-weight:600">{t['signOut']}</span>
        </div>
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4b5563" stroke-width="1.8"><path d="M9 18l6-6-6-6"/></svg>
      </a>
    </div>

    <div style="text-align:center;font-size:12px;color:#374151;padding-bottom:6px">SchemeSathi v2.0 · Made with ❤️ for Bharat</div>
  </div>
</div>"""
    return shell(content, "settings", profile, t, prefs)

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 52)
    print("  SchemeSathi – Python/Flask Edition")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 52)
    app.run(debug=True, port=5000)
