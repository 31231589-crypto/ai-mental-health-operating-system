import os
from datetime import datetime
from functools import wraps
from io import BytesIO
from collections import Counter

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from database import User, MoodEntry, JournalEntry, Prediction, init_db, db
from predict import analyze_sentiment, predict_status
from train_model import ensure_model_exists


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "mental-health-ai-project-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)


MOOD_OPTIONS = [
    ("Happy", "Happy 😊"),
    ("Calm", "Calm 🙂"),
    ("Neutral", "Neutral 😐"),
    ("Sad", "Sad 😔"),
    ("Angry", "Angry 😠"),
    ("Anxious", "Anxious 😰"),
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_user():
    user = None
    if "user_id" in session:
        user = User.query.get(session["user_id"])
    return {"current_user": user}


@app.before_request
def ensure_training_model():
    if not os.path.exists(os.path.join(BASE_DIR, "model.pkl")):
        ensure_model_exists()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html", show_register_link=True)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        age = request.form.get("age", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            age=int(age) if age.isdigit() else None,
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user_id"])
    entries = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.created_at.desc()).all()
    journals = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()

    latest_entry = entries[0] if entries else None
    latest_journal = journals[0] if journals else None
    latest_prediction = predictions[0] if predictions else None

    stress_values = [entry.stress_level for entry in entries[-7:]][::-1]
    labels = [entry.created_at.strftime("%b %d") for entry in entries[-7:]][::-1]
    sleep_values = [entry.sleep_hours for entry in entries[-7:]][::-1]

    mood_distribution = Counter(entry.mood for entry in entries)
    distribution_labels = list(mood_distribution.keys())
    distribution_values = list(mood_distribution.values())

    if latest_entry:
        stress_level = latest_entry.stress_level
        if stress_level <= 3:
            stress_badge = "Low Stress"
            stress_class = "bg-success"
        elif stress_level <= 6:
            stress_badge = "Moderate Stress"
            stress_class = "bg-warning text-dark"
        elif stress_level <= 8:
            stress_badge = "High Stress"
            stress_class = "bg-orange"
        else:
            stress_badge = "Critical Stress"
            stress_class = "bg-danger"

        score = 100 - (stress_level * 7) - max(0, 8 - latest_entry.sleep_hours) * 4 - max(0, 30 - latest_entry.exercise_minutes) * 0.5 - max(0, 2.0 - latest_entry.water_intake) * 8 - max(0, latest_entry.screen_time - 4) * 3
        wellness_score = max(0, min(100, int(score)))
    else:
        stress_level = 0
        stress_badge = "No records"
        stress_class = "bg-secondary"
        wellness_score = 0

    if latest_prediction:
        prediction_text = latest_prediction.prediction_label
        risk_level = latest_prediction.risk_level
    else:
        prediction_text = "No prediction yet"
        risk_level = "Pending"

    return render_template(
        "dashboard.html",
        entries=entries,
        latest_entry=latest_entry,
        latest_journal=latest_journal,
        latest_prediction=latest_prediction,
        stress_level=stress_level,
        stress_badge=stress_badge,
        stress_class=stress_class,
        wellness_score=wellness_score,
        prediction_text=prediction_text,
        risk_level=risk_level,
        labels=labels,
        stress_values=stress_values,
        sleep_values=sleep_values,
        distribution_labels=distribution_labels,
        distribution_values=distribution_values,
        mood_distribution=mood_distribution,
    )


