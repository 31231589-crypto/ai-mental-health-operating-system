import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATASET_PATH = Path(__file__).with_name("dataset.csv")
MODEL_PATH = Path(__file__).with_name("model.pkl")

MOOD_MAP = {
    "Happy": 0,
    "Calm": 1,
    "Neutral": 2,
    "Sad": 3,
    "Angry": 4,
    "Anxious": 5,
}

SENTIMENT_MAP = {
    "Positive": 0,
    "Neutral": 1,
    "Negative": 2,
}


def train_model(dataset_path: str | None = None, model_path: str | None = None):
    dataset_path = Path(dataset_path or DATASET_PATH)
    model_path = Path(model_path or MODEL_PATH)

    data = pd.read_csv(dataset_path)
    data["Mood"] = data["Mood"].map(MOOD_MAP)
    data["Sentiment"] = data["Sentiment"].map(SENTIMENT_MAP)

    features = ["Age", "Sleep_Hours", "Exercise_Minutes", "Water_Intake", "Screen_Time", "Mood", "Stress_Level", "Sentiment"]
    X = data[features]
    y = data["Mental_Health_Status"]

    model = RandomForestClassifier(n_estimators=120, random_state=42)
    model.fit(X, y)

    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)

    payload = {
        "model": model,
        "feature_columns": features,
        "accuracy": float(accuracy),
    }
    joblib.dump(payload, model_path)
    return payload


def ensure_model_exists():
    if not MODEL_PATH.exists():
        return train_model()
    return joblib.load(MODEL_PATH)


if __name__ == "__main__":
    result = train_model()
    print(f"Model trained with accuracy: {result['accuracy']:.2f}")
