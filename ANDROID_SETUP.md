# Complete Android Testing Guide - AstroTamil Customer Care Assistant

Follow these steps to deploy and test the project on your Android device.

---

## 📋 Phase 1: Prerequisites & Setup (20-30 minutes)

### Step 1: Install Required Software
1. **Android Studio** - Download from https://developer.android.com/studio
   - During installation, ensure "Android Virtual Device (AVD)" is selected
   - Complete the installation wizard

2. **Node.js** - Download from https://nodejs.org (LTS version)
   - Choose the installer for Windows
   - Run installer and follow prompts

3. **Python 3.8+** - Download from https://www.python.org
   - ✅ Check "Add Python to PATH" during installation
   - Click "Install Now"

4. **Git** - Download from https://git-scm.com/download/win
   - Use default installation settings

### Step 2: Verify Installation
Open PowerShell and run:
```powershell
python --version          # Should show Python 3.x.x
node --version            # Should show v18+
npm --version             # Should show 9+
git --version             # Should show 2.x+
```

---

## 🔧 Phase 2: Backend Setup (15 minutes)

### Step 3: Navigate to Backend Folder
```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\backend
```

### Step 4: Create Python Virtual Environment
```powershell
python -m venv venv
venv\Scripts\Activate
```
✅ Your PowerShell prompt should now show `(venv)` prefix

### Step 5: Install Python Dependencies
```powershell
pip install -r requirements.txt
```
⏳ This may take 2-3 minutes. Dependencies installed:
- Django, DRF, NLTK, fuzzywuzzy, psycopg2, python-dotenv

### Step 6: Initialize Database
```powershell
python manage.py makemigrations
python manage.py migrate
```
✅ Creates SQLite database (`db.sqlite3`) and tables

### Step 7: Create Admin User (Required)
```powershell
python manage.py createsuperuser
```
When prompted, enter:
```
Username: admin
Email: admin@example.com
Password: admin123
Password (again): admin123
```

### Step 8: Start Django Backend Server
```powershell
python manage.py runserver
```

✅ **Success Indicators:**
- Message: `Starting development server at http://127.0.0.1:8000/`
- Terminal shows `[DD/Mon/YYYY HH:MM:SS] "GET /api/ HTTP/1.1" 200`

**Keep this terminal open!** Backend must run while testing mobile app.

---

## 📱 Phase 3: Android Emulator Setup (20 minutes)

### Step 9: Open Android Studio & Create Emulator
1. Open **Android Studio**
2. Click **Tools** → **AVD Manager** (Device Manager in newer versions)
3. Click **Create Virtual Device**
4. Select: **Pixel 4** (or any recent device)
5. Select API: **API 33 (Android 13)** or higher
6. Click **Next** → **Finish**

### Step 10: Start Android Emulator
1. In AVD Manager, click the **Play** ▶️ button next to your device
2. Wait for emulator to fully boot (3-5 minutes)
3. You should see Android home screen

✅ Emulator is ready when you see the lock screen

---

## 📲 Phase 4: Mobile App Setup & Run (20 minutes)

### Step 11: Open New PowerShell Terminal (Keep backend running!)
```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\AstroTamilAssistant
```

### Step 12: Install React Native Dependencies
```powershell
npm install
```
⏳ Takes 3-5 minutes

### Step 13: Verify API Configuration
Edit `src/config.ts` and ensure it has:
```typescript
export const API_BASE_URL = 'http://10.0.2.2:8000/api';
```
✅ `10.0.2.2` is the special IP for Android emulator to reach host machine

### Step 14: Start Metro Bundler (in same terminal)
```powershell
npm start
```
✅ You should see:
```
┌─────────────────────────────────────────────────────────────┐
│  Metro Bundler ready                                        │
│  To reload the app press r                                  │
│  To open developer menu press d                             │
└─────────────────────────────────────────────────────────────┘
```
**Keep this terminal open!**

### Step 15: Build & Deploy to Emulator (in NEW 3rd terminal)
```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\AstroTamilAssistant
npm run android
```
⏳ First build takes 5-10 minutes. Subsequent builds are faster.

✅ **Success Indicators:**
- Gradle build completes with `BUILD SUCCESSFUL`
- App appears on emulator screen
- ChatScreen displays with message input box and language toggle (EN/TA)

---

## 🧪 Phase 5: Testing the Application (15 minutes)

### Test 1: Verify Backend Connection
1. In emulator, tap the message input box
2. Type: `"hello"`
3. Tap **Send**

✅ Expected:
- Message appears in chat with timestamp
- Backend terminal shows HTTP request: `POST /api/chat/ 200`
- Bot responds with a message

❌ If fails:
- Check backend is running (Terminal 1)
- Verify `API_BASE_URL` is `http://10.0.2.2:8000/api`
- Check Android emulator has internet access

### Test 2: Test FAQ Matching
1. Ask an FAQ question: `"What is astrology?"`
2. Send message

✅ Expected:
- Bot responds with confidence score and FAQ answer
- Response appears within 2 seconds