@app.route("/mood", methods=["GET", "POST"])
@login_required
def mood():
    user = User.query.get(session["user_id"])
    entries = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.created_at.desc()).all()

    if request.method == "POST":
        mood = request.form.get("mood", "Neutral")
        sleep_hours = float(request.form.get("sleep_hours", 0))
        exercise_minutes = int(request.form.get("exercise_minutes", 0))
        water_intake = float(request.form.get("water_intake", 0))
        screen_time = float(request.form.get("screen_time", 0))
        stress_level = int(request.form.get("stress_level", 5))
        journal_notes = request.form.get("journal_notes", "").strip()

        entry = MoodEntry(
            mood=mood,
            sleep_hours=sleep_hours,
            exercise_minutes=exercise_minutes,
            water_intake=water_intake,
            screen_time=screen_time,
            stress_level=stress_level,
            journal_notes=journal_notes,
            user_id=user.id,
        )
        db.session.add(entry)
        db.session.commit()

        sentiment_result = analyze_sentiment(journal_notes or f"I feel {mood.lower()} today.")
        journal_entry = JournalEntry(
            title=f"Entry {entry.created_at.strftime('%b %d')}",
            content=journal_notes or f"Mood logged: {mood}",
            sentiment=sentiment_result["sentiment"],
            sentiment_score=sentiment_result["score"],
            confidence=str(sentiment_result["confidence"]),
            suggested_mood=sentiment_result["suggested_mood"],
            user_id=user.id,
        )
        db.session.add(journal_entry)

        prediction_result = predict_status(
            age=user.age or 25,
            sleep_hours=sleep_hours,
            exercise_minutes=exercise_minutes,
            water_intake=water_intake,
            screen_time=screen_time,
            mood=mood,
            stress_level=stress_level,
            sentiment=sentiment_result["sentiment"],
        )
        prediction = Prediction(
            prediction_label=prediction_result["prediction_label"],
            risk_level=prediction_result["risk_level"],
            confidence_score=prediction_result["confidence_score"],
            recommendations="\n".join(prediction_result["recommendations"]),
            user_id=user.id,
        )
        db.session.add(prediction)
        db.session.commit()
        flash("Mood entry recorded successfully.", "success")
        return redirect(url_for("mood"))

    return render_template("mood.html", mood_options=MOOD_OPTIONS, entries=entries)


@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    user = User.query.get(session["user_id"])
    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Personal Journal"
        content = request.form.get("content", "").strip()
        if not content:
            flash("Please write something in your journal.", "warning")
            return redirect(url_for("journal"))

        sentiment_result = analyze_sentiment(content)
        entry = JournalEntry(
            title=title,
            content=content,
            sentiment=sentiment_result["sentiment"],
            sentiment_score=sentiment_result["score"],
            confidence=str(sentiment_result["confidence"]),
            suggested_mood=sentiment_result["suggested_mood"],
            user_id=user.id,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Journal saved and analyzed.", "success")
        return redirect(url_for("journal"))

    return render_template("journal.html", journal_entries=journal_entries)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        age = request.form.get("age", "").strip()
        if age.isdigit():
            user.age = int(age)
            db.session.commit()
            flash("Profile updated.", "success")
        else:
            flash("Please enter a valid age.", "warning")

    mood_entries = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.created_at.desc()).all()
    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()
    return render_template("profile.html", user=user, mood_entries=mood_entries, journal_entries=journal_entries, predictions=predictions)


@app.route("/report")
def report():
    user = User.query.get(session["user_id"])
    mood_entries = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.created_at.desc()).all()
    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()
    return render_template("report.html", user=user, mood_entries=mood_entries, journal_entries=journal_entries, predictions=predictions)


@app.route("/report/download")
@login_required
def download_report():
    user = User.query.get(session["user_id"])
    mood_entries = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.created_at.desc()).all()
    journal_entries = JournalEntry.query.filter_by(user_id=user.id).order_by(JournalEntry.created_at.desc()).all()
    predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Mental Health Monitoring Report", styles["Title"]))
    story.append(Paragraph(f"User: {user.username}", styles["Heading2"]))
    story.append(Paragraph(f"Email: {user.email}", styles["BodyText"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Mood History", styles["Heading2"]))
    row_data = [["Date", "Mood", "Stress", "Sleep", "Exercise"]]
    for entry in mood_entries[:10]:
        row_data.append([
            entry.created_at.strftime("%Y-%m-%d"),
            entry.mood,
            str(entry.stress_level),
            str(entry.sleep_hours),
            str(entry.exercise_minutes),
        ])
    story.append(Table(row_data, repeatRows=1))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Sentiment Analysis", styles["Heading2"]))
    for journal in journal_entries[:5]:
        story.append(Paragraph(f"{journal.title}: {journal.sentiment} ({journal.sentiment_score})", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Predictions", styles["Heading2"]))
    for prediction in predictions[:5]:
        story.append(Paragraph(f"{prediction.prediction_label} - {prediction.risk_level}", styles["BodyText"]))
        story.append(Paragraph(prediction.recommendations, styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{user.username}_report.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)
