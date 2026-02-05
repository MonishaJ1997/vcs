import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Extract text from resume PDF
def extract_resume_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()


# Calculate job match percentage
def calculate_match(resume_text, job_text):
    documents = [resume_text, job_text]

    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(documents)

    similarity = cosine_similarity(matrix[0:1], matrix[1:2])

    return round(similarity[0][0] * 100, 2)


# Simple skill analyzer
def analyze_resume(resume_text):
    skills = ["python", "django", "sql", "html", "css", "javascript"]
    found = []

    for skill in skills:
        if skill in resume_text:
            found.append(skill)

    return found
