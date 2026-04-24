import streamlit as st
import base64, numpy as np
from pathlib import Path
from datetime import datetime

from database import (
    get_courses, ajouter_course, accepter_course,
    terminer_course, get_courses_disponibles,
    get_courses_chauffeur, inscrire_chauffeur,
    get_chauffeur_by_tel
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

# ── CONFIG ───────────────────────────────────────────
st.set_page_config(page_title="UbanDrive", page_icon="🚖",
                   layout="wide", initial_sidebar_state="collapsed")

def get_logo():
    p = Path("logo.png")
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

logo_b64 = get_logo()
logo_src  = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

# ── SESSION STATE ────────────────────────────────────
for k,v in {
    "role":None, "page_passager":"accueil", "page_chauffeur":"login",
    "step":1, "form":{}, "submitted":False, "last_id":None,
    "chauffeur":None, "show_author":False,
}.items():
    if k not in st.session_state: st.session_state[k] = v

# ── CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Space+Mono&display=swap');

:root{
    --v:#6C3FD4; --v2:#8B5CF6;
    --b:#2563EB; --g:#22C55E;
    --dark:#0D0D1A; --dark2:#13132A; --dark3:#1A1A35;
    --card:#16162E; --card2:#1E1E3A;
    --border:rgba(108,63,212,0.3);
    --text:#E8E8F0; --text2:#8888A8;
    --grad:linear-gradient(135deg,#6C3FD4 0%,#2563EB 50%,#22C55E 100%);
    --shadow:0 4px 24px rgba(108,63,212,0.2);
}
*,html,body{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif!important;}
[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{
    background:var(--dark)!important; color:var(--text)!important;}
.main .block-container{padding:0!important;max-width:100%!important;}
[data-testid="stSidebar"],header[data-testid="stHeader"],footer,#MainMenu{display:none!important;}

/* TOPBAR */
.topbar{background:var(--dark2);border-bottom:1px solid var(--border);
    padding:12px 20px;display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:999;box-shadow:0 2px 20px rgba(108,63,212,0.15);}
.logo-img{width:44px;height:44px;object-fit:contain;
    filter:drop-shadow(0 0 10px rgba(108,63,212,0.6));
    animation:float 3s ease-in-out infinite;}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
.app-title{font-size:1.5rem;font-weight:900;letter-spacing:-1px;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;}
.app-sub{font-size:0.62rem;color:var(--text2);font-style:italic;}

/* BOTTOM NAV */
.bnav{position:fixed;bottom:0;left:0;right:0;z-index:998;
    background:var(--dark2);border-top:1px solid var(--border);
    display:flex;padding:6px 0 10px;
    box-shadow:0 -4px 20px rgba(108,63,212,0.15);}
.bni{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;
    font-size:0.6rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.5px;color:var(--text2);cursor:pointer;}
.bni.on{color:var(--v2);}
.bni-icon{font-size:1.3rem;transition:transform 0.3s cubic-bezier(0.34,1.56,0.64,1);}
.bni.on .bni-icon{transform:translateY(-3px);}

/* PAGE */
.page{padding:20px 20px 90px;max-width:700px;margin:0 auto;animation:fadeUp 0.35s ease;}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

/* HERO CARD (style FinStat) */
.hero-card{
    background:linear-gradient(135deg,#1A1A40 0%,#2D1B6B 50%,#1A2A1A 100%);
    border:1px solid var(--border);border-radius:22px;
    padding:28px;margin-bottom:20px;position:relative;overflow:hidden;
}
.hero-card::before{content:'';position:absolute;top:-40px;right:-40px;
    width:150px;height:150px;border-radius:50%;
    background:radial-gradient(circle,rgba(108,63,212,0.3) 0%,transparent 70%);}
.hero-label{font-size:0.75rem;color:var(--text2);margin-bottom:4px;}
.hero-name{font-size:2rem;font-weight:900;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px;}
.hero-desc{font-size:0.82rem;color:var(--text2);line-height:1.6;margin-bottom:18px;}
.hero-badge{display:inline-flex;align-items:center;gap:8px;
    background:rgba(108,63,212,0.15);border:1px solid var(--border);
    border-radius:30px;padding:8px 18px;font-size:0.82rem;
    font-weight:600;color:var(--v2);}

/* STAT GRID (2x2 comme FinStat) */
.sg{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;}
.sc{background:var(--card);border:1px solid var(--border);border-radius:16px;
    padding:20px;position:relative;overflow:hidden;transition:all 0.3s;}
.sc:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(108,63,212,0.2);}
.sc-icon{width:42px;height:42px;border-radius:12px;display:flex;
    align-items:center;justify-content:center;font-size:1.3rem;margin-bottom:14px;}
.sc-num{font-size:2rem;font-weight:900;color:var(--text);display:block;line-height:1;}
.sc-lbl{font-size:0.65rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:var(--text2);margin-top:4px;}
.sc-bar{position:absolute;bottom:0;left:0;right:0;height:3px;}

/* ROLE CARDS */
.role-hero{min-height:85vh;display:flex;flex-direction:column;
    align-items:center;justify-content:center;text-align:center;padding:30px 20px 90px;}
.hero-big-name{font-size:3.2rem;font-weight:900;letter-spacing:-2px;line-height:1;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:6px;}
.hero-tag{font-size:0.88rem;color:var(--text2);font-style:italic;margin-bottom:16px;}
.hdivider{width:60px;height:3px;background:var(--grad);border-radius:99px;margin:0 auto 20px;}
.hchoose{font-size:0.72rem;font-weight:700;text-transform:uppercase;
    letter-spacing:2px;color:var(--text2);margin-bottom:18px;}
.rcards{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;}
.rcard{background:var(--card);border:1.5px solid var(--border);border-radius:18px;
    padding:26px 28px;cursor:pointer;min-width:150px;text-align:center;
    transition:all 0.35s cubic-bezier(0.34,1.56,0.64,1);box-shadow:var(--shadow);}
.rcard:hover{border-color:var(--v2);transform:translateY(-8px) scale(1.04);
    box-shadow:0 16px 40px rgba(108,63,212,0.3);}
.rc-icon{font-size:2.5rem;margin-bottom:10px;display:block;}
.rc-lbl{font-size:0.95rem;font-weight:700;color:var(--text);}
.rc-desc{font-size:0.72rem;color:var(--text2);margin-top:4px;line-height:1.5;}

/* CARD */
.card{background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;margin-bottom:14px;
    position:relative;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.3);}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--grad);}
