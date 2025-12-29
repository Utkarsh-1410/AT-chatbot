# AstroTamil Customer Care Assistant

An AI-powered customer support system for AstroTamil, featuring an intelligent FAQ matching engine and bilingual (English/Tamil) chat interface. The system uses Django REST Framework for the backend API and React Native for cross-platform mobile applications.

## Architecture

**Backend (Django)**
- REST API with Django REST Framework
- AI-powered FAQ matching using fuzzy text similarity (fuzzywuzzy + NLTK)
- Conversation history with persistent storage
- Human handoff workflow for complex queries
- Admin interface for managing conversations, FAQs, and handoff requests
- PostgreSQL (production) / SQLite (development)

**Frontend (React Native)**
- Native iOS and Android mobile applications
- Real-time chat interface with conversation history
- Bilingual support (English/Tamil)
- Session-based conversation management
- AsyncStorage for local data persistence

## Key Features

- **181 Pre-loaded FAQs**: Comprehensive knowledge base covering astrology services
- **Smart Matching**: 70% confidence threshold for direct answers, 60-69% for clarification
- **Persistent Chat**: All conversations permanently stored with full history loading
- **Human Handoff**: Seamless escalation to customer service agents
- **Multi-language**: Native support for English and Tamil
- **Session Management**: Multiple conversation threads with "New Chat" functionality
- **Production Ready**: Deployment guides for Digital Ocean, email notifications

## Quick Start

### Backend Setup (Windows)

1. Navigate to the backend folder:
```powershell
cd backend
```

2. Create and activate virtual environment:
```powershell
python -m venv venv
venv\Scripts\Activate
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Configure environment variables (copy `.env.example` to `.env` and update):
```powershell
cp .env.example .env
```

5. Run database migrations:
```powershell
python manage.py migrate
```

6. Import FAQ data:
```powershell
python scripts\import_faqs.py
```

7. Create superuser for admin access:
```powershell
python manage.py createsuperuser
```

8. Start the development server:
```powershell
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Mobile App Setup

1. Navigate to the mobile app folder:
```powershell
cd AstroTamilAssistant
```

2. Install dependencies:
```powershell
npm install
```

3. Start Metro bundler:
```powershell
npm start
```

4. Run on Android:
```powershell
npm run android
```

5. Run on iOS (macOS only):
```powershell
npm run ios
```

## Testing

**Backend Unit Tests**
```powershell
cd backend
python manage.py test chatbot --verbosity=2
```

**Mobile Tests**
```powershell
cd AstroTamilAssistant
npm test
```

## Deployment

See `DIGITAL_OCEAN_DEPLOYMENT.md` for comprehensive production deployment instructions including:
- PostgreSQL managed database setup
- App Platform configuration
- Email notification setup (Gmail/SendGrid/AWS SES)
- Environment variable management
- SSL/TLS configuration
- Cost estimates (approximately $25/month)

## API Endpoints

- `POST /api/chat/` - Send message, receive AI response
- `POST /api/chat/handoff/` - Request human assistance
- `GET /api/conversation-history/` - Retrieve conversation history
- `GET /api/faq/` - List FAQs (with category/keyword filters)

## Project Structure

```
astrotamil-customer-care/
├── backend/                    # Django REST API
│   ├── astrotamil_api/        # Project settings
│   ├── chatbot/               # Chat logic, AI matcher, models
│   ├── faq/                   # FAQ management
│   ├── scripts/               # Data import utilities
│   └── requirements.txt       # Python dependencies
├── AstroTamilAssistant/       # React Native mobile app
│   ├── src/
│   │   ├── screens/           # Chat interface
│   │   └── config.ts          # API configuration
│   ├── android/               # Android build files
│   └── ios/                   # iOS build files
└── .github/
    └── copilot-instructions.md # AI coding assistant guidance
```

## Requirements

**Backend**
- Python 3.8+
- PostgreSQL 12+ (production) or SQLite (development)
- Django 4.2+
- NLTK with punkt and stopwords data

**Mobile**
- Node.js 20+
- React Native 0.83
- Android Studio (for Android development)
- Xcode 13+ (for iOS development, macOS only)

## Configuration

**Backend Environment Variables** (see `.env.example`):
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `POSTGRES_*` - Database credentials
- `EMAIL_*` - Email notification settings
- `CORS_ALLOWED_ORIGINS` - Frontend URLs

**Mobile Configuration** (`src/config.ts`):
- `API_BASE_URL` - Backend API endpoint
- Android emulator uses `10.0.2.2:8000` for localhost

## Admin Interface

Access Django admin at `/admin/` with superuser credentials:
- View all conversations with duration statistics
- Manage FAQ entries with category filtering
- Monitor human handoff requests
- Track message counts and timestamps

## License

Proprietary - AstroTamil Customer Care System

## Support

For technical issues or questions, refer to:
- Backend documentation in `backend/README.md`
- Mobile app documentation in `AstroTamilAssistant/README.md`
- Deployment guide in `DIGITAL_OCEAN_DEPLOYMENT.md`
