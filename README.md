\# 🛰️ AI Landslide Prediction \& Alert System



An advanced AI-powered landslide detection and early warning system built with Django, Machine Learning, and real-time alert infrastructure.



\## Features

\- 🤖 AI/ML landslide risk prediction from satellite imagery

\- 🚨 Public alert system with area-based warnings

\- 🏛️ Government control unit — approve/reject alerts

\- 📱 SMS \& email notifications (Twilio + Gmail)

\- 🗺️ Live warning map with Leaflet.js

\- 🏠 Shelter management with real-time occupancy

\- 📞 Emergency contacts (NDRF, Police, Fire, Medical)

\- 🛡️ Safety instructions in English \& Malayalam

\- ⚡ Celery background tasks with Redis

\- 🛰️ Sentinel-2 satellite image auto-fetch



\## Setup

1\. Clone the repo

2\. Create virtual environment: `python -m venv env`

3\. Install dependencies: `pip install -r requirements.txt`

4\. Copy `.env.example` to `.env` and fill in your keys

5\. Run migrations: `python manage.py migrate`

6\. Load initial data: `python manage.py loaddata alerts/fixtures/initial\_data.json`

7\. Start server: `python manage.py runserver`



\## Tech Stack

Django · Python · SQLite · Redis · Celery · Leaflet.js · Twilio · Sentinel-2

