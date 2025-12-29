# Digital Ocean Deployment Guide
Complete step-by-step guide to deploy AstroTamil Customer Care Assistant on Digital Ocean.

---

## 📋 Prerequisites

- ✅ Digital Ocean Account
- ✅ GitHub Repository Ready
- ✅ Domain Name (optional but recommended)
- ✅ PostgreSQL Database on Digital Ocean

---

## 🚀 Part 1: Database Setup (PostgreSQL)

### 1.1 Create Managed PostgreSQL Database

1. Login to Digital Ocean → **Databases** → **Create Database**
2. Choose:
   - **Engine**: PostgreSQL 15+
   - **Datacenter**: Choose nearest to your users
   - **Plan**: Basic ($15/month minimum)
   - **Database name**: `astrotamil_db`
3. Wait for database to provision (5-10 minutes)

### 1.2 Configure Database Connection

1. Click on your database → **Connection Details**
2. Note down:
   ```
   Host: db-postgresql-nyc3-12345-do-user-xxxx.ondigitalocean.com
   Port: 25060
   User: doadmin
   Password: [your-password]
   Database: astrotamil_db
   SSL Mode: require
   ```

3. Create application database user:
   ```sql
   CREATE USER astrotamil_user WITH PASSWORD 'your_strong_password';
   GRANT ALL PRIVILEGES ON DATABASE astrotamil_db TO astrotamil_user;
   ```

---

## 🖥️ Part 2: Backend (Django) on App Platform

### 2.1 Push Code to GitHub

```bash
# Initialize git if not already done
cd backend
git init
git add .
git commit -m "Initial commit - Django backend"
git branch -M main
git remote add origin https://github.com/Utkarsh-1410/AstroTamilAssistant.git
git push -u origin main
```

### 2.2 Create Django App on Digital Ocean

1. **Apps** → **Create App**
2. **Source**: GitHub → Authorize → Select `AstroTamilAssistant` repo
3. **Resources**:
   - **Type**: Web Service
   - **Source Directory**: `/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn astrotamil_api.wsgi:application --bind 0.0.0.0:$PORT`

### 2.3 Configure Environment Variables

In App Platform → **Settings** → **Environment Variables**, add:

```bash
# Django Core
SECRET_KEY=<generate-using-command-below>
DEBUG=False
ALLOWED_HOSTS=.ondigitalocean.app,yourdomain.com

# Database
POSTGRES_NAME=astrotamil_db
POSTGRES_USER=astrotamil_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=db-postgresql-nyc3-xxxx.ondigitalocean.com
POSTGRES_PORT=25060

# Email Notifications
ADMIN_EMAIL=admin@astrotamil.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=noreply@astrotamil.com
EMAIL_USE_TLS=True

# Optional: SMS Notifications
SMS_NOTIFICATIONS_ENABLED=false
AGENT_PHONE_NUMBER=+919876543210
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.4 Add Required Dependencies

Create `backend/requirements.txt` (if not updated):
```txt
Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
psycopg2-binary>=2.9.5
gunicorn>=21.2.0
nltk>=3.8.1
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
```

### 2.5 Database Migration (One-time Setup)

After first deployment, run console commands:

```bash
# Access App Console in Digital Ocean
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# Import FAQs (if not already done)
python backend/scripts/import_faqs.py
```

---

## 📱 Part 3: React Native Mobile App

### 3.1 Update API Configuration

Edit `AstroTamilAssistant/src/config.ts`:

```typescript
// For production
export const API_BASE_URL = 'https://your-app-name.ondigitalocean.app/api';

// For development (keep for local testing)
// export const API_BASE_URL = 'http://10.0.2.2:8000/api';
```

### 3.2 Build APK for Android

```bash
cd AstroTamilAssistant

# Build release APK
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### 3.3 Build for iOS (macOS required)

```bash
cd AstroTamilAssistant
cd ios
pod install
cd ..

# Build in Xcode or:
npx react-native run-ios --configuration Release
```

