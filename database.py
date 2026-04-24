import json, os
from datetime import datetime

COURSES_FILE    = "courses.json"
CHAUFFEURS_FILE = "chauffeurs.json"

def _load(f):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else []

def _save(f, d):
    json.dump(d, open(f,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def get_courses():       return _load(COURSES_FILE)
def save_courses(d):     _save(COURSES_FILE, d)
def get_chauffeurs():    return _load(CHAUFFEURS_FILE)
def save_chauffeurs(d):  _save(CHAUFFEURS_FILE, d)

def ajouter_course(data: dict) -> dict:
    courses = get_courses()
    course  = {
        "id": f"UBD-{len(courses)+1:04d}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "statut": "disponible",
        "chauffeur": None, "tel_chauffeur": None,
        "heure_acceptation": None, "heure_fin": None,
        **data
    }
    courses.append(course)
    save_courses(courses)
    return course

def accepter_course(course_id, nom_chauffeur, tel_chauffeur) -> bool:
    courses = get_courses()
    for c in courses:
        if c["id"] == course_id and c["statut"] == "disponible":
            c.update({"statut":"en_cours","chauffeur":nom_chauffeur,
                      "tel_chauffeur":tel_chauffeur,
                      "heure_acceptation":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_courses(courses)
            return True
    return False

def terminer_course(course_id) -> bool:
    courses = get_courses()
    for c in courses:
        if c["id"] == course_id and c["statut"] == "en_cours":
            c.update({"statut":"terminee",
                      "heure_fin":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_courses(courses)
            return True
    return False

def get_courses_disponibles():
    return [c for c in get_courses() if c["statut"]=="disponible"]

def get_courses_chauffeur(nom):
    return [c for c in get_courses() if c.get("chauffeur")==nom]

def inscrire_chauffeur(nom, tel, immat) -> dict:
    chs = get_chauffeurs()
    for ch in chs:
        if ch["tel"] == tel:
            return ch
    ch = {"id":f"CH-{len(chs)+1:03d}","nom":nom,"tel":tel,"immat":immat,
          "date_inscription":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    chs.append(ch)
    save_chauffeurs(chs)
    return ch

def get_chauffeur_by_tel(tel):
    for ch in get_chauffeurs():
        if ch["tel"] == tel: return ch
    return None