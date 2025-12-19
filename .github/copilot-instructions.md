# Backend
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py runserver

# Mobile (in new terminal)
cd AstroTamilAssistant
npm install
npm start
npm run android  # or: npm run ios# Backend
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py runserver

# Mobile (in new terminal)
cd AstroTamilAssistant
npm install
npm start
npm run android  # or: npm run ios# AI Copilot Instructions for AstroTamil Customer Care Assistant

## Architecture Overview

**Two-tier architecture:**
- **Backend (Django)**: `backend/` - FAQ management, AI matching, conversation history, human handoff workflow
- **Frontend Mobile (React Native)**: `AstroTamilAssistant/` - Native iOS/Android app with navigation & async storage

**Data flow**: User message → `FAQMatcher.get_response()` → fuzzy match against FAQ database → AI response + metadata → persisted in `Conversation`/`Message` models

## Database Configuration

- **Default**: SQLite (`db.sqlite3`) for local development
- **Production**: PostgreSQL via env vars: `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- **Models**: `chatbot/models.py` (Conversation, Message, HumanHandoffRequest), `faq/models.py` (FAQ with keyword-based search)
- **Note**: FAQ model uses `django.contrib.postgres.ArrayField` for keywords; ensure postgres app is in `INSTALLED_APPS` even for SQLite

## Core AI Matching Algorithm

Located in `backend/chatbot/ai_matcher.py`:
- **Text preprocessing**: lowercase + normalize special characters + remove extra spaces
- **Similarity calculation**: weighted average of token_sort_ratio (0.4), partial_ratio (0.3), token_set_ratio (0.3)
- **Keyword matching**: extract non-stopword tokens >2 chars, score overlap against FAQ keywords
- **Threshold**: `min_similarity_threshold = 0.6` (tunable via FAQMatcher constructor)
- **NLTK dependencies**: punkt + stopwords downloaded on first run; can pre-download via `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`

## REST API Endpoints

- `POST /api/chat/` - send message, get AI response (expects `session_id`, `message`, `language`)
- `POST /api/chat/handoff/` - create human handoff request
- FAQ endpoints at `/api/faq/` (list, filter by category/keywords)

## Critical Developer Workflows

**Backend setup (Windows)**:
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Import FAQs**:
1. Place `astrologer_faqs_complete.json` in `backend/scripts/`
2. Run: `python backend/scripts/import_faqs.py` (from root)
3. Handles both comma-separated & list-format keywords; creates or updates FAQ entries

**React Native setup**:
```powershell
cd AstroTamilAssistant
npm install
npm start  # Starts Metro bundler; then npm run android/ios
```

## Project-Specific Patterns

1. **Session-based conversations**: User identified by `session_id` (client-generated); persistent across app restarts via AsyncStorage
2. **Multi-language support (English/Tamil)**: UI strings in `LANGUAGE_STRINGS` constant; language preference persisted in AsyncStorage; API receives language code per message
3. **Human handoff flow**: If AI confidence <threshold OR user explicitly requests, collect name/phone/issue via HumanHandoffRequest → NotificationService alerts admin → agent contacts customer
4. **CORS config**: `localhost:8081` + Django DEBUG mode for development; use env-based settings for prod
5. **UUID primary keys**: All models use UUID for distributed system readiness; session_id is CharField (client-generated)

## Integration Points

- **Backend-Frontend communication**: JSON REST (DRF serializers in `chatbot/serializers.py` & `faq/serializers.py`)
- **Chat flow**: Message → FAQMatcher.calculate_similarity() → FAQ database lookup → response + confidence score
- **Handoff escalation**: API creates HumanHandoffRequest → NotificationService.send_agent_notification() → email/SMS alerts
- **Session persistence**: AsyncStorage in RN; generates UUID-like session_id on first app launch
- **Language switching**: Dropdown in ChatScreen header → updates AsyncStorage → next message uses new language
- **Admin management**: Django admin at `/admin/` for CRUD on FAQs, conversations, handoff requests; bulk actions for status updates

## Common Gotchas

- FAQ import script assumes cwd is backend/scripts when run (adjust paths for different locations)
- postgres app required in INSTALLED_APPS even for SQLite (no-op but required for ArrayField import)
- NLTK downloads happen at runtime on first chat request; can cause latency spike
- RN `react-native-safe-area-context` required for iOS notch handling; `App.tsx` wraps all UI
- Conversation.last_active updated on every message (good for session expiry detection)

## Testing & Verification

**Backend unit tests** (full coverage):
```powershell
cd backend
python manage.py test chatbot --verbosity=2
```
Tests cover: FAQMatcher algorithm, Chat API, human handoff flow, conversation persistence, model interactions.

**Django admin interface** (access at `/admin/`):
```powershell
python manage.py createsuperuser
python manage.py runserver
# Login with superuser credentials; manage conversations, messages, FAQs, handoff requests
```

**API testing** (Postman/curl): `POST /api/chat/` with `{"session_id": "...", "message": "...", "language": "en"}`

**Mobile testing**: `npm start` from AstroTamilAssistant, then `npm run android` or `npm run ios`

## Notification System

**File**: `backend/chatbot/notifications.py`
- **NotificationService** sends alerts when handoff requests created
- **Email**: Configure `ADMIN_EMAIL`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- **SMS** (optional): Enable with `SMS_NOTIFICATIONS_ENABLED=true`, set `AGENT_PHONE_NUMBER`
- Failures logged; non-blocking (won't break handoff creation if notification fails)
