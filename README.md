🚀 AI-Based Skill Gap Analyzer
Smart Resume vs Job Description Matching using NLP + SBERT

The AI-Based Skill Gap Analyzer is an intelligent system that evaluates how closely a candidate’s resume aligns with a job description.
Using Natural Language Processing (NLP) and Sentence-BERT (SBERT) embeddings, the tool extracts skills, compares them semantically, identifies gaps, and generates a personalized improvement plan.

Built with an interactive Streamlit UI, it provides a smooth user experience with:

📄 Resume & Job Description upload (PDF/DOCX)

🧠 Automatic skill extraction using NLP

🤖 Semantic similarity matching using SBERT

📊 Visual match score with pie chart

📝 Instant improvement recommendations

📥 Professional PDF report generator

🎨 Modern UI with gradient background & sidebar navigation

This tool helps students, job seekers, and HR teams analyze job readiness with clarity and accuracy.

✨ Features

✔️ Extracts skills from resume & job description
✔️ Semantic matching using SBERT (beyond keyword matching)
✔️ Calculates match percentage
✔️ Highlights missing skills
✔️ Generates personalized learning roadmap
✔️ Professional downloadable PDF report
✔️ Beautiful Streamlit UI with sidebar navigation

🧠 Technologies Used

Python 3

Streamlit – UI

spaCy – NLP preprocessing

Sentence-BERT (SBERT) – Semantic similarity

Matplotlib – Pie chart visualization

FPDF – PDF report generation

📌 Project Structure
AI-Based-Skill-Gap-Analyzer/
│── app.py                # Main Streamlit application
│── nlp_utils.py          # NLP + SBERT skill extraction & matching logic
│── requirements.txt       # Required dependencies
│── LICENSE                # MIT License
│── README.md              # Project documentation
│── .gitignore             # Ignore venv, cache, etc.

⚡ Installation & Usage
1️⃣ Clone the repository
git clone https://github.com/KaviBharathi643/AI-Based-Skill-Gap-Analyzer.git
cd AI-Based-Skill-Gap-Analyzer

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run the application
streamlit run app.py

🖥️ UI Preview (Features)

📝 Resume Upload

🏢 Job Description Upload

🔍 Skill Extraction

📊 Match Score Visualization

🧩 Skill Gap Identification

📥 Downloadable PDF Report

📘 License

This project is licensed under the MIT License.

⭐ Show Your Support

If this project helped you, please star the repository ⭐
It motivates further development and features!
