
def review_resume(resume_text, job_title="", job_description=""):
    resume = resume_text.lower()
    job = job_description.lower()

    suggestions = []

    if not resume_text.strip():
        return "No resume text was extracted. Please check your PDF or DOCX file."

    if job_title:
        suggestions.append(f"Target role: {job_title}")

    skills = [
        "python", "java", "sql", "c++", "html", "css",
        "javascript", "machine learning", "flask", "git",
        "data structures", "pandas", "numpy", "scikit-learn"
    ]

    matched = [skill for skill in skills if skill in resume and skill in job]
    missing = [skill for skill in skills if skill in job and skill not in resume]

    suggestions.append(
        "\nRelevant skills found: " +
        (", ".join(matched) if matched else "None of the checked skills")
    )

    suggestions.append(
        "\nSkills to consider adding if you genuinely have them: " +
        (", ".join(missing) if missing else "No checked skill gaps found")
    )

    if "project" not in resume:
        suggestions.append(
            "\nSuggestion: Add a Projects section describing your work, "
            "technologies used, and results."
        )

    if "education" not in resume:
        suggestions.append(
            "\nSuggestion: Add an Education section with your degree and university."
        )

    suggestions.append(
        "\nGeneral tips: Use clear headings, quantify project results where possible, "
        "and tailor your resume to the job description."
    )

    return "\n".join(suggestions)