.clbl{font-size:0.63rem;font-weight:700;text-transform:uppercase;
    letter-spacing:2px;color:var(--v2);margin-bottom:12px;}

/* FIELD LABEL */
.flbl{font-size:0.72rem;font-weight:600;color:var(--text2);
    text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;}

/* STEPPER */
.stepper{display:flex;align-items:center;justify-content:center;margin-bottom:24px;}
.step{display:flex;flex-direction:column;align-items:center;gap:4px;}
.sc2{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-weight:700;font-size:0.82rem;
    border:2px solid var(--border);background:var(--card2);color:var(--text2);transition:all 0.3s;}
.sc2.active{background:var(--grad);border-color:var(--v);color:#fff;
    box-shadow:0 0 20px rgba(108,63,212,0.5);animation:pulse 2s infinite;}
.sc2.done{background:var(--g);border-color:var(--g);color:#fff;}
@keyframes pulse{0%,100%{box-shadow:0 0 18px rgba(108,63,212,0.5)}50%{box-shadow:0 0 30px rgba(108,63,212,0.8)}}
.sl2{font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text2);}
.sl2.active{color:var(--v2);}.sl2.done{color:var(--g);}
.sline{height:2px;width:60px;background:var(--border);margin-bottom:14px;transition:all 0.4s;}
.sline.done{background:var(--g);}

/* RECAP */
.recap{display:grid;grid-template-columns:1fr 1fr;gap:10px;
    background:var(--card2);border:1px solid var(--border);
    border-radius:12px;padding:14px;margin-bottom:14px;}
.recap label{font-size:0.58rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:var(--text2);display:block;margin-bottom:2px;}
.recap span{font-size:0.85rem;font-weight:600;color:var(--g);}

/* COURSE CARD */
.ccard{background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:16px;margin-bottom:12px;transition:all 0.3s;
    position:relative;box-shadow:0 2px 12px rgba(0,0,0,0.3);}
.ccard:hover{border-color:var(--v2);box-shadow:0 8px 28px rgba(108,63,212,0.2);}
.badge2{position:absolute;top:12px;right:12px;padding:3px 10px;border-radius:20px;
    font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;}
