import streamlit as st
import fitz
import docx
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime

from nlp_utils import (
    extract_resume_skills_strict,
    get_jd_skills,
    filter_real_skills,
    compare_skill_sets
)

st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")


# ----------------------------------------------------
# PREMIUM UI + SIDEBAR NAVIGATION
# ----------------------------------------------------

page_bg = """
<style>

/* --------------------------------------------- */
/* BACKGROUND + GLOBAL UI */
/* --------------------------------------------- */

.stApp {
    background: linear-gradient(135deg, #e3f2fd 0%, #fce4ec 100%);
    background-attachment: fixed;
}

/* Title */
h1 {
    color: #1a237e !important;
    text-align: center !important;
    font-weight: 900 !important;
}

/* Headers */
h2, h3 {
    color: #283593 !important;
    font-weight: 700 !important;
}

/* --------------------------------------------- */
/* MAIN SCREEN TEXT = BLACK  */
/* --------------------------------------------- */

html, body, p {
    color: #000000 !important;
}

/* FIX MARKDOWN TEXT (bullet points, instructions, etc.) */
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {
    color: #000000 !important;
}

/* --------------------------------------------- */
/* SIDEBAR TEXT = WHITE */
/* --------------------------------------------- */

section[data-testid="stSidebar"] {
    background-color: #1a237e !important;
    border-right: 2px solid #0d1b2a;
}

section[data-testid="stSidebar"] * {
    color: white !important;
    font-weight: 500;
}

/* --------------------------------------------- */
/* FILE UPLOADER FIX */
/* --------------------------------------------- */

div[data-testid="stFileUploadDropzone"] {
    background-color: rgba(255, 255, 255, 0.25) !important;
    border: 2px dashed #3949ab !important;
    border-radius: 12px !important;
}

div[data-testid="stFileUploadDropzone"] * {
    color: white !important;
    font-weight: 600 !important;
}

/* --------------------------------------------- */
/* TEXT AREA */
/* --------------------------------------------- */

textarea {
    border-radius: 12px !important;
    padding: 10px !important;
    font-size: 15px !important;
    background-color: #fafafa !important;
    color: #000000 !important;
}

/* --------------------------------------------- */
/* BUTTONS */
/* --------------------------------------------- */

.stButton>button {
    background-color: #283593;
    color: white;
    padding: 10px 18px;
    border-radius: 10px;
    border: none;
    font-size: 16px;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #1a237e;
    transform: scale(1.03);
}

/* --------------------------------------------- */
/* RESULT CARD */
/* --------------------------------------------- */

.result-card {
    background: #ffffffcc;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-top: 20px;
    color: #000000 !important;
}

</style>




"""

st.markdown(page_bg, unsafe_allow_html=True)


# ----------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------

st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "📄 Upload Resume", "🏢 Upload Job Description",
     "📊 Skill Report", "📥 Download PDF"]
)


# ----------------------------------------------------
# TEXT EXTRACTION FUNCTIONS
# ----------------------------------------------------

def extract_text_pdf(file):
    file.seek(0)
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for p in pdf:
        text += p.get_text()
    return text


def extract_text_docx(file):
    file.seek(0)
    d = docx.Document(file)
    return "\n".join([p.text for p in d.paragraphs])


# ----------------------------------------------------
# UNICODE-SAFE TEXT CLEANER
# ----------------------------------------------------

def clean_text_for_pdf(text):
    replace_map = {
        "•": "-",
        "✔": "-",
        "✓": "-",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "′": "'",
        "‣": "-",
        "·": "-",
        "►": "-",
        "→": "->",
        "\u200b": "",
    }
    if text is None:
        return ""
    out = str(text)
    for bad, good in replace_map.items():
        out = out.replace(bad, good)
    return out.encode("latin-1", "replace").decode("latin-1")
# ----------------------------------------------------
# CANDIDATE NAME EXTRACTION
# ----------------------------------------------------

def extract_candidate_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines[:10]:  # look at top section only
        clean = line.replace("-", " ").replace("–", " ").strip()

        if (
            clean.replace(" ", "").isalpha() and        # only letters
            2 <= len(clean.split()) <= 4 and            # 2–4 words
            not any(x in clean.lower() for x in 
                    ["objective", "education", "skills", "project",
                     "experience", "resume", "email", "@", "phone"])
        ):
            return clean.title()

    return "Unknown Candidate"


# ====================================================
# ================     HOME PAGE     ==================
# ====================================================

if page == "🏠 Home":
    st.title("AI Skill Gap Analyzer")
    st.write("""
### Welcome to the AI Skill Gap Analyzer  
This system helps you:

- Upload your **Resume**
- Upload the **Job Description**
- Extract skills using **NLP + SBERT**
- Compare resume vs JD skills
- Generate a **personalized improvement plan**
- Download a **professional PDF report**

Use the sidebar to navigate.
""")


