# AstroTamil Customer Care Assistant

This repository contains a Django backend scaffold for an AI-driven FAQ/chat assistant for AstroTamil plus a React Native frontend plan.

## Quick start (Windows)

1. Open PowerShell and navigate to the backend folder:

```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\backend
```

2. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create Django project and apps (if you didn't use the scaffold):

```powershell
django-admin startproject astrotamil_api .
python manage.py startapp chatbot
python manage.py startapp faq
```

5. Make migrations and start the server (ensure Postgres is configured or switch to sqlite for local testing):

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

6. Import FAQs (place your `astrologer_faqs_complete.json` into `backend/scripts` and run):

```powershell
python scripts\import_faqs.py
```

Notes
- The scaffold includes `chatbot` and `faq` apps. You may need to adapt `astrotamil_api/settings.py` (SECRET_KEY, DB credentials, ALLOWED_HOSTS) before running in production.
- NLTK data is downloaded on first run by the matcher, but you can pre-download using:

```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

Next steps
- Wire the Django project `manage.py` (if you created the project outside this scaffold) and ensure `astrotamil_api` is the project package name.
- Implement admin registrations, unit tests, and CI as needed.
