import streamlit as st
import base64, numpy as np
from pathlib import Path
from datetime import datetime

from database import (
    get_courses, ajouter_course, accepter_course,
    terminer_course, get_courses_disponibles,
    get_courses_chauffeur, inscrire_chauffeur,
    get_chauffeur_by_tel, get_chauffeurs
)
from models import (
    QUARTIERS, METEOS, TRAFICS, PLAGES_HORAIRES,
    DISTANCES, TYPES_COURSE, PRIX_MIN, PRIX_MAX,
    PRIX_STEP, PRIX_DEFAULT,
    AUTHOR, MATRICULE, APP_VERSION, APP_TAGLINE, COURS, UNIVERSITE
)
from analytics import (
    build_df, stats_generales, fig_regression,
    fig_quartiers, fig_meteo, fig_prix_hist,
    fig_trafic, fig_plage, fig_boxplot, fig_statuts
)

st.set_page_config(page_title="UbanDrive", page_icon="🚖",
                   layout="wide", initial_sidebar_state="collapsed")

def get_logo():
    p = Path("logo.png")
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

logo_b64 = get_logo()
logo_src  = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

for k,v in {
    "role":None, "page_passager":"accueil", "page_chauffeur":"login",
    "step":1, "form":{}, "submitted":False, "last_id":None,
    "chauffeur":None, "show_author":False,
}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Space+Mono&display=swap');

:root{
    --v:#7C3AED; --v2:#A78BFA;
    --b:#3B82F6; --g:#10B981;
    --dark:#000000; --dark2:#0D0D0D;
    --card:#1A1A2E; --card2:#16213E;
    --border:rgba(124,58,237,0.4);
    --text:#F1F5F9; --text2:#94A3B8;
    --grad:linear-gradient(135deg,#7C3AED 0%,#3B82F6 50%,#10B981 100%);
    --shadow:0 4px 24px rgba(124,58,237,0.25);
}
*,html,body{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif!important;}
[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{
    background:var(--dark)!important;color:var(--text)!important;}
.main .block-container{padding:0!important;max-width:100%!important;}
[data-testid="stSidebar"],header[data-testid="stHeader"],footer,#MainMenu{display:none!important;}

.topbar{background:var(--dark2);border-bottom:1px solid var(--border);
    padding:10px 16px;display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:999;box-shadow:0 2px 20px rgba(124,58,237,0.2);}
.logo-img{width:40px;height:40px;object-fit:contain;
    filter:drop-shadow(0 0 10px rgba(124,58,237,0.7));
    animation:float 3s ease-in-out infinite;}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.app-title{font-size:1.4rem;font-weight:900;letter-spacing:-1px;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;}
.app-sub{font-size:0.6rem;color:var(--text2);font-style:italic;}

/* NAV HORIZONTALE COMPACTE */
.nav-wrap{
    background:var(--dark2);
    border-bottom:1px solid var(--border);
    padding:8px 12px;
    display:flex;
    gap:6px;
    overflow-x:auto;
    position:sticky;
    top:62px;
    z-index:998;
}
.nav-wrap::-webkit-scrollbar{display:none;}
.nav-btn{
    flex:1;
    min-width:60px;
    padding:7px 4px;
    border-radius:12px;
    border:2px solid;
    background:transparent;
    font-family:'Poppins',sans-serif;
    font-size:0.62rem;
    font-weight:700;
    cursor:pointer;
    white-space:nowrap;
    transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1);
    text-align:center;
}
.nav-btn:hover{transform:translateY(-2px);}

.page{padding:16px 16px 40px;max-width:700px;margin:0 auto;animation:fadeUp 0.3s ease;}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

.hero-role{min-height:88vh;display:flex;flex-direction:column;
    align-items:center;justify-content:center;text-align:center;padding:30px 20px;}
.big-title{font-size:3rem;font-weight:900;letter-spacing:-2px;line-height:1;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px;}
.tag{font-size:0.88rem;color:var(--text2);font-style:italic;margin-bottom:16px;}
.hdiv{width:60px;height:3px;background:var(--grad);border-radius:99px;margin:0 auto 20px;}
.choose{font-size:0.72rem;font-weight:700;text-transform:uppercase;
    letter-spacing:2px;color:var(--text2);margin-bottom:18px;}
.rcard{background:var(--card);border:2px solid var(--border);border-radius:20px;
    padding:28px 32px;cursor:pointer;min-width:155px;text-align:center;
    transition:all 0.35s cubic-bezier(0.34,1.56,0.64,1);box-shadow:var(--shadow);}
.rcard:hover{border-color:var(--v2);transform:translateY(-8px) scale(1.04);}
.rc-icon{font-size:2.8rem;margin-bottom:10px;display:block;}
.rc-lbl{font-size:1rem;font-weight:700;color:var(--text);}
.rc-desc{font-size:0.72rem;color:var(--text2);margin-top:5px;line-height:1.5;}

.hero-card{
    background:linear-gradient(135deg,#0D0D2B 0%,#1A0A3D 50%,#0A1F0A 100%);
    border:1px solid var(--border);border-radius:22px;
    padding:24px;margin-bottom:16px;position:relative;overflow:hidden;}

.feat-item{display:flex;align-items:center;gap:12px;
    padding:12px;background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:14px;margin-bottom:8px;transition:all 0.3s;}
.feat-item:hover{background:rgba(124,58,237,0.1);border-color:var(--border);}
.feat-icon{width:40px;height:40px;border-radius:10px;
    display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;}
.feat-title{font-size:0.88rem;font-weight:700;color:var(--text);}
.feat-desc{font-size:0.72rem;color:var(--text2);margin-top:2px;}

.card{background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:18px;margin-bottom:14px;
    position:relative;overflow:hidden;}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--grad);}
.clbl{font-size:0.62rem;font-weight:700;text-transform:uppercase;
    letter-spacing:2px;color:var(--v2);margin-bottom:12px;}
.flbl{font-size:0.7rem;font-weight:600;color:var(--text2);
    text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;display:block;}

.stepper{display:flex;align-items:center;justify-content:center;margin-bottom:20px;}
.step{display:flex;flex-direction:column;align-items:center;gap:4px;}
.sc2{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-weight:700;font-size:0.82rem;
    border:2px solid var(--border);background:var(--card2);color:var(--text2);transition:all 0.3s;}