# ====================================================
# ===========   RESUME UPLOAD PAGE    ================
# ====================================================

if page == "📄 Upload Resume":
    st.header("📄 Upload Resume File")

    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="resume")

    if resume_file:
        resume_text = extract_text_pdf(resume_file) if resume_file.name.endswith("pdf") \
                        else extract_text_docx(resume_file)

        st.text_area("Extracted Resume Text:", resume_text, height=350)

        st.session_state["resume_text"] = resume_text
        st.success("Resume uploaded successfully!")


# ====================================================
# ===========   JOB DESCRIPTION UPLOAD   =============
# ====================================================

if page == "🏢 Upload Job Description":
    st.header("🏢 Upload Job Description File")

    jd_file = st.file_uploader("Upload JD", type=["pdf", "docx"], key="jd")

    if jd_file:
        jd_text = extract_text_pdf(jd_file) if jd_file.name.endswith("pdf") \
                        else extract_text_docx(jd_file)

        st.text_area("Extracted JD Text:", jd_text, height=350)

        st.session_state["jd_text"] = jd_text
        st.success("Job Description uploaded successfully!")


# ====================================================
# ===========   SKILL REPORT PAGE   ==================
# ====================================================

if page == "📊 Skill Report":

    if "resume_text" not in st.session_state or "jd_text" not in st.session_state:
        st.warning("Please upload both Resume and Job Description first!")
        st.stop()

    resume_text = st.session_state["resume_text"]
    jd_text = st.session_state["jd_text"]

    st.header("📊 Skill Match Report")

    # Extract skills
    resume_skills = extract_resume_skills_strict(resume_text)
    jd_skills = get_jd_skills(jd_text)

    resume_skills = filter_real_skills(resume_skills)
    jd_skills = filter_real_skills(jd_skills)

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.write("### Extracted Resume Skills:", resume_skills)
    st.write("### Extracted JD Skills:", jd_skills)
    st.markdown("</div>", unsafe_allow_html=True)

    # Compare using SBERT
    result = compare_skill_sets(resume_skills, jd_skills)

    matched = [m[1] for m in result["matches"]]
    missing = result["missing"]

    # Animated progress display
    st.subheader("Skill Match Percentage")
    st.progress(result["match_pct"] / 100)

    st.write(f"### Match Score: **{result['match_pct']}%**")

    # Pie Chart
    labels = ["Matched", "Missing"]
    sizes = [len(matched), len(missing)]
    colors = ["#2ECC71", "#E74C3C"]

    fig, ax = plt.subplots(figsize=(2.6, 2.6), dpi=110)
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, textprops={'fontsize': 8})
    ax.set_title("Skill Match Breakdown", fontsize=10)
    ax.axis("equal")

    st.pyplot(fig)

    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
    st.write("### ✔ Matched Skills:", matched)
    st.write("### ❌ Missing Skills:", missing)
    st.markdown("</div>", unsafe_allow_html=True)

    # Save for PDF page
    st.session_state["matched"] = matched
    st.session_state["missing"] = missing
    st.session_state["match_pct"] = result["match_pct"]
    st.session_state["pie_chart"] = fig

    # Extract candidate name
    st.session_state["candidate_name"] = extract_candidate_name(resume_text)
# ====================================================
# ============ PERSONALIZED PLAN GENERATOR ===========
# ====================================================

def generate_personalized_plan(missing_skills):
    missed = [m.lower() for m in missing_skills]
    plan = []

    # Programming languages
    prog_keys = ("python", "java", "c++", "c#", "javascript", "js")
    if any(k in s for s in missed for k in prog_keys):
        plan += [
            "- Programming Skills:",
            "  * Build 2 small projects using Python/Java.",
            "  * Practice 3 problems daily on HackerRank.",
            "  * Follow Codebasics / FreeCodeCamp tutorials."
        ]

    # Git / GitHub
    if any("git" in s or "github" in s for s in missed):
        plan += [
            "- Git & GitHub:",
            "  * Learn Git basics: add, commit, branch, merge.",
            "  * Upload all projects to GitHub.",
            "  * Contribute to one open-source repo."
        ]

    # Machine Learning
    if any("machine" in s or "ml" in s for s in missed):
        plan += [
            "- Machine Learning:",
            "  * Learn regression & classification basics.",
            "  * Train simple ML models using scikit-learn.",
            "  * Take Coursera ML by Andrew Ng."
        ]

    # Cloud (AWS, Azure)
    if any(x in s for s in missed for x in ("aws", "azure", "cloud", "gcp")):
        plan += [
            "- Cloud Fundamentals:",
            "  * Learn basics of AWS EC2 and S3.",
            "  * Deploy a small Flask/Streamlit app.",
            "  * Watch AWS free tutorials on YouTube."
        ]

    # Databases
    if any("sql" in s or "mongo" in s for s in missed):
        plan += [
            "- Databases:",
            "  * Practice SQL joins, group-by, subqueries.",
            "  * Learn MongoDB CRUD operations.",
            "  * Build a mini project using a database."
        ]

    # Web development & APIs
    if any(x in s for s in missed for x in ("html", "css", "js", "api", "frontend", "backend")):
        plan += [
            "- Web Development:",
            "  * Build 3 simple web pages.",
            "  * Integrate a public API (Weather, News).",
            "  * Learn basics of frontend & backend flow."
        ]

    # Soft skills
    if any(x in s for s in missed for x in ("communication", "team", "adapt", "problem")):
        plan += [
            "- Soft Skills:",
            "  * Practice speaking 10 mins/day.",
            "  * Participate in team coding discussions.",
            "  * Improve problem-solving using puzzles."
        ]

    # General skills
    if any(x in s for s in missed for x in ("initiative", "learn", "motivation", "collaboration")):
        plan += [
            "- Work Habits:",
            "  * Build 1 project every week.",
            "  * Maintain a learning journal.",
            "  * Learn actively by implementing tutorials."
        ]

    # If no category matched
    if not plan:
        plan = [
            "- Practice small projects weekly.",
            "- Improve using YouTube tutorials.",
            "- Push all work to GitHub."
        ]

    final_lines = []
    for line in plan:
        final_lines.append(clean_text_for_pdf(line))

    return final_lines


