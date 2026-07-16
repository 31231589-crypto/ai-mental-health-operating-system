from __future__ import annotations
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from textblob import TextBlob

from train_model import ensure_model_exists, MOOD_MAP, SENTIMENT_MAP

MODEL_PATH = Path(__file__).with_name("model.pkl")


def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    confidence = min(0.99, max(0.1, abs(polarity)))
    if sentiment == "Neutral":
        confidence = 0.65

    if sentiment == "Positive":
        suggested_mood = "Happy"
    elif sentiment == "Negative":
        suggested_mood = "Calm"
    else:
        suggested_mood = "Neutral"

    return {
        "sentiment": sentiment,
        "score": round(float(polarity), 3),
        "confidence": round(float(confidence), 3),
        "suggested_mood": suggested_mood,
    }


def get_recommendations(prediction_label: str):
    mapping = {
        "Healthy": [
            "Keep maintaining your healthy routine.",
            "Continue exercising regularly.",
            "Stay hydrated and keep good sleep habits.",
        ],
        "Mild Stress": [
            "Improve your sleep quality.",
            "Drink enough water and take regular breaks.",
            "Consider light stretching or a short walk.",
        ],
        "Moderate Stress": [
            "Try meditation or breathing exercises.",
            "Reduce screen time for a while.",
            "Exercise daily and keep a consistent routine.",
        ],
        "High Stress": [
            "Practice breathing exercises and rest whenever possible.",
            "Reach out to trusted friends, family, or a support network.",
            "If stress continues, consider speaking with a qualified mental health professional.",
        ],
    }
    return mapping.get(prediction_label, mapping["Mild Stress"])


def predict_status(age: int, sleep_hours: float, exercise_minutes: int, water_intake: float, screen_time: float, mood: str, stress_level: int, sentiment: str):
    payload = ensure_model_exists()
    model = payload["model"]
    feature_columns = payload["feature_columns"]

    features = pd.DataFrame([
        {
            "Age": age,
            "Sleep_Hours": sleep_hours,
            "Exercise_Minutes": exercise_minutes,
            "Water_Intake": water_intake,
            "Screen_Time": screen_time,
            "Mood": MOOD_MAP.get(mood, 2),
            "Stress_Level": stress_level,
            "Sentiment": SENTIMENT_MAP.get(sentiment, 1),
        }
    ])

    prediction = model.predict(features[feature_columns])[0]
    proba = model.predict_proba(features[feature_columns])[0]
    confidence = float(np.max(proba))

    risk_level = "Low"
    if prediction in {"Moderate Stress", "High Stress"}:
        risk_level = "High"
    elif prediction == "Mild Stress":
        risk_level = "Medium"

    return {
        "prediction_label": prediction,
        "risk_level": risk_level,
        "confidence_score": round(confidence, 3),
        "recommendations": get_recommendations(prediction),
    }