.bd{background:rgba(34,197,94,0.1);color:#22C55E;border:1px solid #22C55E;}
.bc{background:rgba(37,99,235,0.1);color:#60A5FA;border:1px solid #60A5FA;}
.bt{background:rgba(100,100,130,0.15);color:var(--text2);border:1px solid var(--border);}
.route{display:flex;align-items:center;gap:8px;margin-bottom:8px;}
.rpt{font-size:0.85rem;font-weight:600;color:var(--text);}
.rarr{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px;}
.chip{background:var(--card2);border:1px solid var(--border);border-radius:6px;
    padding:2px 8px;font-size:0.68rem;color:var(--text2);}
.chip-g{background:rgba(34,197,94,0.08);border-color:#22C55E;color:#22C55E;}

/* SUCCESS */
.success{text-align:center;padding:50px 20px;}
.si{font-size:3rem;margin-bottom:10px;animation:bounceIn 0.5s ease;}
@keyframes bounceIn{0%{transform:scale(0)}60%{transform:scale(1.1)}100%{transform:scale(1)}}
.st2{font-size:1.5rem;font-weight:800;color:var(--g);margin-bottom:6px;}
.ss{color:var(--text2);font-size:0.85rem;}

/* AUTHOR */
.abox{background:var(--card);border:2px solid var(--border);border-radius:16px;
    padding:20px;text-align:center;box-shadow:0 8px 32px rgba(108,63,212,0.2);margin-bottom:14px;}
.aname{font-size:1rem;font-weight:800;
    background:var(--grad);-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;background-clip:text;}
.amat{font-size:0.72rem;color:var(--text2);font-family:'Space Mono',monospace;}

/* BACK BTN */
.back-row{display:flex;align-items:center;gap:8px;margin-bottom:16px;cursor:pointer;}

/* OVERRIDES */
div[data-testid="stButton"]>button{
    background:var(--grad)!important;color:#fff!important;border:none!important;
    border-radius:12px!important;font-family:'Poppins',sans-serif!important;
    font-weight:600!important;transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1)!important;
    box-shadow:0 4px 16px rgba(108,63,212,0.35)!important;}
div[data-testid="stButton"]>button:hover{
    transform:translateY(-3px) scale(1.02)!important;
    box-shadow:0 8px 28px rgba(108,63,212,0.55)!important;}
div[data-testid="stButton"]>button:active{transform:scale(0.96)!important;}
.stSelectbox>div>div,.stNumberInput>div>div>input,.stTextInput>div>div>input{
    background:var(--card2)!important;border:1.5px solid var(--border)!important;
    border-radius:10px!important;color:var(--text)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--card2)!important;border-radius:10px!important;padding:4px!important;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;color:var(--text2)!important;font-weight:600!important;}
.stTabs [aria-selected="true"]{background:var(--grad)!important;color:#fff!important;}
hr{border:none;height:1px;background:var(--border);margin:14px 0;}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────────
def topbar():
    li = f'<img src="{logo_src}" class="logo-img"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="topbar">
        <div style="display:flex;align-items:center;gap:12px;">
            {li}
            <div>
                <div class="app-title">UbanDrive</div>
                <div class="app-sub">{APP_TAGLINE}</div>
            </div>
        </div>
        <div style="font-size:0.7rem;color:var(--text2);">{APP_VERSION}</div>
    </div>""", unsafe_allow_html=True)

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

def bottom_nav_p(active):
    items=[("🏠","accueil","Accueil"),("📝","collecte","Collecte"),
           ("📋","mes_courses","Courses"),("📊","analyse","Analyse")]
    h='<div class="bnav">'
    for ic,k,lb in items:
        cls="bni on" if active==k else "bni"
        h+=f'<div class="{cls}"><span class="bni-icon">{ic}</span><span>{lb}</span></div>'
    h+='</div>'
    st.markdown(h, unsafe_allow_html=True)
    cols=st.columns(4)
    nav=[("accueil","🏠"),("collecte","📝"),("mes_courses","📋"),("analyse","📊")]
    for i,(k,ic) in enumerate(nav):
        with cols[i]:
            if st.button(ic, key=f"pn_{k}"):
                st.session_state.page_passager=k
                if k=="collecte":
                    st.session_state.step=1
                    st.session_state.form={}
                    st.session_state.submitted=False
                st.rerun()

def bottom_nav_c(active):
    items=[("🏠","c_accueil","Accueil"),("🚖","c_courses","Courses"),
           ("📋","c_mes","Trajets"),("👤","c_profil","Profil")]
    h='<div class="bnav">'
    for ic,k,lb in items:
        cls="bni on" if active==k else "bni"
        h+=f'<div class="{cls}"><span class="bni-icon">{ic}</span><span>{lb}</span></div>'
    h+='</div>'
    st.markdown(h, unsafe_allow_html=True)
    cols=st.columns(4)
    nav=[("c_accueil","🏠"),("c_courses","🚖"),("c_mes","📋"),("c_profil","👤")]
    for i,(k,ic) in enumerate(nav):
        with cols[i]:
            if st.button(ic, key=f"cn_{k}"):
                st.session_state.page_chauffeur=k
                st.rerun()

def back_btn(page_key, dest, label="← Retour"):
    if st.button(label, key=f"back_{dest}"):
        st.session_state[page_key]=dest
        st.rerun()

def field(label):
    st.markdown(f'<div class="flbl">{label}</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────
#  ACCUEIL (CHOIX RÔLE)
# ────────────────────────────────────────────────────
def page_accueil():
    li = f'<img src="{logo_src}" style="width:100px;filter:drop-shadow(0 0 20px rgba(108,63,212,0.6));animation:float 3s ease-in-out infinite;margin-bottom:16px;"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="role-hero">
        {li}
        <div class="hero-big-name">UbanDrive</div>
        <div class="hero-tag">{APP_TAGLINE}</div>
        <div class="hdivider"></div>
        <div class="hchoose">Choisissez votre profil pour continuer</div>
        <div class="rcards">
            <div class="rcard">
                <span class="rc-icon">🧑‍💼</span>
                <div class="rc-lbl">Passager</div>
                <div class="rc-desc">Demandez une course<br/>et suivez votre trajet</div>
            </div>
            <div class="rcard">
                <span class="rc-icon">🚖</span>
                <div class="rc-lbl">Chauffeur</div>
                <div class="rc-desc">Acceptez des courses<br/>et gérez vos trajets</div>
            </div>
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
        <div class="abox">
            <div style="font-size:1.3rem;margin-bottom:6px;">👩‍💻</div>
            <div class="aname">✦ {AUTHOR} ✦</div>
            <div class="amat">Matricule · {MATRICULE}</div>
            <div style="font-size:0.68rem;color:var(--text2);margin-top:4px;">{COURS} · {UNIVERSITE}</div>
            <div style="font-size:0.65rem;color:var(--text2);">UbanDrive {APP_VERSION} · 2024–2025</div>
        </div>""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────
#  ESPACE PASSAGER
# ────────────────────────────────────────────────────
def p_accueil():
    courses=get_courses()
    total=len(courses)
    dispos=len([c for c in courses if c["statut"]=="disponible"])
    encours=len([c for c in courses if c["statut"]=="en_cours"])
    terminees=len([c for c in courses if c["statut"]=="terminee"])

    li=f'<img src="{logo_src}" style="width:36px;vertical-align:middle;filter:drop-shadow(0 0 6px rgba(108,63,212,0.5));"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div class="page">
    <div class="hero-card">
        <div class="hero-label">Bienvenue sur</div>
        <div class="hero-name">UbanDrive {li}</div>
        <div class="hero-desc">{APP_TAGLINE} — Plateforme de mobilité urbaine à Yaoundé.<br/>Collectez et analysez les données des courses.</div>
        <div class="hero-badge">🚖 {total} course{"s" if total>1 else ""} enregistrée{"s" if total>1 else ""}</div>
    </div>
    <div class="sg">
        <div class="sc">
            <div class="sc-icon" style="background:rgba(108,63,212,0.15);">🚖</div>
            <span class="sc-num">{total}</span>
            <div class="sc-lbl">Total Courses</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#6C3FD4,#8B5CF6);"></div>
        </div>
        <div class="sc">
            <div class="sc-icon" style="background:rgba(34,197,94,0.15);">✅</div>
            <span class="sc-num">{dispos}</span>
            <div class="sc-lbl">Disponibles</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#22C55E,#16A34A);"></div>
        </div>
        <div class="sc">
            <div class="sc-icon" style="background:rgba(37,99,235,0.15);">🚗</div>
            <span class="sc-num">{encours}</span>
            <div class="sc-lbl">En Cours</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#2563EB,#3B82F6);"></div>
        </div>
        <div class="sc">
            <div class="sc-icon" style="background:rgba(139,92,246,0.15);">🏁</div>
            <span class="sc-num">{terminees}</span>
            <div class="sc-lbl">Terminées</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#8B5CF6,#6C3FD4);"></div>
        </div>
    </div>
    <div class="card">
        <div class="clbl">⭐ Fonctionnalités</div>
        <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="display:flex;align-items:center;gap:12px;padding:10px;background:var(--card2);border-radius:10px;">
                <div style="width:36px;height:36px;border-radius:10px;background:rgba(108,63,212,0.2);display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📝</div>
                <div><div style="font-weight:600;font-size:0.88rem;">Collecte intelligente</div><div style="font-size:0.72rem;color:var(--text2);">Enregistrez votre course en 3 étapes</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px;background:var(--card2);border-radius:10px;">
                <div style="width:36px;height:36px;border-radius:10px;background:rgba(34,197,94,0.2);display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📡</div>
                <div><div style="font-weight:600;font-size:0.88rem;">Suivi en temps réel</div><div style="font-size:0.72rem;color:var(--text2);">Votre chauffeur vous contacte directement</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px;background:var(--card2);border-radius:10px;">
                <div style="width:36px;height:36px;border-radius:10px;background:rgba(37,99,235,0.2);display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📊</div>
                <div><div style="font-weight:600;font-size:0.88rem;">Analyses & Régression</div><div style="font-size:0.72rem;color:var(--text2);">Stats descriptives + droite de régression IA</div></div>
            </div>
        </div>
    </div>
    </div>""", unsafe_allow_html=True)

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
        st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:4px;">📝 Nouvelle Course</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:var(--text2);font-size:0.82rem;margin-bottom:18px;">Enregistrez votre trajet à Yaoundé</div>', unsafe_allow_html=True)
        stepper(st.session_state.step)
        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.session_state.step==1: _step1()
        elif st.session_state.step==2: _step2()
        elif st.session_state.step==3: _step3()
    st.markdown('</div>', unsafe_allow_html=True)

def _step1():
    f=st.session_state.form
    st.markdown('<div class="card"><div class="clbl">👤 Informations Passager</div>', unsafe_allow_html=True)
    field("Nom complet *")
    nom=st.text_input("", value=f.get("nom",""), placeholder="Ex: Jean Dupont", key="nom_in", label_visibility="collapsed")
    field("Numéro de téléphone * (+237...)")
    tel=st.text_input("", value=f.get("tel",""), placeholder="+237 6XX XX XX XX", key="tel_in", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🌤️ Conditions Météorologiques</div>', unsafe_allow_html=True)
    meteo=f.get("meteo",METEOS[0])
    cols=st.columns(2)
    for i,m in enumerate(METEOS):
        with cols[i%2]:
            if st.button(("✅ " if meteo==m else "")+m, key=f"m{i}", use_container_width=True):
                st.session_state.form["meteo"]=m; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="clbl">🚦 État du Trafic</div>', unsafe_allow_html=True)
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

def p_mes_courses():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    back_btn("page_passager","accueil")
    st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:14px;">📋 Mes Courses</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="clbl">🔍 Rechercher mes courses</div>', unsafe_allow_html=True)
    field("Votre numéro de téléphone")
    tel=st.text_input("", placeholder="+237 6XX XX XX XX", key="tel_search", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if tel.strip():
        mes=[c for c in get_courses() if c.get("tel")==tel.strip()]
        if not mes: st.info("Aucune course trouvée pour ce numéro.")
        for c in mes:
            s=c.get("statut","")
            bcls="bd" if s=="disponible" else ("bc" if s=="en_cours" else "bt")
            btxt="En attente" if s=="disponible" else ("En cours 🚗" if s=="en_cours" else "Terminée ✓")
            ch_info=f'<span class="chip chip-g">🚖 {c["chauffeur"]} · 📞 {c.get("tel_chauffeur","—")}</span>' if c.get("chauffeur") else ""
            st.markdown(f"""
            <div class="ccard">
                <span class="badge2 {bcls}">{btxt}</span>
                <div class="route"><span class="rpt">📍 {c.get('depart','?')}</span>
                    <span class="rarr">→</span><span class="rpt">🏁 {c.get('arrivee','?')}</span></div>
                <div class="chips">
                    <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
                    <span class="chip">📏 {c.get('distance','?')}</span>
                    {ch_info}
                </div>
                <div style="font-size:0.68rem;color:var(--text2);">Réf : {c['id']} · {c.get('timestamp','')}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def p_analyse():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    back_btn("page_passager","accueil")
    st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:4px;">📊 Analyse des Données</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:var(--text2);font-size:0.78rem;margin-bottom:16px;">{COURS}</div>', unsafe_allow_html=True)

    courses=get_courses()
    df=build_df(courses)
    if df.empty:
        st.info("Aucune donnée. Enregistrez des courses d'abord.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    s=stats_generales(df)
    st.markdown(f"""
    <div class="sg">
        <div class="sc"><div class="sc-icon" style="background:rgba(108,63,212,0.15);">📊</div>
            <span class="sc-num">{s['total']}</span><div class="sc-lbl">Total</div>
            <div class="sc-bar" style="background:var(--grad);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(34,197,94,0.15);">💵</div>
            <span class="sc-num">{s['prix_moyen']:,}</span><div class="sc-lbl">Prix Moyen</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#22C55E,#16A34A);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(37,99,235,0.15);">📈</div>
            <span class="sc-num">{s['prix_median']:,}</span><div class="sc-lbl">Médiane</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#2563EB,#3B82F6);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(139,92,246,0.15);">📉</div>
            <span class="sc-num">{s['prix_ecart']}</span><div class="sc-lbl">Écart-type</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#8B5CF6,#6C3FD4);"></div></div>
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
                    <div><div style="font-size:1.2rem;font-weight:800;color:#6C3FD4;">{a:.1f}</div><div style="font-size:0.65rem;color:var(--text2);">Pente (a)</div></div>
                    <div><div style="font-size:1.2rem;font-weight:800;color:#2563EB;">{b:.1f}</div><div style="font-size:0.65rem;color:var(--text2);">Ordonnée (b)</div></div>
                    <div><div style="font-size:1.2rem;font-weight:800;color:#22C55E;">{r2:.3f}</div><div style="font-size:0.65rem;color:var(--text2);">R²</div></div>
                </div>
                <div style="margin-top:10px;padding:10px;background:var(--card2);border-radius:8px;font-size:0.78rem;">
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
        <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="padding:12px;background:var(--card2);border-radius:10px;border-left:3px solid #6C3FD4;">
                <strong>📈 Régression Linéaire Simple</strong><br/>
                <span style="font-size:0.75rem;color:var(--text2);">Prédit le prix selon la distance</span></div>
            <div style="padding:12px;background:var(--card2);border-radius:10px;border-left:3px solid #2563EB;">
                <strong>📊 Analyse Descriptive Complète</strong><br/>
                <span style="font-size:0.75rem;color:var(--text2);">Moyenne, médiane, écart-type, Q1, Q3, IQR</span></div>
            <div style="padding:12px;background:var(--card2);border-radius:10px;border-left:3px solid #22C55E;">
                <strong>🗺️ Analyse Géographique</strong><br/>
                <span style="font-size:0.75rem;color:var(--text2);">Quartiers les plus fréquentés</span></div>
            <div style="padding:12px;background:var(--card2);border-radius:10px;border-left:3px solid #8B5CF6;">
                <strong>🌤️ Impact Météo & Trafic</strong><br/>
                <span style="font-size:0.75rem;color:var(--text2);">Corrélation conditions/prix</span></div>
        </div></div>""", unsafe_allow_html=True)
        res2=fig_regression(df)
        if res2:
            fig2,a2,b2,r22=res2
            st.plotly_chart(fig2, use_container_width=True, key="reg_ia")
            st.markdown(f"""
            <div class="card"><div class="clbl">📐 Équation Apprise par le Modèle</div>
            <div style="text-align:center;padding:16px;background:var(--card2);border-radius:10px;">
                <div style="font-size:1.3rem;font-weight:800;color:#6C3FD4;">Prix = {a2:.1f}x + {b2:.1f}</div>
                <div style="font-size:0.78rem;color:var(--text2);margin-top:4px;">R² = {r22:.3f} · Précision : {round(r22*100,1)}%</div>
            </div></div>""", unsafe_allow_html=True)

    st.download_button("⬇️ Télécharger CSV",
        data=df.to_csv(index=False, encoding="utf-8"),
        file_name=f"ubandrive_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", key="dl_csv")
    st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────
#  ESPACE CHAUFFEUR
# ────────────────────────────────────────────────────
def c_login():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    back_btn("role","__reset__")
    li=f'<img src="{logo_src}" style="width:64px;filter:drop-shadow(0 0 12px rgba(108,63,212,0.5));animation:float 3s ease-in-out infinite;"/>' if logo_src else "🚖"
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 16px;">
        {li}
        <div style="font-size:1.5rem;font-weight:900;margin-top:10px;
            background:var(--grad);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;background-clip:text;">Espace Chauffeur</div>
        <div style="color:var(--text2);font-size:0.82rem;">Connectez-vous ou créez votre compte</div>
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
    st.markdown('</div>', unsafe_allow_html=True)

def c_accueil():
    ch=st.session_state.chauffeur
    dispos=get_courses_disponibles()
    mes=get_courses_chauffeur(ch['nom'])
    done=[c for c in mes if c['statut']=='terminee']
    encours=[c for c in mes if c['statut']=='en_cours']

    st.markdown(f"""
    <div class="page">
    <div class="hero-card">
        <div class="hero-label">Connecté en tant que</div>
        <div class="hero-name">🚖 {ch['nom']}</div>
        <div class="hero-desc">📞 {ch['tel']} &nbsp;·&nbsp; 🚗 {ch['immat']}</div>
        <div class="hero-badge">🆔 {ch['id']}</div>
    </div>
    <div class="sg">
        <div class="sc"><div class="sc-icon" style="background:rgba(34,197,94,0.15);">🟢</div>
            <span class="sc-num">{len(dispos)}</span><div class="sc-lbl">Disponibles</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#22C55E,#16A34A);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(37,99,235,0.15);">🚗</div>
            <span class="sc-num">{len(encours)}</span><div class="sc-lbl">En cours</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#2563EB,#3B82F6);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(108,63,212,0.15);">🏁</div>
            <span class="sc-num">{len(done)}</span><div class="sc-lbl">Terminées</div>
            <div class="sc-bar" style="background:var(--grad);"></div></div>
        <div class="sc"><div class="sc-icon" style="background:rgba(139,92,246,0.15);">💵</div>
            <span class="sc-num">{sum(c.get('prix',0) for c in done):,}</span><div class="sc-lbl">FCFA</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#8B5CF6,#6C3FD4);"></div></div>
    </div>
    <div class="card"><div class="clbl">⭐ Fonctionnalités Chauffeur</div>
        <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="display:flex;align-items:center;gap:12px;padding:10px;background:var(--card2);border-radius:10px;">
                <div style="width:36px;height:36px;border-radius:10px;background:rgba(34,197,94,0.2);display:flex;align-items:center;justify-content:center;">🚖</div>
                <div><div style="font-weight:600;font-size:0.85rem;">Courses en temps réel</div><div style="font-size:0.7rem;color:var(--text2);">Acceptez les demandes instantanément</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:12px;padding:10px;background:var(--card2);border-radius:10px;">
                <div style="width:36px;height:36px;border-radius:10px;background:rgba(37,99,235,0.2);display:flex;align-items:center;justify-content:center;">📞</div>
                <div><div style="font-weight:600;font-size:0.85rem;">Contact client direct</div><div style="font-size:0.7rem;color:var(--text2);">Numéro visible dès l'acceptation</div></div>
            </div>
        </div>
    </div>
    </div>""", unsafe_allow_html=True)

def c_courses():
    ch=st.session_state.chauffeur
    st.markdown('<div class="page">', unsafe_allow_html=True)
    back_btn("page_chauffeur","c_accueil")
    st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:8px;">🚖 Courses Disponibles</div>', unsafe_allow_html=True)
    if st.button("🔄 Rafraîchir", key="ref"): st.rerun()
    dispos=get_courses_disponibles()
    if not dispos: st.info("Aucune course disponible pour le moment.")
    for c in dispos:
        st.markdown(f"""
        <div class="ccard">
            <span class="badge2 bd">Disponible</span>
            <div class="route"><span class="rpt">📍 {c.get('depart','?')}</span>
                <span class="rarr">→</span><span class="rpt">🏁 {c.get('arrivee','?')}</span></div>
            <div class="chips">
                <span class="chip">👤 {c.get('nom','?')}</span>
                <span class="chip chip-g">📞 {c.get('tel','?')}</span>
                <span class="chip">📏 {c.get('distance','?')}</span>
                <span class="chip">{c.get('meteo','?')}</span>
                <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
            </div>
            <div style="font-size:0.68rem;color:var(--text2);">Réf : {c['id']} · {c.get('timestamp','')}</div>
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
    back_btn("page_chauffeur","c_accueil")
    st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:14px;">📋 Mes Trajets</div>', unsafe_allow_html=True)
    mes=get_courses_chauffeur(ch['nom'])
    if not mes: st.info("Pas encore de courses.")
    for c in mes:
        s=c.get("statut","")
        bcls="bc" if s=="en_cours" else "bt"
        btxt="En cours 🚗" if s=="en_cours" else "Terminée ✓"
        st.markdown(f"""
        <div class="ccard">
            <span class="badge2 {bcls}">{btxt}</span>
            <div class="route"><span class="rpt">📍 {c.get('depart','?')}</span>
                <span class="rarr">→</span><span class="rpt">🏁 {c.get('arrivee','?')}</span></div>
            <div class="chips">
                <span class="chip">👤 {c.get('nom','?')}</span>
                <span class="chip chip-g">📞 {c.get('tel','?')}</span>
                <span class="chip">💵 {c.get('prix',0):,} FCFA</span>
            </div>
            <div style="font-size:0.68rem;color:var(--text2);">Réf : {c['id']}</div>
        </div>""", unsafe_allow_html=True)
        if s=="en_cours":
            if st.button(f"🏁 Terminer", key=f"dn_{c['id']}", use_container_width=True):
                terminer_course(c["id"]); st.success("✅ Terminée !"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def c_profil():
    ch=st.session_state.chauffeur
    mes=get_courses_chauffeur(ch['nom'])
    done=[c for c in mes if c['statut']=='terminee']
    st.markdown(f"""
    <div class="page">
    <div class="card" style="text-align:center;">
        <div style="font-size:3rem;margin-bottom:8px;">👤</div>
        <div style="font-size:1.2rem;font-weight:800;
            background:var(--grad);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;background-clip:text;">{ch['nom']}</div>
        <div style="font-size:0.82rem;color:var(--text2);margin-top:6px;">📞 {ch['tel']}</div>
        <div style="font-size:0.82rem;color:var(--text2);">🚗 {ch['immat']}</div>
        <div style="font-size:0.72rem;color:var(--text2);margin-top:4px;">ID : {ch['id']} · {ch.get('date_inscription','—')[:10]}</div>
    </div>
    <div class="sg">
        <div class="sc"><span class="sc-num">{len(mes)}</span><div class="sc-lbl">Total</div>
            <div class="sc-bar" style="background:var(--grad);"></div></div>
        <div class="sc"><span class="sc-num">{len(done)}</span><div class="sc-lbl">Terminées</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#22C55E,#16A34A);"></div></div>
        <div class="sc" style="grid-column:span 2;"><span class="sc-num">{sum(c.get('prix',0) for c in done):,}</span><div class="sc-lbl">FCFA Encaissés</div>
            <div class="sc-bar" style="background:linear-gradient(90deg,#8B5CF6,#6C3FD4);"></div></div>
    </div>
    </div>""", unsafe_allow_html=True)
    if st.button("🚪 Se déconnecter", use_container_width=True, key="logout"):
        st.session_state.chauffeur=None
        st.session_state.role=None
        st.rerun()

# ────────────────────────────────────────────────────
#  ROUTING
# ────────────────────────────────────────────────────
topbar()
role=st.session_state.role

if role is None:
    page_accueil()
elif role=="passager":
    pg=st.session_state.page_passager
    if pg=="accueil":       p_accueil()
    elif pg=="collecte":    p_collecte()
    elif pg=="mes_courses": p_mes_courses()
    elif pg=="analyse":     p_analyse()
    bottom_nav_p(pg)
elif role=="chauffeur":
    if not st.session_state.chauffeur:
        c_login()
    else:
        pg=st.session_state.page_chauffeur
        if pg=="c_accueil":  c_accueil()
        elif pg=="c_courses":c_courses()
        elif pg=="c_mes":    c_mes_trajets()
        elif pg=="c_profil": c_profil()
        bottom_nav_c(pg)