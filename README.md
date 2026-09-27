# PocketSmart AI

PocketSmart AI is a Generative AI assisted budgeting and recommendation web application.

## Features

- User registration
- User login
- Session authentication
- SQLite database
- Home Interior Planner
- Party Budget Planner
- Jewelry & Outfit Planner
- Image upload
- Google Gemini integration
- Demo fallback without an API key
- Recommendation history
- REST APIs
- Swagger API documentation
- Responsive frontend
- Automated tests

---

# Project Structure

```text
pocketsmart_ai/
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── auth.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── schemas.py
│
├── static/
│   ├── app.js
│   └── styles.css
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   ├── jewelry_planner.html
│   ├── history.html
│   └── history_detail.html
│
└── tests/
    └── test_app.py