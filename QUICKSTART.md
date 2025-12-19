# Quick Start Guide - AstroTamil Customer Care Assistant

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)
- Android Studio or Xcode (for mobile development)

---

## Backend Setup (Django)

### 1. Create Virtual Environment
```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\backend
python -m venv venv
venv\Scripts\Activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Initialize Database
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin User
```powershell
python manage.py createsuperuser
# Follow prompts for username, email, password
```

### 5. Import Sample FAQs (Optional)
```powershell
# Place astrologer_faqs_complete.json in backend/scripts/
python scripts/import_faqs.py
```

### 6. Start Server
```powershell
python manage.py runserver
```
Access:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

---

## Mobile App Setup (React Native)

### 1. Install Dependencies
```powershell
cd ..\AstroTamilAssistant
npm install
```

### 2. Start Metro Bundler
```powershell
npm start
```

### 3. Run on Emulator/Device
```powershell
# Android
npm run android

# iOS (macOS only)
npm run ios
```

---

## First-Time Testing

### Test Backend API
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_user_1",
    "message": "What is astrology?",
    "language": "en"
  }'
```

### Test Admin Interface
1. Navigate to: http://localhost:8000/admin/
2. Login with superuser credentials
3. Create a sample FAQ:
   - Question: "How do I book a consultation?"
   - Answer: "You can book through our website"
   - Keywords: ["booking", "consultation"]
   - Category: "Services"

### Test Mobile Chat
1. Start Android emulator (or iOS simulator)
2. Run `npm run android` from AstroTamilAssistant
3. Type a message and verify it reaches the backend
4. Try language switching (EN ↔ TA)

---

## Environment Configuration

### Backend `.env` (optional, or set in settings.py)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_EMAIL=admin@example.com
```

### Mobile `src/config.ts`
```typescript
// Already configured for Android emulator
export const API_BASE_URL = 'http://10.0.2.2:8000/api';

// For physical device, use:
// export const API_BASE_URL = 'http://YOUR_PC_IP:8000/api';
```

---

## Key Features to Try

### 1. Chat with AI
- Send a message matching FAQ content
- Send a message that doesn't match FAQs (low confidence response)

### 2. Language Switching
- Tap language button (EN/TA) in header
- Chat messages now in selected language

### 3. Human Handoff
- Ask to speak with human agent
- Fill in contact details
- Check admin panel for new handoff request
- Email should be sent to ADMIN_EMAIL (if configured)

### 4. Admin Management
- View all conversations
- Search messages by content
- Update handoff request status (pending → contacted → resolved)
- Add new FAQs directly in admin

---

## Troubleshooting

### Mobile Can't Connect to Backend
**Problem**: `Connection refused` error
**Solution**: 
- Ensure backend is running: `python manage.py runserver`
- For Android emulator, use IP `10.0.2.2` (not `localhost`)
- For physical device, find your PC IP: `ipconfig` and update `src/config.ts`

### NLTK Data Not Found
**Problem**: `Error: NLTK data not found`
**Solution**:
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Module Import Errors
**Problem**: `ModuleNotFoundError`
**Solution**:
```powershell
# Activate venv and reinstall
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
**Problem**: `Address already in use`
**Solution**:
```powershell
# Start on different port
python manage.py runserver 8001
```

---

## Useful Commands

### Django
```powershell
# Run tests
python manage.py test chatbot --verbosity=2

# Create admin user
python manage.py createsuperuser

# Reset database
python manage.py flush

# See database schema
python manage.py sqlmigrate chatbot 0001
```

### React Native
```bash
# Clear cache
npm start -- --reset-cache

# Run tests
npm test

# Lint code
npm run lint
```

---

## Documentation Files

- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Detailed implementation notes
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent guidelines
- **[README.md](README.md)** - Project overview

---

## Next Steps

1. ✅ **Backend Ready**: FAQ matching, API, admin interface, notifications
2. ✅ **Mobile Ready**: Chat UI, language support, session persistence
3. 🔲 **Deploy to Production**: Set up SSL, configure domain, use PostgreSQL
4. 🔲 **Integrate SMS Gateway**: Link Twilio or similar for SMS notifications
5. 🔲 **Analytics**: Add conversation analytics dashboard
6. 🔲 **CI/CD Pipeline**: Set up GitHub Actions for automated testing

---

## Support

For issues or questions:
1. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. Review error logs: `python manage.py runserver` output
3. Check Django admin for data validation

