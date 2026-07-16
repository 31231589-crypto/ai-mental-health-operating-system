# MentalHealthAI

A Flask-based Mental Wellness Monitoring System developed as a final-year B.Sc. Computer Science project. The application helps users monitor their daily mental wellness by combining mood tracking, lifestyle analysis, sentiment analysis, and machine learning-based risk prediction. It provides an easy-to-use interface for recording daily activities, analyzing emotional well-being, visualizing progress through interactive dashboards, and generating professional wellness reports.

## Features

### User Authentication
- Secure user registration and login system
- Password hashing for enhanced security
- User session management
- Logout functionality
- Personal profile management

### Daily Mood Tracking
Users can record their daily wellness information including:
- Current mood
- Sleep duration
- Exercise time
- Water intake
- Screen time
- Stress level
- Personal notes

### Journal Management
- Daily journal writing
- Personal wellness diary
- Automatic sentiment analysis
- Emotional trend monitoring
- Suggested mood detection

### AI-Based Sentiment Analysis
- TextBlob-powered sentiment analysis
- Positive, Neutral, and Negative sentiment detection
- Sentiment confidence score
- Mood suggestion based on journal entries
- Emotional wellness insights

### Machine Learning Prediction
- Random Forest Classifier
- Mental health risk prediction
- Low, Moderate, and High risk classification
- Confidence score generation
- Personalized wellness recommendations

### Interactive Dashboard
- Wellness score calculation
- Stress monitoring
- Mood distribution charts
- Sleep trend visualization
- Weekly analytics
- Latest prediction summary
- Overall mental wellness overview

### Profile Management
- Update personal information
- View mood history
- View journal history
- View prediction history
- Personal wellness records

### PDF Report Generation
Generate downloadable reports containing:
- User information
- Mood history
- Journal sentiment analysis
- Mental health predictions
- Wellness summary
- Recommendation history

---

## Technology Stack

### Backend
- Python
- Flask
- SQLAlchemy
- SQLite

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Machine Learning
- Scikit-learn
- Random Forest Classifier
- Pandas
- NumPy

### Natural Language Processing
- TextBlob

### Visualization
- Chart.js

### Report Generation
- ReportLab (PDF)

### Security
- Werkzeug Password Hashing
- Flask Session Management

---

## Project Structure

```
MentalHealthAI/
│
├── app.py
├── database.py
├── predict.py
├── train_model.py
├── requirements.txt
├── database.db
├── model.pkl
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── mood.html
│   ├── journal.html
│   ├── profile.html
│   └── report.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---

## System Workflow

1. User registers a new account.
2. User logs into the system.
3. Daily wellness information is recorded.
4. Journal entries are analyzed using TextBlob.
5. Lifestyle data is processed by the Random Forest model.
6. Mental health risk prediction is generated.
7. Dashboard displays charts and wellness statistics.
8. Users can monitor progress over time.
9. A detailed PDF report can be generated and downloaded.

---

## Machine Learning Inputs

The prediction model considers the following parameters:

- Age
- Mood
- Sleep Hours
- Exercise Minutes
- Water Intake
- Screen Time
- Stress Level
- Journal Sentiment

---

## Prediction Output

The AI model predicts:

- Mental Wellness Status
- Risk Level
- Confidence Score
- Personalized Recommendations

---

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

### 4. Open the application

```
http://127.0.0.1:5000/
```

---

## Requirements

- Python 3.10 or above
- Flask
- SQLAlchemy
- Scikit-learn
- Pandas
- NumPy
- TextBlob
- ReportLab
- Werkzeug

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## Learning Outcomes

This project demonstrates practical implementation of:

- Flask Web Development
- Database Management with SQLAlchemy
- Machine Learning using Random Forest
- Natural Language Processing
- Sentiment Analysis
- Data Visualization
- User Authentication
- PDF Report Generation
- CRUD Operations
- Session Management
- Responsive Web Design

---

## Future Enhancements

- Deep Learning-based emotion prediction
- Voice emotion analysis
- Mobile application integration
- AI chatbot for mental wellness support
- Email notifications
- Cloud database integration
- Doctor and counselor dashboard
- Multi-language support
- Real-time analytics
- Personalized wellness plans

---

## Disclaimer

This application is developed solely for educational and academic purposes as a final-year B.Sc. Computer Science project. The predictions generated by the system are based on machine learning models and sentiment analysis and should not be considered professional medical advice or a substitute for consultation with qualified mental health professionals.<img width="1920" height="1080" alt="Screenshot 2026-07-15 141724" src="https://github.com/user-attachments/assets/7e0855d3-c2ea-4ec9-bcc7-f204cc160b8d" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141714" src="https://github.com/user-attachments/assets/604f2edb-df53-4b49-8e69-f1da434a1ce2" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141655" src="https://github.com/user-attachments/assets/7e3eafff-2297-4e11-a016-85806880861b" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141639" src="https://github.com/user-attachments/assets/e7146f7a-e20f-400e-9e89-564a03f2938c" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141622" src="https://github.com/user-attachments/assets/18f20b8e-de1e-4b76-aba8-fdf189afcb16" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141610" src="https://github.com/user-attachments/assets/42cfd370-c1c7-4b33-b24f-db903caf05fd" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141509" src="https://github.com/user-attachments/assets/6aef58d5-e664-4958-8f77-9dd2839cdb23" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141459" src="https://github.com/user-attachments/assets/ec7d16d9-df69-43ef-904b-6875b3a761db" />
<img width="1920" height="1080" alt="Screenshot 2026-07-15 141447" src="https://github.com/user-attachments/assets/c6725c64-e469-4c1f-9879-0bd263538e0f" />