.sc2.active{background:var(--grad);border-color:var(--v);color:#fff;
    box-shadow:0 0 20px rgba(124,58,237,0.6);animation:pulse 2s infinite;}
.sc2.done{background:var(--g);border-color:var(--g);color:#fff;}
@keyframes pulse{0%,100%{box-shadow:0 0 20px rgba(124,58,237,0.5)}50%{box-shadow:0 0 35px rgba(124,58,237,0.9)}}
.sl2{font-size:0.56rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text2);}
.sl2.active{color:var(--v2);}.sl2.done{color:var(--g);}
.sline{height:2px;width:55px;background:var(--border);margin-bottom:12px;transition:all 0.4s;}
.sline.done{background:var(--g);}

.recap{display:grid;grid-template-columns:1fr 1fr;gap:10px;
    background:var(--card2);border:1px solid var(--border);
    border-radius:12px;padding:14px;margin-bottom:14px;}
.recap label{font-size:0.56rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:var(--text2);display:block;margin-bottom:2px;}
.recap span{font-size:0.85rem;font-weight:600;color:var(--g);}

.sg{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;}
.scard{background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:16px;position:relative;overflow:hidden;transition:all 0.3s;}
.scard:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(124,58,237,0.25);}
.scard-icon{width:38px;height:38px;border-radius:10px;display:flex;
    align-items:center;justify-content:center;font-size:1.2rem;margin-bottom:10px;}
.scard-num{font-size:1.8rem;font-weight:900;color:var(--text);display:block;line-height:1;}
.scard-lbl{font-size:0.62rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:var(--text2);margin-top:4px;}
.scard-bar{position:absolute;bottom:0;left:0;right:0;height:3px;}

.ccard{background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:14px;margin-bottom:10px;transition:all 0.3s;position:relative;}
.ccard:hover{border-color:var(--v2);box-shadow:0 6px 24px rgba(124,58,237,0.2);}
.badge2{position:absolute;top:12px;right:12px;padding:3px 10px;border-radius:20px;
    font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;}
.bd{background:rgba(16,185,129,0.15);color:#10B981;border:1px solid #10B981;}
.bc{background:rgba(59,130,246,0.15);color:#60A5FA;border:1px solid #60A5FA;}
.bt{background:rgba(100,116,139,0.15);color:var(--text2);border:1px solid var(--border);}
.route{display:flex;align-items:center;gap:8px;margin-bottom:8px;}
.rpt{font-size:0.85rem;font-weight:600;color:var(--text);}
.rarr{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px;}
.chip{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
    border-radius:6px;padding:2px 8px;font-size:0.68rem;color:var(--text2);}
.chip-g{background:rgba(16,185,129,0.12);border-color:#10B981;color:#10B981;}

.list-item{background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:16px;margin-bottom:10px;transition:all 0.3s;}
.list-item:hover{border-color:var(--v2);box-shadow:0 4px 20px rgba(124,58,237,0.2);}
.course-row{padding:8px;background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08);border-radius:8px;margin-bottom:6px;}
.course-row-enc{background:rgba(59,130,246,0.08);border-color:rgba(59,130,246,0.3);}
.course-row-done{background:rgba(16,185,129,0.08);border-color:rgba(16,185,129,0.2);}

.success{text-align:center;padding:50px 20px;}
.si{font-size:3rem;margin-bottom:10px;animation:bounceIn 0.5s ease;}
@keyframes bounceIn{0%{transform:scale(0)}60%{transform:scale(1.1)}100%{transform:scale(1)}}
.st2{font-size:1.5rem;font-weight:800;color:var(--g);margin-bottom:6px;}
.ss{color:var(--text2);font-size:0.85rem;}

.abox{background:var(--card);border:2px solid var(--border);border-radius:16px;
    padding:20px;text-align:center;margin-bottom:14px;}
.aname{font-size:1rem;font-weight:800;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;}

div[data-testid="stButton"]>button{
    background:var(--grad)!important;color:#fff!important;border:none!important;
    border-radius:12px!important;font-family:'Poppins',sans-serif!important;
    font-weight:600!important;transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1)!important;
    box-shadow:0 4px 16px rgba(124,58,237,0.4)!important;}
div[data-testid="stButton"]>button:hover{
    transform:translateY(-2px) scale(1.02)!important;
    box-shadow:0 8px 28px rgba(124,58,237,0.6)!important;}
div[data-testid="stButton"]>button:active{transform:scale(0.97)!important;}
.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextInput>div>div>input{
    background:var(--card2)!important;border:1.5px solid var(--border)!important;
    border-radius:10px!important;color:var(--text)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card2)!important;border-radius:10px!important;padding:4px!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;color:var(--text2)!important;font-weight:600!important;}
