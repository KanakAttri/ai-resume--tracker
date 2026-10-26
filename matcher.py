
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python", "java", "c++", "javascript",
    "html", "css", "sql", "mysql", "mongodb",
    "flask", "django", "spring boot", "react",
    "node.js", "rest api", "git", "github",
    "machine learning", "deep learning",
    "data structures", "oop", "pandas",
    "numpy", "scikit-learn", "docker", "aws"
]


def find_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found.append(skill)

    return found


def analyze_resume(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words="english")

    vectors = vectorizer.fit_transform([
        resume_text,
        job_description
    ])

    similarity = float(
        cosine_similarity(vectors[0], vectors[1])[0][0]
    )

    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)

    matched = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    coverage = (
        len(matched) / len(job_skills)
        if job_skills else 0
    )

    score = round(
        100 * (0.4 * similarity + 0.6 * coverage)
    )

    suggestions = []

    if missing:
        suggestions.append(
            "Review these job requirements: "
            + ", ".join(missing)
        )

    if not job_skills:
        suggestions.append(
            "Add specific technical skills to the job description."
        )

    if not suggestions:
        suggestions.append(
            "Make sure your projects demonstrate your relevant skills."
        )

    return {
        "score": score,
        "similarity": round(similarity * 100, 2),
        "skill_coverage": round(coverage * 100, 2),
        "matched": matched,
        "missing": missing,
        "resume_skills": resume_skills,
        "suggestions": suggestions
    }