### Test 3: Language Switching
1. Look for language toggle button (EN/TA) at top of screen
2. Tap to switch languages
3. Send a new message: `"Hello"` (or `"नमस्ते"`)

✅ Expected:
- Button now shows **TA** (Tamil)
- All UI text switches to Tamil
- Bot responses in Tamil
- Tap again to switch back to **EN** (English)

### Test 4: Human Handoff Request
1. Type: `"I want to speak to an agent"`
2. Send message
3. App shows human handoff form with fields:
   - Name
   - Email
   - Phone
   - Issue Description

4. Fill in form:
   - Name: `Test User`
   - Email: `test@example.com`
   - Phone: `9876543210`
   - Description: `Need urgent help`

5. Tap **Submit**

✅ Expected:
- Form disappears
- Success message appears
- Backend terminal shows: `POST /api/handoff/ 201`

### Test 5: Verify Admin Panel
1. Open browser on your PC: http://localhost:8000/admin/
2. Login with credentials: `admin` / `admin123`
3. Navigate to **Chatbot** → **Conversations**

✅ Expected:
- See conversation entries from your mobile app tests
- Each conversation shows session_id and message count

4. Click on a conversation to view all messages

### Test 6: Verify Handoff Request in Admin
1. In Admin Panel, go to **Chatbot** → **Human Handoff Requests**
2. Check if your handoff request appears with:
   - Status: "Pending"
   - Your contact info (email, phone)

---

## 🔄 Phase 6: Useful Commands & Tips

### Reload App Without Rebuilding
In Metro Bundler terminal (Terminal 2), press `r` to reload

### Open React Native Debugger
Press `d` in Metro Bundler terminal to open developer menu

### Reset Everything
```powershell
# Stop backend (Terminal 1) - Press Ctrl+C
# Stop Metro (Terminal 2) - Press Ctrl+C
# Close emulator

# Clear caches
npm cache clean --force

# Restart Metro
npm start

# Rebuild app
npm run android
```

### Run on Physical Android Device
1. Enable USB Debugging on device:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable USB Debugging
2. Connect phone to PC via USB cable
3. Run `npm run android` (automatically detects device)

### View Logs from App
```powershell
adb logcat | find "ReactNative"
```

### Import Sample FAQs (Optional)
```powershell
# Terminal 1 (Backend activated)
cd backend
python scripts/import_faqs.py
```

---

## 🆘 Troubleshooting

### Problem: "Module not found" error when building
**Solution:**
```powershell
npm install
npm start --reset-cache
npm run android
```

### Problem: "Cannot connect to backend" (socket timeout)
**Solution:**
1. Verify `config.ts` has: `http://10.0.2.2:8000/api`
2. Emulator settings → Network → Check internet connectivity
3. Restart emulator and backend

### Problem: Gradle build fails with "SDK not found"
**Solution:**
1. Open Android Studio
2. Tools → SDK Manager
3. Install: Android SDK Platform 33+, Build Tools 34.0.0

### Problem: App crashes on startup
**Solution:**
1. Stop Metro (`Ctrl+C`)
2. Stop Android app in emulator
3. Run: `npm run android` again

### Problem: Backend won't start (port 8000 in use)
**Solution:**
```powershell
# Change port
python manage.py runserver 8001

# Update config.ts
export const API_BASE_URL = 'http://10.0.2.2:8001/api';
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────┐
│       Android Emulator / Phone          │
│  ┌───────────────────────────────────┐  │
│  │  React Native Mobile App          │  │
│  │  - ChatScreen Component           │  │
│  │  - Language Toggle (EN/TA)        │  │
│  │  - AsyncStorage (persistence)     │  │
│  └───────────┬───────────────────────┘  │
└──────────────┼───────────────────────────┘
               │
               │ HTTP Requests
               │ 10.0.2.2:8000
               ▼
┌─────────────────────────────────────────┐
│    Your PC / Laptop                     │
│  ┌───────────────────────────────────┐  │
│  │  Django Backend Server            │  │
│  │  - Chat API (/api/chat/)          │  │
│  │  - Handoff API (/api/handoff/)    │  │
│  │  - SQLite Database                │  │
│  │  - FAQMatcher Algorithm           │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌───────────────────────────────────┐  │
│  │  Admin Panel                      │  │
│  │  http://localhost:8000/admin/     │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] Android Studio installed with API 33+ SDK
- [ ] Backend running on http://localhost:8000/
- [ ] Admin user created
- [ ] Android emulator booted
- [ ] Mobile app installed and running on emulator
- [ ] Chat message sent and received
- [ ] Language switching works (EN ↔ TA)
- [ ] Human handoff form submits successfully
- [ ] Admin panel shows conversation and handoff data

---

## 🎉 You're Ready!

Once all checks pass, your AstroTamil application is fully operational. You can now:
- Chat with the AI assistant
- Switch between English and Tamil
- Request human agent assistance
- Manage conversations via admin panel
- Monitor system performance

For more information, see:
- [QUICKSTART.md](QUICKSTART.md)
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- [COMPLETION_REPORT.md](COMPLETION_REPORT.md)