.stTabs [aria-selected="true"]{background:var(--grad)!important;color:#fff!important;}
hr{border:none;height:1px;background:var(--border);margin:12px 0;}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────
def topbar():
    li = f'<img src="{logo_src}" class="logo-img"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="topbar">
        <div style="display:flex;align-items:center;gap:10px;">
            {li}
            <div>
                <div class="app-title">UbanDrive</div>
                <div class="app-sub">{APP_TAGLINE}</div>
            </div>
        </div>
        <div style="font-size:0.65rem;color:var(--text2);">{APP_VERSION}</div>
    </div>""", unsafe_allow_html=True)

def nav_passager(active):
    NAV = [
        ("🏠 Accueil",   "accueil",          "#A78BFA"),
        ("📝 Collecte",  "collecte",          "#FCA5A5"),
        ("📋 Courses",   "mes_courses",       "#FCD34D"),
        ("👥 Passagers", "liste_passagers",   "#6EE7B7"),
        ("📊 Analyse",   "analyse",           "#F9A8D4"),
    ]
    # Barre HTML visuelle
    nav_html = '<div class="nav-wrap">'
    for lbl, key, color in NAV:
        is_on = active == key
        bg = f"{color}33" if is_on else "transparent"
        shadow = f"0 0 12px {color}60" if is_on else "none"
        nav_html += f"""<button class="nav-btn" style="border-color:{color};color:{color};
            background:{bg};box-shadow:{shadow};">{lbl}</button>"""
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

    # Boutons Streamlit invisibles mais fonctionnels
    st.markdown('<div style="position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden">', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (lbl, key, _) in enumerate(NAV):
        with cols[i]:
            if st.button(lbl, key=f"pnav_{key}"):
                st.session_state.page_passager = key
                if key == "collecte":
                    st.session_state.step = 1
                    st.session_state.form = {}
                    st.session_state.submitted = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Vraie navigation via selectbox caché
    st.markdown('<div style="display:none">', unsafe_allow_html=True)
    choice = st.radio("nav", [k for _,k,_ in NAV],
                      index=[k for _,k,_ in NAV].index(active),
                      key="pnav_radio", horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation réelle avec boutons visibles sous la barre
    cols2 = st.columns(5)
    for i, (lbl, key, color) in enumerate(NAV):
        is_on = active == key
        with cols2[i]:
            st.markdown(f"""
            <style>
            div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) > div > div > div > button {{
                background: {"rgba("+str(int(color[1:3],16))+","+str(int(color[3:5],16))+","+str(int(color[5:7],16))+",0.2)"} !important;
                border: 2px solid {color} !important;
                color: {color} !important;
                border-radius: 12px !important;
                font-size: 0.6rem !important;
                font-weight: 700 !important;
                padding: 6px 2px !important;
                box-shadow: {"0 0 12px "+color+"60" if is_on else "none"} !important;
            }}
            </style>""", unsafe_allow_html=True)
            if st.button(lbl, key=f"pnav2_{key}", use_container_width=True):
                st.session_state.page_passager = key
                if key == "collecte":
                    st.session_state.step = 1
                    st.session_state.form = {}
                    st.session_state.submitted = False
                st.rerun()
    st.markdown("<hr/>", unsafe_allow_html=True)

def nav_chauffeur(active):
    NAV = [
        ("🏠 Accueil",    "c_accueil", "#A78BFA"),
        ("🚖 Courses",    "c_courses", "#FCA5A5"),
        ("📋 Trajets",    "c_mes",     "#FCD34D"),
        ("🚘 Chauffeurs", "c_liste",   "#6EE7B7"),
        ("👤 Profil",     "c_profil",  "#F9A8D4"),
    ]
    cols = st.columns(5)
    for i, (lbl, key, color) in enumerate(NAV):
        is_on = active == key
        with cols[i]:
            st.markdown(f"""
            <style>
            div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) > div > div > div > button {{
                background: {"rgba("+str(int(color[1:3],16))+","+str(int(color[3:5],16))+","+str(int(color[5:7],16))+",0.2)"} !important;
                border: 2px solid {color} !important;
                color: {color} !important;
                border-radius: 12px !important;
                font-size: 0.6rem !important;
                font-weight: 700 !important;
                padding: 6px 2px !important;
                box-shadow: {"0 0 12px "+color+"60" if is_on else "none"} !important;
            }}
            </style>""", unsafe_allow_html=True)
            if st.button(lbl, key=f"cnav_{key}", use_container_width=True):
                st.session_state.page_chauffeur = key
                st.rerun()
    st.markdown("<hr/>", unsafe_allow_html=True)

def stepper(cur):
    steps=[("1","Contexte"),("2","Trajet"),("3","Paiement")]
    h='<div class="stepper">'
    for i,(n,l) in enumerate(steps):
        k=i+1
        cc="active" if k==cur else ("done" if k<cur else "")
        ct="✓" if k<cur else n
        h+=f'<div class="step"><div class="sc2 {cc}">{ct}</div><div class="sl2 {cc}">{l}</div></div>'
        if i<2: h+=f'<div class="sline {"done" if cur>k else ""}"></div>'
    h+='</div>'
    st.markdown(h, unsafe_allow_html=True)

def back_to_home():
    if st.button("← Changer de profil", key=f"bth_{st.session_state.page_passager}{st.session_state.page_chauffeur}"):
        st.session_state.role = None
        st.session_state.chauffeur = None
        st.session_state.page_passager = "accueil"
        st.session_state.page_chauffeur = "login"
        st.rerun()

def field(label):
    st.markdown(f'<span class="flbl">{label}</span>', unsafe_allow_html=True)

# ── ACCUEIL CHOIX RÔLE ───────────────────────────────
def page_accueil():
    li = f'<img src="{logo_src}" style="width:100px;filter:drop-shadow(0 0 24px rgba(124,58,237,0.7));animation:float 3s ease-in-out infinite;margin-bottom:16px;"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="hero-role">
        {li}
        <div class="big-title">UbanDrive</div>
        <div class="tag">{APP_TAGLINE}</div>
        <div class="hdiv"></div>
        <div class="choose">Choisissez votre profil pour continuer</div>
        <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:24px;">
            <div class="rcard"><span class="rc-icon">🧑‍💼</span>
                <div class="rc-lbl">Passager</div>
                <div class="rc-desc">Demandez une course<br/>et suivez votre trajet</div></div>
            <div class="rcard"><span class="rc-icon">🚖</span>
                <div class="rc-lbl">Chauffeur</div>
                <div class="rc-desc">Acceptez des courses<br/>et gérez vos trajets</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3=st.columns([1,0.2,1])
    with c1:
        if st.button("🧑‍💼 Je suis Passager", use_container_width=True, key="rp"):
            st.session_state.role="passager"
            st.session_state.page_passager="accueil"
            st.rerun()
    with c3:
        if st.button("🚖 Je suis Chauffeur", use_container_width=True, key="rc"):
            st.session_state.role="chauffeur"
            st.session_state.page_chauffeur="login"
            st.rerun()
    if st.button("ℹ️ Créé par", key="author"):
        st.session_state.show_author=not st.session_state.show_author
        st.rerun()
    if st.session_state.show_author:
        st.markdown(f"""
        <div class="abox" style="max-width:400px;margin:0 auto;">
            <div style="font-size:1.5rem;margin-bottom:8px;">👩‍💻</div>
            <div class="aname">✦ {AUTHOR} ✦</div>
            <div style="font-size:0.72rem;color:var(--text2);font-family:'Space Mono',monospace;">Matricule · {MATRICULE}</div>
            <div style="font-size:0.68rem;color:var(--text2);margin-top:4px;">{COURS} · {UNIVERSITE}</div>
        </div>""", unsafe_allow_html=True)

# ── PASSAGER ACCUEIL ─────────────────────────────────
def p_accueil():
    courses=get_courses()
    total=len(courses)
    li=f'<img src="{logo_src}" style="width:28px;vertical-align:middle;margin-right:6px;filter:drop-shadow(0 0 6px rgba(124,58,237,0.6));"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="page">
    <div class="hero-card">
        <div style="font-size:0.75rem;color:var(--text2);margin-bottom:4px;">Bienvenue sur</div>
        <div style="font-size:1.7rem;font-weight:900;background:var(--grad);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;margin-bottom:8px;">{li}UbanDrive</div>
        <div style="font-size:0.8rem;color:var(--text2);line-height:1.6;margin-bottom:16px;">
            Plateforme de mobilité urbaine à Yaoundé.<br/>
            Collectez et analysez les données des courses en temps réel.
        </div>
        <div style="display:inline-flex;align-items:center;gap:8px;
            background:rgba(124,58,237,0.15);border:1px solid var(--border);
            border-radius:30px;padding:7px 16px;font-size:0.8rem;font-weight:600;color:var(--v2);">
            🚖 {total} course{"s" if total!=1 else ""} enregistrée{"s" if total!=1 else ""}
        </div>
    </div>""", unsafe_allow_html=True)

    feats=[
        ("rgba(124,58,237,0.2)","📝","Collecte intelligente","Enregistrez votre course en 3 étapes"),
        ("rgba(16,185,129,0.2)","📡","Suivi en temps réel","Votre chauffeur vous contacte directement"),
        ("rgba(59,130,246,0.2)","📊","Analyses & Régression","Stats descriptives + droite de régression IA"),
        ("rgba(245,158,11,0.2)","🔒","Courses sécurisées","Course acceptée verrouillée pour un seul chauffeur"),
    ]
    for bg,ic,title,desc in feats:
        st.markdown(f"""
        <div class="feat-item">
            <div class="feat-icon" style="background:{bg};">{ic}</div>
            <div><div class="feat-title">{title}</div><div class="feat-desc">{desc}</div></div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    back_to_home()

# ── ÉTAPES COLLECTE ──────────────────────────────────
def _step1():
    f=st.session_state.form
    st.markdown('<div class="card"><div class="clbl">👤 Informations Passager</div>', unsafe_allow_html=True)
    field("Nom complet *")
    nom=st.text_input("", value=f.get("nom",""), placeholder="Ex: Jean Dupont", key="nom_in", label_visibility="collapsed")
    field("Numéro de téléphone * (+237...)")
    tel=st.text_input("", value=f.get("tel",""), placeholder="+237 6XX XX XX XX", key="tel_in", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🌤️ Météo</div>', unsafe_allow_html=True)
    meteo=f.get("meteo",METEOS[0])
    cols=st.columns(2)
    for i,m in enumerate(METEOS):
        with cols[i%2]:
            if st.button(("✅ " if meteo==m else "")+m, key=f"m{i}", use_container_width=True):
                st.session_state.form["meteo"]=m; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🚦 Trafic</div>', unsafe_allow_html=True)
    trafic=f.get("trafic",TRAFICS[0])
    cols2=st.columns(2)
    for i,t in enumerate(TRAFICS):
        with cols2[i%2]:
            if st.button(("✅ " if trafic==t else "")+t, key=f"t{i}", use_container_width=True):
                st.session_state.form["trafic"]=t; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🕐 Plage Horaire</div>', unsafe_allow_html=True)
    field("Sélectionnez une plage horaire")
    plage=st.selectbox("", PLAGES_HORAIRES,
        index=PLAGES_HORAIRES.index(f.get("plage",PLAGES_HORAIRES[0])),
        key="plage_s", label_visibility="collapsed")
    st.session_state.form["plage"]=plage
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Suivant →", use_container_width=True, key="nx1"):
        if not nom.strip(): st.error("⚠️ Entrez votre nom.")
        elif not tel.strip(): st.error("⚠️ Entrez votre numéro de téléphone.")
        else:
            st.session_state.form.update({"nom":nom,"tel":tel})
            st.session_state.form.setdefault("meteo",METEOS[0])
            st.session_state.form.setdefault("trafic",TRAFICS[0])
            st.session_state.step=2; st.rerun()

def _step2():
    f=st.session_state.form
    st.markdown('<div class="card"><div class="clbl">📍 Trajet</div>', unsafe_allow_html=True)
    field("Quartier de Départ")
    dep=st.selectbox("", QUARTIERS, index=QUARTIERS.index(f.get("depart",QUARTIERS[0])),
        key="dep_s", label_visibility="collapsed")
    autres=[q for q in QUARTIERS if q!=dep]
    arr_def=f.get("arrivee",autres[0])
    if arr_def not in autres: arr_def=autres[0]
    field("Quartier d'Arrivée")
    arr=st.selectbox("", autres, index=autres.index(arr_def),
        key="arr_s", label_visibility="collapsed")
    st.session_state.form.update({"depart":dep,"arrivee":arr})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">📏 Distance Estimée</div>', unsafe_allow_html=True)
    dist=f.get("distance",DISTANCES[1])
    cols=st.columns(2)
    for i,d in enumerate(DISTANCES):
        with cols[i%2]:
            if st.button(("✅ " if dist==d else "")+d, key=f"d{i}", use_container_width=True):
                st.session_state.form["distance"]=d; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    cb,cn=st.columns(2)
    with cb:
        if st.button("← Retour", key="bk2", use_container_width=True):
            st.session_state.step=1; st.rerun()
    with cn:
        if st.button("Suivant →", key="nx2", use_container_width=True):
            st.session_state.form.setdefault("distance",DISTANCES[1])
            st.session_state.step=3; st.rerun()

def _step3():
    f=st.session_state.form
    st.markdown(f"""
    <div class="recap">
        <div><label>Passager</label><span>{f.get('nom','—')}</span></div>
        <div><label>Téléphone</label><span>{f.get('tel','—')}</span></div>
        <div><label>Météo</label><span>{f.get('meteo','—')}</span></div>
        <div><label>Trafic</label><span>{f.get('trafic','—')}</span></div>
        <div><label>Départ</label><span>{f.get('depart','—')}</span></div>
        <div><label>Arrivée</label><span>{f.get('arrivee','—')}</span></div>
        <div><label>Distance</label><span>{f.get('distance','—')}</span></div>
        <div><label>Plage</label><span>{f.get('plage','—')}</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🚗 Type de Course</div>', unsafe_allow_html=True)
    tc=f.get("type_course",TYPES_COURSE[0])
    c1,c2=st.columns(2)
    with c1:
        if st.button(("✅ " if tc==TYPES_COURSE[0] else "")+TYPES_COURSE[0], key="tc0", use_container_width=True):
            st.session_state.form["type_course"]=TYPES_COURSE[0]; st.rerun()
    with c2:
        if st.button(("✅ " if tc==TYPES_COURSE[1] else "")+TYPES_COURSE[1], key="tc1", use_container_width=True):
            st.session_state.form["type_course"]=TYPES_COURSE[1]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">💵 Prix Final (FCFA)</div>', unsafe_allow_html=True)
    field("Montant à payer au chauffeur")
    prix=st.number_input("", min_value=PRIX_MIN, max_value=PRIX_MAX,
        step=PRIX_STEP, value=f.get("prix",PRIX_DEFAULT),
        key="prix_in", label_visibility="collapsed")
    st.session_state.form["prix"]=prix
    st.markdown('</div>', unsafe_allow_html=True)

    cb,cs=st.columns(2)
    with cb:
        if st.button("← Retour", key="bk3", use_container_width=True):
            st.session_state.step=2; st.rerun()
    with cs:
        if st.button("✅ Soumettre", key="sub", use_container_width=True):
            st.session_state.form.setdefault("type_course",TYPES_COURSE[0])
            c=ajouter_course(st.session_state.form)
            st.session_state.last_id=c["id"]
            st.session_state.submitted=True; st.rerun()

def p_collecte():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    if st.session_state.submitted:
        cid=st.session_state.get("last_id","—")
        st.markdown(f"""
        <div class="success">
            <div class="si">🎉</div>
            <div class="st2">Course enregistrée !</div>
            <div class="ss">Référence : <strong>{cid}</strong><br/>Un chauffeur va accepter et vous contacter.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("➕ Nouvelle Course", use_container_width=True, key="new_c"):
            st.session_state.step=1; st.session_state.form={}
            st.session_state.submitted=False; st.rerun()
    else:
        st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:4px;">📝 Nouvelle Course</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:var(--text2);font-size:0.8rem;margin-bottom:16px;">Enregistrez votre trajet à Yaoundé</div>', unsafe_allow_html=True)
        stepper(st.session_state.step)
        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.session_state.step==1: _step1()
        elif st.session_state.step==2: _step2()
        elif st.session_state.step==3: _step3()
    st.markdown('</div>', unsafe_allow_html=True)

def p_mes_courses():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:14px;">📋 Mes Courses</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="clbl">🔍 Rechercher mes courses</div>', unsafe_allow_html=True)
    field("Votre numéro de téléphone")
    tel=st.text_input("", placeholder="+237 6XX XX XX XX", key="tel_search", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if tel.strip():
        mes=[c for c in get_courses() if c.get("tel")==tel.strip()]
        if not mes:
            st.info("Aucune course trouvée pour ce numéro.")
        for c in mes:
            s=c.get("statut","")
            bcls="bd" if s=="disponible" else ("bc" if s=="en_cours" else "bt")
            btxt="En attente" if s=="disponible" else ("En cours 🚗" if s=="en_cours" else "Terminée ✓")
            ch_info=f'<span class="chip chip-g">🚖 {c["chauffeur"]} · 📞 {c.get("tel_chauffeur","—")}</span>' if c.get("chauffeur") else ""
            st.markdown(f"""
            <div class="ccard">
                <span class="badge2 {bcls}">{btxt}</span>
                <div class="route">
                    <span class="rpt">📍 {c.get('depart','?')}</span>
                    <span class="rarr"> → </span>
                    <span class="rpt">🏁 {c.get('arrivee','?')}</span>
                </div>
                <div class="chips">
                    <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
                    <span class="chip">📏 {c.get('distance','?')}</span>
                    {ch_info}
                </div>
                <div style="font-size:0.66rem;color:var(--text2);">Réf : {c.get('id','')} · {c.get('timestamp','')}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    back_to_home()

def p_liste_passagers():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:14px;">👥 Liste des Passagers</div>', unsafe_allow_html=True)
    courses=get_courses()
    passagers={}
    for c in courses:
        tel=c.get("tel","?")
        if tel not in passagers:
            passagers[tel]={"nom":c.get("nom","?"),"tel":tel,"courses":[]}
        passagers[tel]["courses"].append(c)

    if not passagers:
        st.info("Aucun passager enregistré.")

    for tel,p in passagers.items():
        nb=len(p["courses"])
        # Header du passager
        st.markdown(f"""
        <div class="list-item">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <div style="width:42px;height:42px;border-radius:50%;
                    background:rgba(124,58,237,0.2);display:flex;align-items:center;
                    justify-content:center;font-size:1.2rem;flex-shrink:0;">👤</div>
                <div style="flex:1;">
                    <div style="font-weight:700;font-size:0.95rem;color:var(--text);">{p['nom']}</div>
                    <div style="font-size:0.75rem;color:var(--text2);">📞 {tel}</div>
                </div>
                <div style="background:rgba(124,58,237,0.15);border:1px solid var(--border);
                    border-radius:20px;padding:3px 12px;font-size:0.7rem;font-weight:700;color:var(--v2);">
                    {nb} course{"s" if nb>1 else ""}
                </div>
            </div>""", unsafe_allow_html=True)

        # Courses du passager
        for c in p["courses"]:
            s = c.get("statut","")
            if s == "en_cours":
                row_cls = "course-row course-row-enc"
                badge_txt = "En cours"
                badge_cls = "bc"
            elif s == "terminee":
                row_cls = "course-row course-row-done"
                badge_txt = "Terminée"
                badge_cls = "bt"
            else:
                row_cls = "course-row"
                badge_txt = "En attente"
                badge_cls = "bd"

            ch_line = ""
            if c.get("chauffeur"):
                ch_line = f'<div style="font-size:0.7rem;color:#10B981;margin-top:4px;">🚖 {c["chauffeur"]} · 📞 {c.get("tel_chauffeur","—")}</div>'

            st.markdown(f"""
            <div class="{row_cls}" style="margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.78rem;font-weight:600;color:var(--text);">
                        📍 {c.get('depart','?')} → 🏁 {c.get('arrivee','?')}
                    </span>
                    <span class="badge2 {badge_cls}" style="position:relative;top:0;right:0;margin-left:8px;">
                        {badge_txt}
                    </span>
                </div>
                <div style="font-size:0.72rem;color:var(--text2);margin-top:4px;">
                    💵 {c.get('prix',0):,} FCFA · 📏 {c.get('distance','?')} · {c.get('plage','?')}
                </div>
                {ch_line}
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    back_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

def p_analyse():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:4px;">📊 Analyse des Données</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:var(--text2);font-size:0.76rem;margin-bottom:14px;">{COURS}</div>', unsafe_allow_html=True)

    courses=get_courses()
    df=build_df(courses)
    if df.empty:
        st.info("Aucune donnée. Enregistrez des courses d'abord.")
        back_to_home()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    s=stats_generales(df)
    st.markdown(f"""
    <div class="sg">
        <div class="scard"><div class="scard-icon" style="background:rgba(124,58,237,0.2);">📊</div>
            <span class="scard-num">{s['total']}</span><div class="scard-lbl">Total</div>
            <div class="scard-bar" style="background:var(--grad);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(16,185,129,0.2);">💵</div>
            <span class="scard-num">{s['prix_moyen']:,}</span><div class="scard-lbl">Prix Moyen</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#10B981,#059669);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(59,130,246,0.2);">📈</div>
            <span class="scard-num">{s['prix_median']:,}</span><div class="scard-lbl">Médiane</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#3B82F6,#2563EB);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(245,158,11,0.2);">📉</div>
            <span class="scard-num">{s['prix_ecart']}</span><div class="scard-lbl">Écart-type</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#F59E0B,#D97706);"></div></div>
    </div>""", unsafe_allow_html=True)

    tabs=st.tabs(["📈 Régression","📊 Stats","🗺️ Trajets","🤖 Modèles IA"])
    with tabs[0]:
        res=fig_regression(df)
        if res:
            fig,a,b,r2=res
            st.plotly_chart(fig, use_container_width=True, key="reg_main")
            st.markdown(f"""
            <div class="card">
                <div class="clbl">📐 Résultats</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;text-align:center;">
                    <div><div style="font-size:1.2rem;font-weight:800;color:#A78BFA;">{a:.1f}</div>
                        <div style="font-size:0.62rem;color:var(--text2);">Pente (a)</div></div>
                    <div><div style="font-size:1.2rem;font-weight:800;color:#60A5FA;">{b:.1f}</div>
                        <div style="font-size:0.62rem;color:var(--text2);">Ordonnée (b)</div></div>
                    <div><div style="font-size:1.2rem;font-weight:800;color:#10B981;">{r2:.3f}</div>
                        <div style="font-size:0.62rem;color:var(--text2);">R²</div></div>
                </div>
                <div style="margin-top:10px;padding:10px;background:var(--card2);border-radius:8px;font-size:0.76rem;color:var(--text);">
                    <strong>Équation :</strong> Prix = {a:.1f} × Distance + {b:.1f}<br/>
                    <strong>Interprétation :</strong> {round(r2*100,1)}% de la variation du prix est expliquée par la distance.
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("Pas assez de données pour la régression.")
    with tabs[1]:
        c1,c2=st.columns(2)
        with c1:
            f2=fig_prix_hist(df)
            if f2: st.plotly_chart(f2, use_container_width=True, key="hist_p")
        with c2:
            f3=fig_boxplot(df)
            if f3: st.plotly_chart(f3, use_container_width=True, key="box_p")
        f4=fig_meteo(df)
        if f4: st.plotly_chart(f4, use_container_width=True, key="met_p")
        f5=fig_trafic(df)
        if f5: st.plotly_chart(f5, use_container_width=True, key="traf_p")
        f6=fig_plage(df)
        if f6: st.plotly_chart(f6, use_container_width=True, key="plage_p")
    with tabs[2]:
        f7=fig_quartiers(df)
        if f7: st.plotly_chart(f7, use_container_width=True, key="qrt_p")
    with tabs[3]:
        st.markdown("""
        <div class="card"><div class="clbl">🤖 Modèles IA disponibles</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="padding:10px;background:rgba(124,58,237,0.1);border-radius:10px;border-left:3px solid #7C3AED;">
                <strong>📈 Régression Linéaire</strong><br/>
                <span style="font-size:0.73rem;color:var(--text2);">Prédit le prix selon la distance</span></div>
            <div style="padding:10px;background:rgba(59,130,246,0.1);border-radius:10px;border-left:3px solid #3B82F6;">
                <strong>📊 Analyse Descriptive</strong><br/>
                <span style="font-size:0.73rem;color:var(--text2);">Moyenne, médiane, écart-type, Q1, Q3</span></div>
            <div style="padding:10px;background:rgba(16,185,129,0.1);border-radius:10px;border-left:3px solid #10B981;">
                <strong>🗺️ Analyse Géographique</strong><br/>
                <span style="font-size:0.73rem;color:var(--text2);">Quartiers les plus fréquentés</span></div>
        </div></div>""", unsafe_allow_html=True)
        res2=fig_regression(df)
        if res2:
            fig2,a2,b2,r22=res2
            st.plotly_chart(fig2, use_container_width=True, key="reg_ia")
            st.markdown(f"""
            <div class="card"><div class="clbl">📐 Équation Apprise</div>
            <div style="text-align:center;padding:14px;background:var(--card2);border-radius:10px;">
                <div style="font-size:1.2rem;font-weight:800;color:#A78BFA;">Prix = {a2:.1f}x + {b2:.1f}</div>
                <div style="font-size:0.76rem;color:var(--text2);margin-top:4px;">R² = {r22:.3f} · Précision : {round(r22*100,1)}%</div>
            </div></div>""", unsafe_allow_html=True)

    st.download_button("⬇️ Télécharger CSV",
        data=df.to_csv(index=False, encoding="utf-8"),
        file_name=f"ubandrive_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", key="dl_csv")
    back_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

# ── CHAUFFEUR ────────────────────────────────────────
def c_login():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    li=f'<img src="{logo_src}" style="width:60px;filter:drop-shadow(0 0 12px rgba(124,58,237,0.6));animation:float 3s ease-in-out infinite;"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 16px;">
        {li}
        <div style="font-size:1.4rem;font-weight:900;margin-top:10px;
            background:var(--grad);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;background-clip:text;">Espace Chauffeur</div>
        <div style="color:var(--text2);font-size:0.8rem;">Connectez-vous ou créez votre compte</div>
    </div>""", unsafe_allow_html=True)
    t1,t2=st.tabs(["🔐 Connexion","📝 Inscription"])
    with t1:
        st.markdown('<div class="card"><div class="clbl">🔐 Connexion</div>', unsafe_allow_html=True)
        field("Votre numéro de téléphone")
        tel=st.text_input("", placeholder="+237 6XX XX XX XX", key="tc_in", label_visibility="collapsed")
        if st.button("Se connecter", key="btn_conn", use_container_width=True):
            if tel.strip():
                ch=get_chauffeur_by_tel(tel.strip())
                if ch:
                    st.session_state.chauffeur=ch
                    st.session_state.page_chauffeur="c_accueil"
                    st.rerun()
                else: st.error("❌ Numéro non trouvé. Inscrivez-vous d'abord.")
            else: st.error("⚠️ Entrez votre numéro.")
        st.markdown('</div>', unsafe_allow_html=True)
    with t2:
        st.markdown('<div class="card"><div class="clbl">📝 Créer un compte</div>', unsafe_allow_html=True)
        field("Nom complet *")
        ni=st.text_input("", placeholder="Ex: Paul Kamga", key="ni_in", label_visibility="collapsed")
        field("Numéro de téléphone * (+237...)")
        ti=st.text_input("", placeholder="+237 6XX XX XX XX", key="ti_in", label_visibility="collapsed")
        field("Immatriculation du véhicule *")
        ii=st.text_input("", placeholder="Ex: LT-1234-A", key="ii_in", label_visibility="collapsed")
        if st.button("✅ S'inscrire", key="btn_ins", use_container_width=True):
            if not ni.strip(): st.error("⚠️ Entrez votre nom.")
            elif not ti.strip(): st.error("⚠️ Entrez votre numéro.")
            elif not ii.strip(): st.error("⚠️ Entrez l'immatriculation.")
            else:
                ch=inscrire_chauffeur(ni.strip(),ti.strip(),ii.strip())
                st.session_state.chauffeur=ch
                st.session_state.page_chauffeur="c_accueil"
                st.success("✅ Compte créé !")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    back_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

def c_accueil():
    ch=st.session_state.chauffeur
    dispos=get_courses_disponibles()
    mes=get_courses_chauffeur(ch['nom'])
    done=[c for c in mes if c['statut']=='terminee']
    encours=[c for c in mes if c['statut']=='en_cours']
    li=f'<img src="{logo_src}" style="width:26px;vertical-align:middle;margin-right:6px;"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="page">
    <div class="hero-card">
        <div style="font-size:0.75rem;color:var(--text2);margin-bottom:4px;">Connecté en tant que</div>
        <div style="font-size:1.5rem;font-weight:900;background:var(--grad);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;margin-bottom:8px;">{li}{ch['nom']}</div>
        <div style="font-size:0.8rem;color:var(--text2);margin-bottom:10px;">
            📞 {ch['tel']} &nbsp;·&nbsp; 🚗 {ch['immat']}
        </div>
        <div style="display:inline-flex;align-items:center;gap:8px;
            background:rgba(124,58,237,0.15);border:1px solid var(--border);
            border-radius:30px;padding:5px 12px;font-size:0.75rem;font-weight:600;color:var(--v2);">
            🆔 {ch['id']}
        </div>
    </div>
    <div class="sg">
        <div class="scard"><div class="scard-icon" style="background:rgba(16,185,129,0.2);">🟢</div>
            <span class="scard-num">{len(dispos)}</span><div class="scard-lbl">Disponibles</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#10B981,#059669);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(59,130,246,0.2);">🚗</div>
            <span class="scard-num">{len(encours)}</span><div class="scard-lbl">En cours</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#3B82F6,#2563EB);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(124,58,237,0.2);">🏁</div>
            <span class="scard-num">{len(done)}</span><div class="scard-lbl">Terminées</div>
            <div class="scard-bar" style="background:var(--grad);"></div></div>
        <div class="scard"><div class="scard-icon" style="background:rgba(245,158,11,0.2);">💵</div>
            <span class="scard-num">{sum(c.get('prix',0) for c in done):,}</span><div class="scard-lbl">FCFA</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#F59E0B,#D97706);"></div></div>
    </div>
    </div>""", unsafe_allow_html=True)

def c_courses():
    ch=st.session_state.chauffeur
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:8px;">🚖 Courses Disponibles</div>', unsafe_allow_html=True)
    if st.button("🔄 Rafraîchir", key="ref"): st.rerun()
    dispos=get_courses_disponibles()
    if not dispos:
        st.info("Aucune course disponible pour le moment.")
    for c in dispos:
        st.markdown(f"""
        <div class="ccard">
            <span class="badge2 bd">Disponible</span>
            <div class="route">
                <span class="rpt">📍 {c.get('depart','?')}</span>
                <span class="rarr"> → </span>
                <span class="rpt">🏁 {c.get('arrivee','?')}</span>
            </div>
            <div class="chips">
                <span class="chip">👤 {c.get('nom','?')}</span>
                <span class="chip chip-g">📞 {c.get('tel','?')}</span>
                <span class="chip">📏 {c.get('distance','?')}</span>
                <span class="chip">{c.get('meteo','?')}</span>
                <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
            </div>
            <div style="font-size:0.66rem;color:var(--text2);">Réf : {c.get('id','')} · {c.get('timestamp','')}</div>
        </div>""", unsafe_allow_html=True)
        if st.button(f"✅ Accepter — {c['id']}", key=f"acc_{c['id']}", use_container_width=True):
            if accepter_course(c["id"],ch["nom"],ch["tel"]):
                st.success(f"🎉 Acceptée ! Contactez {c.get('nom','le passager')} au {c.get('tel','—')}")
                st.rerun()
            else: st.error("❌ Course déjà prise !")
    st.markdown('</div>', unsafe_allow_html=True)

def c_mes_trajets():
    ch=st.session_state.chauffeur
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:14px;">📋 Mes Trajets</div>', unsafe_allow_html=True)
    mes=get_courses_chauffeur(ch['nom'])
    if not mes:
        st.info("Pas encore de courses.")
    for c in mes:
        s=c.get("statut","")
        bcls="bc" if s=="en_cours" else "bt"
        btxt="En cours 🚗" if s=="en_cours" else "Terminée ✓"
        st.markdown(f"""
        <div class="ccard">
            <span class="badge2 {bcls}">{btxt}</span>
            <div class="route">
                <span class="rpt">📍 {c.get('depart','?')}</span>
                <span class="rarr"> → </span>
                <span class="rpt">🏁 {c.get('arrivee','?')}</span>
            </div>
            <div class="chips">
                <span class="chip">👤 {c.get('nom','?')}</span>
                <span class="chip chip-g">📞 {c.get('tel','?')}</span>
                <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
            </div>
            <div style="font-size:0.66rem;color:var(--text2);">Réf : {c.get('id','')}</div>
        </div>""", unsafe_allow_html=True)
        if s=="en_cours":
            if st.button(f"🏁 Terminer", key=f"dn_{c['id']}", use_container_width=True):
                terminer_course(c["id"]); st.success("✅ Terminée !"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def c_liste_chauffeurs():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem;font-weight:800;margin-bottom:14px;">🚘 Liste des Chauffeurs</div>', unsafe_allow_html=True)
    chauffeurs=get_chauffeurs()
    if not chauffeurs:
        st.info("Aucun chauffeur enregistré.")
    for ch in chauffeurs:
        mes=get_courses_chauffeur(ch['nom'])
        done=[c for c in mes if c['statut']=='terminee']
        encours=[c for c in mes if c['statut']=='en_cours']

        st.markdown(f"""
        <div class="list-item">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="width:44px;height:44px;border-radius:50%;
                    background:rgba(124,58,237,0.2);display:flex;align-items:center;
                    justify-content:center;font-size:1.3rem;flex-shrink:0;">🚖</div>
                <div style="flex:1;">
                    <div style="font-weight:700;font-size:0.92rem;color:var(--text);">{ch['nom']}</div>
                    <div style="font-size:0.73rem;color:var(--text2);">📞 {ch['tel']} · 🚗 {ch['immat']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.7rem;font-weight:700;color:var(--v2);">{len(mes)} course{"s" if len(mes)>1 else ""}</div>
                    <div style="font-size:0.66rem;color:var(--text2);">{sum(c.get('prix',0) for c in done):,} FCFA</div>
                </div>
            </div>""", unsafe_allow_html=True)

        for c in encours:
            st.markdown(f"""
            <div class="course-row course-row-enc" style="margin-bottom:5px;">
                <div style="font-size:0.76rem;font-weight:600;color:var(--text);">
                    🚗 En cours · 👤 {c.get('nom','?')}
                </div>
                <div style="font-size:0.7rem;color:var(--text2);margin-top:3px;">
                    📍 {c.get('depart','?')} → 🏁 {c.get('arrivee','?')} · {c.get('prix',0):,} FCFA
                </div>
            </div>""", unsafe_allow_html=True)

        for c in done[-3:]:
            st.markdown(f"""
            <div class="course-row course-row-done" style="margin-bottom:5px;">
                <div style="font-size:0.72rem;color:#10B981;">
                    ✓ {c.get('depart','?')} → {c.get('arrivee','?')} · {c.get('prix',0):,} FCFA
                </div>
            </div>""", unsafe_allow_html=True)

        if not encours and not done:
            st.markdown('<div style="font-size:0.72rem;color:var(--text2);padding:6px;">Aucune course pour le moment.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    back_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

def c_profil():
    ch=st.session_state.chauffeur
    mes=get_courses_chauffeur(ch['nom'])
    done=[c for c in mes if c['statut']=='terminee']
    st.markdown(f"""
    <div class="page">
    <div class="card" style="text-align:center;margin-bottom:14px;">
        <div style="font-size:2.8rem;margin-bottom:8px;">👤</div>
        <div style="font-size:1.1rem;font-weight:800;background:var(--grad);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">{ch['nom']}</div>
        <div style="font-size:0.8rem;color:var(--text2);margin-top:5px;">📞 {ch['tel']}</div>
        <div style="font-size:0.8rem;color:var(--text2);">🚗 {ch['immat']}</div>
        <div style="font-size:0.7rem;color:var(--text2);margin-top:4px;">
            ID : {ch['id']} · {ch.get('date_inscription','—')[:10]}
        </div>
    </div>
    <div class="sg">
        <div class="scard"><span class="scard-num">{len(mes)}</span><div class="scard-lbl">Total</div>
            <div class="scard-bar" style="background:var(--grad);"></div></div>
        <div class="scard"><span class="scard-num">{len(done)}</span><div class="scard-lbl">Terminées</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#10B981,#059669);"></div></div>
        <div class="scard" style="grid-column:span 2;">
            <span class="scard-num">{sum(c.get('prix',0) for c in done):,}</span>
            <div class="scard-lbl">FCFA Encaissés</div>
            <div class="scard-bar" style="background:linear-gradient(90deg,#F59E0B,#D97706);"></div>
        </div>
    </div>
    </div>""", unsafe_allow_html=True)
    back_to_home()
    if st.button("🚪 Se déconnecter", use_container_width=True, key="logout"):
        st.session_state.chauffeur=None
        st.session_state.role=None
        st.rerun()

# ── ROUTING ──────────────────────────────────────────
topbar()
role = st.session_state.role

if role is None:
    page_accueil()

elif role == "passager":
    pg = st.session_state.page_passager
    nav_passager(pg)
    if pg == "accueil":           p_accueil()
    elif pg == "collecte":        p_collecte()
    elif pg == "mes_courses":     p_mes_courses()
    elif pg == "liste_passagers": p_liste_passagers()
    elif pg == "analyse":         p_analyse()

elif role == "chauffeur":
    if not st.session_state.chauffeur:
        c_login()
    else:
        pg = st.session_state.page_chauffeur
        nav_chauffeur(pg)
        if pg == "c_accueil":  c_accueil()
        elif pg == "c_courses": c_courses()
        elif pg == "c_mes":    c_mes_trajets()
        elif pg == "c_liste":  c_liste_chauffeurs()
        elif pg == "c_profil": c_profil()