
import sqlite3
import tempfile
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from resume_parser import parse_resume
from analyzer import analyze_resume

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "resume_tracker.db"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                job_title TEXT NOT NULL,
                score INTEGER NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_analysis(filename, job_title, result):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO analyses
            (filename, job_title, score, matched_skills, missing_skills)
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename,
            job_title,
            result["skill_match"],
            ", ".join(result["matched_skills"]),
            ", ".join(result["missing_skills"])
        ))
        return cursor.lastrowid


init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    uploaded = request.files.get("resume")
    job_title = request.form.get("job_title", "").strip()
    job_description = request.form.get("job_description", "").strip()

    if not uploaded or not uploaded.filename:
        return render_template(
            "index.html", error="Please upload a resume."
        )

    if not job_title or not job_description:
        return render_template(
            "index.html",
            error="Please enter the job title and job description."
        )

    filename = secure_filename(uploaded.filename)
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return render_template(
            "index.html",
            error="Please upload a PDF or DOCX resume."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=extension, delete=False
        ) as temp:
            temp_path = Path(temp.name)
            uploaded.save(temp_path)

        resume = parse_resume(temp_path)

        if not resume["text"].strip():
            return render_template(
                "index.html",
                error=(
                    "No readable text was found. "
                    "Try a text-based PDF or DOCX file."
                )
            )

        result = analyze_resume(
            resume, job_title, job_description
        )

        analysis_id = save_analysis(
            filename, job_title, result
        )

        return render_template(
            "result.html",
            filename=filename,
            job_title=job_title,
            resume=resume,
            result=result,
            analysis_id=analysis_id
        )

    except Exception:
        app.logger.exception("Resume analysis failed")
        return render_template(
            "index.html",
            error=(
                "Analysis failed. Check the VS Code terminal "
                "for the detailed error."
            )
        ), 500

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


@app.route("/history")
def history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM analyses ORDER BY id DESC
        """).fetchall()

    return render_template("history.html", analyses=rows)


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        error="The uploaded file must be smaller than 5 MB."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