# ====================================================
# =============== DOWNLOAD PDF PAGE ==================
# ====================================================

if page == "📥 Download PDF":

    if "resume_text" not in st.session_state:
        st.warning("Upload resume first!")
        st.stop()

    st.header("📥 Download Your Professional Skill Gap Report")

    candidate_name = st.session_state.get("candidate_name", "Unknown Candidate")
    matched = st.session_state.get("matched", [])
    missing = st.session_state.get("missing", [])
    match_pct = st.session_state.get("match_pct", 0)
    pie_chart = st.session_state.get("pie_chart", None)

    st.write(f"### Candidate Name Identified: **{candidate_name}**")

    if st.button("Generate PDF"):

        pdf = FPDF()
        pdf.add_page()

        # ---------------- HEADER ----------------
        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(30, 60, 120)
        pdf.cell(200, 12, txt="AI Skill Gap Analysis Report", ln=1, align="C")

        # Candidate name
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=clean_text_for_pdf(f"Candidate: {candidate_name}"), ln=1, align="C")

        # Timestamp
        pdf.set_font("Arial", size=11)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M")
        pdf.set_text_color(120, 120, 120)
        pdf.cell(200, 6, txt=clean_text_for_pdf(f"Generated: {timestamp}"), ln=1, align="C")
        pdf.ln(5)

        # Summary Box
        pdf.set_fill_color(230, 240, 255)
        pdf.rect(10, pdf.get_y(), 190, 14, "F")
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(20, 50, 120)
        pdf.ln(1)
        pdf.cell(200, 10, txt=clean_text_for_pdf(f"Skill Match Score: {match_pct}%"), ln=1, align="C")
        pdf.ln(2)

        # Save and insert pie chart
        if pie_chart:
            pie_chart.savefig("pie_chart.png", dpi=130, bbox_inches="tight")
            pdf.image("pie_chart.png", x=55, y=pdf.get_y(), w=80)
            pdf.ln(70)

        # Matched Skills
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 80, 0)
        pdf.cell(200, 10, txt="Matched Skills", ln=1)

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        for m in matched:
            pdf.cell(200, 8, txt=clean_text_for_pdf(f"- {m}"), ln=1)
        pdf.ln(3)

        # Missing Skills
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(200, 10, txt="Skills You Need To Learn", ln=1)

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        for m in missing:
            pdf.cell(200, 8, txt=clean_text_for_pdf(f"- {m}"), ln=1)
        pdf.ln(3)

        # Personalized Plan
        plan_lines = generate_personalized_plan(missing)

        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(20, 20, 120)
        pdf.cell(200, 10, txt="Personalized Improvement Plan", ln=1)

        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)
        for line in plan_lines:
            pdf.cell(200, 7, txt=line, ln=1)

        # Footer
        pdf.set_y(275)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 10, clean_text_for_pdf("Generated by AI SkillGap Analyzer • Powered by SBERT"), 0, 0, "C")

        # Save PDF
        pdf.output("FINAL_SkillGapReport.pdf")

        st.success("Your downloadable PDF is ready!")

        st.download_button(
            "📥 Download Final PDF",
            data=open("FINAL_SkillGapReport.pdf", "rb").read(),
            file_name="SkillGapReport.pdf",
            mime="application/pdf"
        )
# ====================================================
# ===============  END OF APPLICATION  ===============
# ====================================================

# If the user tries to open Skill Report or PDF page
# without uploading necessary files, Streamlit handles it.
# No code needed here — your app is complete.

st.sidebar.info("Developed using NLP + SBERT + Streamlit UI Enhancements")
