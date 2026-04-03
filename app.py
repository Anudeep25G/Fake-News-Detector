import requests
import streamlit as st
import streamlit.components.v1 as components
import pickle
import re

# -----------------------------------------------------------------------
# 1. LOAD MODEL & VECTORIZER
# -----------------------------------------------------------------------
model      = pickle.load(open("model/model.pkl",      "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

if not hasattr(model, "multi_class"):
    model.multi_class = "auto"

# -----------------------------------------------------------------------
# 2. CLEAN TEXT
# -----------------------------------------------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# -----------------------------------------------------------------------
# 3. PAGE CONFIG & CSS
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Verity — Fake News Detector",
    page_icon="📰",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d1117;
    color: #ddd8cc;
}
.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, rgba(180,148,60,0.06) 0%, transparent 55%),
        radial-gradient(ellipse at 90% 85%, rgba(60,90,160,0.06) 0%, transparent 55%),
        #0d1117;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 4rem;
    max-width: 980px;
    margin: 0 auto;
}

/* ── Masthead ── */
.masthead {
    padding: 1.5rem 0 2rem;
    border-bottom: 1px solid rgba(180,148,60,0.25);
    margin-bottom: 2.4rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.masthead-left h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.6rem, 5vw, 3.8rem);
    font-weight: 700;
    color: #f0e6c8;
    letter-spacing: -0.025em;
    line-height: 1;
    margin: 0 0 0.4rem;
}
.masthead-left h1 em { color: #c9a84c; font-style: italic; }
.masthead-left p {
    font-size: 0.88rem;
    color: #6b6457;
    letter-spacing: 0.06em;
    margin: 0;
    font-weight: 300;
}
.masthead-right {
    text-align: right;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    color: #4a4438;
    text-transform: uppercase;
    line-height: 1.9;
}

/* ── Section label ── */
.section-label {
    display: block;
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.65rem;
}

/* ── Textarea ── */
textarea {
    background-color: #12161f !important;
    border: 1px solid rgba(180,148,60,0.2) !important;
    border-radius: 6px !important;
    color: #ddd8cc !important;
    font-family: 'Lora', Georgia, serif !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    line-height: 1.75 !important;
    padding: 1rem 1.1rem !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
textarea:focus {
    border-color: rgba(201,168,76,0.55) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.07) !important;
    outline: none !important;
}
textarea::placeholder {
    font-family: 'Lora', Georgia, serif !important;
    color: #52493e !important;
    font-style: italic !important;
}

/* ── Analyse Button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #c9a84c 0%, #8a6e28 100%) !important;
    color: #0d1117 !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    font-style: italic !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(201,168,76,0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #dbb94e 0%, #9a7c2e 100%) !important;
    box-shadow: 0 8px 36px rgba(201,168,76,0.38) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Warning ── */
.stAlert {
    background: rgba(210,165,40,0.08) !important;
    border: 1px solid rgba(210,165,40,0.22) !important;
    border-radius: 6px !important;
    color: #d2a528 !important;
}

/* ── Footer ── */
.page-footer {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    border-top: 1px solid rgba(180,148,60,0.12);
    margin-top: 3rem;
}
.page-footer p {
    font-size: 0.78rem;
    color: #3e3a34;
    letter-spacing: 0.08em;
    margin: 0;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# 4. MASTHEAD
# -----------------------------------------------------------------------
st.markdown("""
<div class="masthead">
    <div class="masthead-left">
        <h1>Ver<em>ity</em></h1>
        <p>News Authenticity Analysis &nbsp;·&nbsp; Powered by AI</p>
    </div>
    <div class="masthead-right">
        Est. 2025<br>Andhra Pradesh · India<br>v2.0
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------
# 5. LAYOUT — input + tips side by side
# -----------------------------------------------------------------------
col1, gap, col2 = st.columns([3, 0.15, 1.6])

with col1:
    st.markdown('<span class="section-label">Article Input</span>', unsafe_allow_html=True)
    input_text = st.text_area(
        label="article_input",
        height=210,
        placeholder="Paste a news headline or full article excerpt here…",
        label_visibility="collapsed"
    )
    analyze = st.button("✦  Analyse Article")

with col2:
    # Tips panel — minimal chip style
    components.html("""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:transparent; font-family:'DM Sans', sans-serif; }

.label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.label::before {
    content: '';
    display: block;
    width: 18px;
    height: 1px;
    background: #c9a84c;
}

.chips {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
}
.chip {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    font-size: 0.78rem;
    color: #8a8278;
    font-weight: 400;
    line-height: 1.3;
    transition: border-color 0.2s;
}
.chip svg {
    width: 13px; height: 13px;
    flex-shrink: 0;
    opacity: 0.45;
}
</style>
</head>
<body>
<div class="label">Tips</div>
<div class="chips">
    <div class="chip">
        <svg viewBox="0 0 24 24" fill="none" stroke="#c9a84c" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        2–4 sentences for best results
    </div>
    <div class="chip">
        <svg viewBox="0 0 24 24" fill="none" stroke="#c9a84c" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        Formal news prose works best
    </div>
    <div class="chip">
        <svg viewBox="0 0 24 24" fill="none" stroke="#c9a84c" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Patterns only — not factual truth
    </div>
</div>
</body>
</html>
""", height=185)

# -----------------------------------------------------------------------
# 6. PREDICTION — result rendered via components.html (bypasses sanitizer)
# -----------------------------------------------------------------------
if analyze:
    if not input_text.strip():
        st.warning("⚠  Please enter some text before analysing.")
    else:
        cleaned    = clean_text(input_text)
        vec        = vectorizer.transform([cleaned])
        pred       = model.predict(vec)[0]
        proba      = model.predict_proba(vec)[0]

        real_prob  = float(proba[1])
        fake_prob  = float(proba[0])
        confidence = max(real_prob, fake_prob)
        is_real    = (pred == 1)

        verdict    = "Likely Authentic" if is_real else "Likely Fabricated"
        card_color = "#1a3328" if is_real else "#2e1111"
        border_col = "rgba(76,175,130,0.35)" if is_real else "rgba(220,80,80,0.35)"
        text_color = "#52c48a" if is_real else "#e86060"
        bar_real   = "linear-gradient(90deg,#2e7d52,#52c48a)"
        bar_fake   = "linear-gradient(90deg,#9b2020,#e86060)"
        icon       = "✦" if is_real else "✕"
        conf_bg    = "rgba(52,196,138,0.1)"   if confidence >= 0.6 else "rgba(210,165,40,0.1)"
        conf_col   = "#52c48a"                 if confidence >= 0.6 else "#d2a528"
        conf_brd   = "rgba(52,196,138,0.25)"  if confidence >= 0.6 else "rgba(210,165,40,0.25)"
        conf_text  = f"Confidence &nbsp; {confidence*100:.0f}%" if confidence >= 0.6 else f"Low Confidence &nbsp; {confidence*100:.0f}% — verify manually"
        real_w     = f"{real_prob*100:.1f}"
        fake_w     = f"{fake_prob*100:.1f}"

        components.html(f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: transparent; font-family: 'DM Sans', sans-serif; }}

.result-card {{
    background: {card_color};
    border: 1px solid {border_col};
    border-radius: 10px;
    padding: 2rem 2.2rem 2rem;
    animation: fadeUp 0.45s cubic-bezier(0.22,1,0.36,1) forwards;
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.section-label {{
    display: block;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.5rem;
}}

.verdict {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: {text_color};
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.6rem;
    line-height: 1.1;
}}

.prob-section {{ margin-bottom: 1.2rem; }}
.prob-row {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 0.65rem;
}}
.prob-label {{
    width: 40px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6b6457;
    flex-shrink: 0;
}}
.prob-track {{
    flex: 1;
    height: 7px;
    background: rgba(255,255,255,0.07);
    border-radius: 4px;
    overflow: hidden;
}}
.prob-fill-real {{
    height: 100%;
    border-radius: 4px;
    width: {real_w}%;
    background: {bar_real};
}}
.prob-fill-fake {{
    height: 100%;
    border-radius: 4px;
    width: {fake_w}%;
    background: {bar_fake};
}}
.prob-pct {{
    width: 46px;
    text-align: right;
    font-size: 0.86rem;
    font-weight: 500;
    color: #c4baaa;
    flex-shrink: 0;
}}

.badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    background: {conf_bg};
    color: {conf_col};
    border: 1px solid {conf_brd};
    margin-bottom: 1.4rem;
}}
.badge::before {{
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
}}

.note {{
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 1rem;
    font-size: 0.78rem;
    color: #4a4438;
    font-style: italic;
    line-height: 1.6;
}}
</style>
</head>
<body>
<div class="result-card">
    <span class="section-label">Verdict</span>
    <div class="verdict">
        <span>{icon}</span>
        <span>{verdict}</span>
    </div>

    <div class="prob-section">
        <div class="prob-row">
            <span class="prob-label">Real</span>
            <div class="prob-track"><div class="prob-fill-real"></div></div>
            <span class="prob-pct">{real_w}%</span>
        </div>
        <div class="prob-row">
            <span class="prob-label">Fake</span>
            <div class="prob-track"><div class="prob-fill-fake"></div></div>
            <span class="prob-pct">{fake_w}%</span>
        </div>
    </div>

    <div class="badge">{conf_text}</div>

    <div class="note">
        Verity analyses linguistic patterns only — it does not verify factual claims.
        Always cross-reference with authoritative sources.
    </div>
</div>
</body>
</html>
""", height=320)

# -----------------------------------------------------------------------
# 7. FOOTER
# -----------------------------------------------------------------------
st.markdown("""
<div class="page-footer">
    <p>
        Verity &nbsp;·&nbsp; Fake News Detection System<br>
        Pattern-based analysis &nbsp;·&nbsp; Not a substitute for editorial judgement
    </p>
</div>
""", unsafe_allow_html=True)
