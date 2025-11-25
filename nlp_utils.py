# nlp_utils.py

import re
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer, util


# Strict skill dictionary
SKILL_DB = [
    # Programming
    "python","java","c","c++","html","css","javascript","sql",

    # Databases
    "mongodb","mysql","postgresql",

    # AI / ML
    "machine learning","deep learning","nlp","tensorflow","pytorch","sklearn",
    "neural networks","data analysis","data science",

    # Tools
    "git","github","docker","flask","django","streamlit","api integration",

    # Cloud
    "aws","azure","gcp",

    # Soft skills (ONLY core)
    "problem-solving","creativity","adaptability","communication","teamwork"
]

# Load sentence-BERT model
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load spaCy
nlp = spacy.load("en_core_web_sm")


# ---------- CLEAN TEXT ----------
def clean_text(text):
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'\+?\d[\d\s\-]{6,}\d', ' ', text)
    text = re.sub(r'http\S+', ' ', text)
    return text.strip()


# ---------- STRICT RESUME SKILL EXTRACTION ----------
def extract_resume_skills_strict(text):
    text = text.lower()

    sections = {
        "core skills": [],
        "intermediate skills": [],
        "familiar with": [],
        "soft skills": [],
        "skills": []
    }

    patterns = {
        "core skills": r"core skills(.*?)(intermediate skills|familiar with|soft skills|education|languages|projects|$)",
        "intermediate skills": r"intermediate skills(.*?)(core skills|familiar with|soft skills|education|languages|projects|$)",
        "familiar with": r"familiar with(.*?)(core skills|intermediate skills|soft skills|education|languages|projects|$)",
        "soft skills": r"soft skills(.*?)(core skills|intermediate skills|familiar with|education|languages|projects|$)",
        "skills": r"skills(.*?)(core skills|intermediate skills|familiar with|soft skills|education|languages|projects|$)"
    }

    all_skills = []

    for sec, patt in patterns.items():
        match = re.search(patt, text, flags=re.S)
        if match:
            block = match.group(1)
            items = re.split(r"[,\n•\-]+", block)
            cleaned = [i.strip().lower() for i in items if len(i.strip()) > 1]
            all_skills.extend(cleaned)

    return list(dict.fromkeys(all_skills))


# ---------- CLEAN JD SKILL EXTRACTION ----------
def get_jd_skills(text):
    text = text.lower()
    lines = re.split(r"\n+", text)

    # Step 1: Extract bullet lines
    bullets = [l.strip("• ").strip() for l in lines if l.strip().startswith("•")]

    # Step 2: Split bullet items
    raw_items = []
    for b in bullets:
        parts = re.split(r"[,&/]| and ", b)
        raw_items.extend([p.strip() for p in parts])

    # Step 3: Keep ONLY skills that match SKILL_DB
    clean = []
    for item in raw_items:
        for skill in SKILL_DB:
            if skill in item:
                clean.append(skill)

    # Step 4: Remove duplicates
    clean = list(dict.fromkeys(clean))

    return clean



# ---------- FILTER REAL SKILLS ----------
def filter_real_skills(skill_list):
    ban = ["student", "resume", "email", "tamil", "tiruppur", "address"]

    real = []
    for s in skill_list:
        if any(b in s for b in ban):
            continue
        if len(s) <= 2:
            continue
        real.append(s)

    return list(dict.fromkeys(real))


# ---------- SBERT SEMANTIC MATCHING ----------
def compare_skill_sets(resume_skills, jd_skills, threshold=0.60):
    if not resume_skills or not jd_skills:
        return {"matches": [], "missing": jd_skills, "match_pct": 0}

    emb_resume = sbert_model.encode(resume_skills, convert_to_tensor=True)
    emb_jd = sbert_model.encode(jd_skills, convert_to_tensor=True)

    sim = util.cos_sim(emb_jd, emb_resume).cpu().numpy()

    matches = []
    missing = []

    for j_idx, j_skill in enumerate(jd_skills):
        best_idx = np.argmax(sim[j_idx])
        best_score = sim[j_idx][best_idx]

        if best_score >= threshold:
            matches.append((resume_skills[best_idx], j_skill, float(best_score)))
        else:
            missing.append(j_skill)

    match_pct = int((len(matches) / len(jd_skills)) * 100)

    return {
        "matches": matches,
        "missing": missing,
        "match_pct": match_pct
    }
