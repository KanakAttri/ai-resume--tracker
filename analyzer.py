
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python", "java", "c++", "javascript", "html", "css",
    "sql", "mysql", "sqlite", "mongodb", "flask", "django",
    "fastapi", "git", "github", "data structures", "algorithms",
    "object oriented programming", "oop",
    "machine learning", "deep learning",
    "artificial intelligence", "natural language processing",
    "nlp", "pandas", "numpy", "scikit-learn",
    "matplotlib", "data analysis", "data visualization",
    "excel", "power bi", "tableau", "linux", "docker",
    "aws", "react", "node.js", "rest api", "restful api",
    "communication", "problem solving", "debugging",
    "testing", "json", "csv", "networking",
    "socket programming", "computer vision",
    "tensorflow", "pytorch", "statistics", "data mining"
]


def normalize(text):
    text = text.lower()
    text = text.replace("object-oriented", "object oriented")
    return re.sub(r"\s+", " ", text).strip()


def contains_skill(text, skill):
    pattern = (
        r"(?<![a-z0-9+#.])"
        + re.escape(skill)
        + r"(?![a-z0-9+#.])"
    )
    return re.search(pattern, text) is not None


def extract_skills(text):
    text = normalize(text)
    found = []

    for skill in SKILLS:
        if contains_skill(text, skill):
            if skill == "oop":
                skill = "object oriented programming"

            if skill not in found:
                found.append(skill)

    return found


def calculate_similarity(resume_text, job_description):
    """Free local TF-IDF and cosine similarity."""

    if not resume_text.strip() or not job_description.strip():
        return 0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        vectors = vectorizer.fit_transform([
            resume_text,
            job_description
        ])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(float(similarity) * 100)

    except ValueError:
        return 0


def analyze_resume(resume_data, job_title, job_description):
    resume_text = resume_data["text"]

    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    if required_skills:
        skill_match = round(
            len(matched_skills) / len(required_skills) * 100
        )
    else:
        skill_match = 0

    semantic_similarity = calculate_similarity(
        resume_text,
        job_title + "\n" + job_description
    )

    sections = resume_data.get("sections", {})

    sections_found = [
        name.title()
        for name, content in sections.items()
        if content.strip()
    ]

    return {
        "skill_match": skill_match,
        "semantic_similarity": semantic_similarity,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_count": len(matched_skills),
        "required_count": len(required_skills),
        "sections_found": sections_found
    }
