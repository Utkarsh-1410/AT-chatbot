# AI Copilot Instructions for AstroTamil Customer Care Assistant

## Architecture Overview

**Two-tier architecture:**
- **Backend (Django)**: `backend/` - FAQ management, AI matching, conversation history, human handoff workflow
- **Frontend Mobile (React Native)**: `AstroTamilAssistant/` - Native iOS/Android app with navigation & async storage

**Data flow**: User message → `FAQMatcher.get_response()` → fuzzy match against FAQ database → AI response + metadata → persisted in `Conversation`/`Message` models

## Database Configuration

- **Default**: SQLite (`db.sqlite3`) for local development
- **Production**: PostgreSQL via env vars: `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- **Models**: 
  - `chatbot/models.py`: Conversation (UUID PK, session_id), Message (UUID PK, ForeignKey to Conversation), HumanHandoffRequest (UUID PK, OneToOne with Conversation, status choices: pending/contacted/resolved)
  - `faq/models.py`: FAQ (UUID PK, question, answer, keywords as JSONField, category)
- **Note**: `django.contrib.postgres` app required in INSTALLED_APPS even for SQLite (imports used by models)

## Core AI Matching Algorithm

Located in `backend/chatbot/ai_matcher.py`:
- **Text preprocessing**: lowercase + normalize special characters + remove extra spaces
- **Similarity calculation**: weighted average of token_sort_ratio (0.4), partial_ratio (0.3), token_set_ratio (0.3) using `fuzzywuzzy`
- **Keyword matching**: extract non-stopword tokens >2 chars, score overlap against FAQ keywords
- **Threshold logic**: 
  - ≥70% confidence → direct answer
  - 60-69% confidence → clarification with partial answer
  - <60% → fallback message suggesting human handoff
- **NLTK dependencies**: punkt, punkt_tab, stopwords downloaded on first run; can pre-download via `python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"`
- **FAQ model note**: Uses `JSONField` for keywords array (works with both SQLite and PostgreSQL)

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

1. **Session-based conversations**: User identified by `session_id` (client-generated); persistent across app restarts via AsyncStorage; **all conversations permanently stored in database**
2. **Conversation persistence**: On app start, full conversation history loaded from backend via `/api/conversation-history/`; "New Chat" button creates new session while preserving old ones
3. **Multi-language support (English/Tamil)**: UI strings in `LANGUAGE_STRINGS` constant; language preference persisted in AsyncStorage; API receives language code per message
4. **Human handoff flow**: If AI confidence <threshold OR user explicitly requests, collect name/phone/issue via HumanHandoffRequest → NotificationService alerts admin → agent contacts customer
5. **CORS config**: `localhost:8081` + Django DEBUG mode for development; use env-based settings for prod
6. **UUID primary keys**: All models use UUID for distributed system readiness; session_id is CharField (client-generated) with db_index for fast lookups
7. **Data preservation**: Admin interface prevents accidental deletion (only superusers can delete); messages are immutable once created; `on_delete=CASCADE` ensures referential integrity

## Integration Points

- **Backend-Frontend communication**: JSON REST (DRF serializers in `chatbot/serializers.py` & `faq/serializers.py`)
- **Chat flow**: Message → FAQMatcher.calculate_similarity() → FAQ database lookup → response + confidence score → **both user & AI messages saved to DB**
- **History restoration**: On app launch → fetch `/api/conversation-history/?session_id=X` → populate message list with full conversation history
- **Handoff escalation**: API creates HumanHandoffRequest → NotificationService.send_agent_notification() → email/SMS alerts
- **Session persistence**: AsyncStorage stores session_id in RN; generates UUID-like session_id on first app launch; preserved until user explicitly starts new chat
- **Language switching**: Dropdown in ChatScreen header → updates AsyncStorage → next message uses new language
- **Admin management**: Django admin at `/admin/` for viewing conversations, messages, FAQs, handoff requests; enhanced with duration stats, message counts; deletion restricted to superusers only

## Common Gotchas

- FAQ import script (`backend/scripts/import_faqs.py`) uses relative paths from `backend/scripts/` directory - run from project root with `python backend/scripts/import_faqs.py` or adjust sys.path
- `django.contrib.postgres` required in INSTALLED_APPS even for SQLite (imports used by models, no-op functionality)
- NLTK downloads (punkt, punkt_tab, stopwords) happen at runtime on first chat request; causes latency spike - pre-download recommended
- RN `react-native-safe-area-context` required for iOS notch handling; `App.tsx` wraps all screens
- `Conversation.last_active` auto-updates on every message via `auto_now=True` (useful for session expiry detection)
- Android emulator uses `10.0.2.2:8000` for localhost access (configured in `AstroTamilAssistant/src/config.ts`)
- Auto-generated session_id if client doesn't provide one: `f"auto_{timezone.now().timestamp()}_{id(request)}"`

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