---

## 🔧 Part 4: Email Notifications Setup

### Option A: Gmail SMTP (Easiest)

1. **Enable 2-Step Verification** in Google Account
2. **Generate App Password**:
   - Google Account → Security → 2-Step Verification → App passwords
   - Create password for "Mail" → Copy the 16-character password
3. **Use in Environment Variables**:
   ```bash
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
   EMAIL_USE_TLS=True
   ```

### Option B: SendGrid (Professional)

1. Sign up at [SendGrid](https://sendgrid.com/)
2. Create API Key → Full Access
3. **Configure**:
   ```bash
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your_sendgrid_api_key
   ```

### Option C: AWS SES (Scalable)

1. AWS SES → Verify domain/email
2. Create SMTP credentials
3. **Configure**:
   ```bash
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_smtp_username
   EMAIL_HOST_PASSWORD=your_smtp_password
   ```

---

## 🔐 Part 5: Security Best Practices

### 5.1 Update Django Settings for Production

Edit `backend/astrotamil_api/settings.py`:

```python
import os

# Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key-for-dev')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Security headers
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
```

### 5.2 Setup HTTPS

Digital Ocean App Platform provides automatic HTTPS. No extra configuration needed!

### 5.3 Firewall Rules

In Digital Ocean → Networking → Firewalls:
- **Inbound**: HTTP (80), HTTPS (443), PostgreSQL (25060 - only from app)
- **Outbound**: All

---

## 📊 Part 6: Monitoring & Logging

### 6.1 Enable Application Logs

In Digital Ocean App Platform → **Runtime Logs**:
- View real-time logs
- Set up log forwarding (optional)

### 6.2 Setup Health Checks

Add to Django `urls.py`:
```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'astrotamil-api'})

urlpatterns = [
    path('health/', health_check),
    # ... other urls
]
```

Configure in App Platform → **Health Checks**:
- **HTTP Path**: `/health/`
- **Port**: 8080
- **Timeout**: 5s

---

## 🧪 Part 7: Testing Your Deployment

### 7.1 Test Backend API

```bash
# Health check
curl https://your-app.ondigitalocean.app/health/

# Test chat endpoint
curl -X POST https://your-app.ondigitalocean.app/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "message": "How to register?",
    "language": "en"
  }'
```

### 7.2 Test Email Notifications

1. Access Django Admin: `https://your-app.ondigitalocean.app/admin/`
2. Create test handoff request
3. Verify email received at `ADMIN_EMAIL`

### 7.3 Test Mobile App

1. Build release APK
2. Install on Android device
3. Test registration flow
4. Test FAQ queries
5. Test human handoff

---

## 💰 Cost Estimation (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| App Platform (Django) | Basic | $5 |
| PostgreSQL Database | Basic | $15 |
| Spaces (Optional - static files) | 250GB | $5 |
| **Total** | | **$25/month** |

*Prices as of 2025. Check Digital Ocean pricing for updates.*

---

## 🚨 Troubleshooting

### Database Connection Error
```bash
# Check if database is accessible
python manage.py dbshell

# Verify environment variables
echo $POSTGRES_HOST
```

### NLTK Data Missing
```bash
# Run in app console
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

---

## 📞 Support Resources

- **Digital Ocean Docs**: https://docs.digitalocean.com/
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **React Native**: https://reactnative.dev/docs/signed-apk-android

---

## ✅ Deployment Checklist

- [ ] PostgreSQL database created and configured
- [ ] Django app deployed on App Platform
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Superuser created
- [ ] FAQs imported
- [ ] Email notifications configured and tested
- [ ] Mobile app built with production API URL
- [ ] HTTPS working (automatic on DO)
- [ ] Health checks passing
- [ ] Test human handoff flow
- [ ] Monitor logs for errors

---

**🎉 Congratulations! Your AstroTamil Customer Care Assistant is now live!**
