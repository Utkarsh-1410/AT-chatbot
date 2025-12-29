# AstroTamil Customer Care Assistant - Mobile App

An intelligent AI-powered customer support mobile application for AstroTamil, built with [React Native](https://reactnative.dev). The app provides instant answers to customer queries using a comprehensive FAQ database, with seamless escalation to human agents when needed.

## 🌟 Features

- ✅ **AI-Powered FAQ Matching** - Instant responses using fuzzy matching algorithm
- ✅ **Bilingual Support** - Tamil & English language interface
- ✅ **Conversation History** - Persistent chat sessions stored permanently
- ✅ **Human Handoff** - Smooth escalation to human agents with contact form
- ✅ **Session Management** - Create new chats while preserving old conversations
- ✅ **Offline-First** - AsyncStorage for session persistence
- ✅ **Real-time Updates** - Fast Refresh for seamless development

## 🏗️ Architecture

**Tech Stack:**
- **Frontend**: React Native (TypeScript)
- **Backend**: Django REST API (Python)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **State Management**: React Hooks + AsyncStorage
- **API Client**: Axios

**Communication Flow:**
```
React Native App
    ↓ HTTP/HTTPS
Django REST API
    ↓ ORM
PostgreSQL Database (181 FAQs)
```

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js** 16+ and npm/yarn
- **React Native CLI** installed globally
- **Android Studio** (for Android) or **Xcode** (for iOS)
- **Backend API** running (see `../backend/README.md`)
- **Java JDK** 11+ (for Android builds)

> 💡 Complete setup guide: [React Native Environment Setup](https://reactnative.dev/docs/set-up-your-environment)

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
cd AstroTamilAssistant
npm install

# For iOS (macOS only)
cd ios
pod install
cd ..
```

### Step 2: Configure Backend API

Edit `src/config.ts` to point to your backend:

```typescript
// For development with Android emulator
export const API_BASE_URL = 'http://10.0.2.2:8000/api';

// For iOS simulator
// export const API_BASE_URL = 'http://localhost:8000/api';

// For production
// export const API_BASE_URL = 'https://your-domain.ondigitalocean.app/api';
```

### Step 3: Start Metro Bundler

```bash
npm start
# Metro will start on http://localhost:8081
```

### Step 4: Run on Android

Open a new terminal and run:

```bash
npm run android
```

**Requirements:**
- Android Studio with SDK Platform 33 (Android 13)
- Android emulator running or physical device connected
- USB debugging enabled (for physical devices)

**Troubleshooting Android:**
```bash
# Clean build
cd android
./gradlew clean
cd ..

# Rebuild
npm run android
```

### Step 5: Run on iOS (macOS only)

```bash
npm run ios
```

**Requirements:**
- Xcode 14+ installed
- CocoaPods dependencies installed
- iOS Simulator or physical device

**Troubleshooting iOS:**
```bash
# Clean build
cd ios
xcodebuild clean
pod install --repo-update
cd ..

# Rebuild
npm run ios
```

## 🔧 Development

### Project Structure

```
AstroTamilAssistant/
├── src/
│   ├── screens/
│   │   └── ChatScreen.tsx      # Main chat interface
│   ├── config.ts               # API configuration
│   └── ...
├── android/                    # Android native code
├── ios/                        # iOS native code
├── App.tsx                     # Root component
└── package.json
```

### Key Features Implementation

**1. Chat History Persistence**
- Loads full conversation on app start
- Stored permanently in backend PostgreSQL
- Session ID persisted in AsyncStorage

**2. Language Switching**
- Toggle between English/Tamil
- Preference saved in AsyncStorage
- UI strings defined in `LANGUAGE_STRINGS`

**3. Human Handoff**
- Triggered when AI confidence < 60%
- Modal form collects: name, phone, issue
- Creates ticket in backend database

**4. New Chat Sessions**
- "+" button in header
- Generates new session ID
- Previous chat preserved in database

### Development Commands

```bash
# Start Metro with cache clearing
npm start -- --reset-cache

# Run on specific Android device
npm run android -- --deviceId=<device-id>

# Run iOS on specific simulator
npm run ios -- --simulator="iPhone 15 Pro"

# Check TypeScript errors
npx tsc --noEmit

# Lint code
npm run lint
```

### Hot Reload & Debugging

- **Fast Refresh**: Automatic on file save
- **Dev Menu**: 
  - Android: <kbd>Ctrl</kbd> + <kbd>M</kbd> (or shake device)
  - iOS: <kbd>Cmd ⌘</kbd> + <kbd>D</kbd> (or shake device)
- **Reload App**: Press <kbd>R</kbd> twice
- **Debug JS**: Chrome DevTools or Flipper

## 📱 Building for Production

### Android APK

```bash
cd android

# Generate release APK
./gradlew assembleRelease

# Output: android/app/build/outputs/apk/release/app-release.apk
```

**Before building:**
1. Update `src/config.ts` with production API URL
2. Configure signing keys in `android/app/build.gradle`
3. Update version in `android/app/build.gradle`

### iOS App

```bash
# Open in Xcode
open ios/AstroTamilAssistant.xcworkspace

# Select Generic iOS Device
# Product → Archive
# Follow Xcode's distribution wizard
```

**Before building:**
1. Update API URL in `src/config.ts`
2. Configure signing in Xcode
3. Update version/build number

## 🧪 Testing

### Backend API Connection Test

```bash
# In mobile app, send test message
# Expected flow:
# 1. Message sent to API
# 2. AI matches FAQ
# 3. Response displayed in chat
```

### Human Handoff Test

```bash
# 1. Ask unrelated question (e.g., "What is quantum physics?")
# 2. Verify handoff prompt appears
# 3. Confirm "yes" or tap "Request Human Agent"
# 4. Fill form with test data
# 5. Verify submission success
# 6. Check backend admin for new ticket
```

## 🔍 Troubleshooting

### Common Issues

**1. Metro bundler not starting**
```bash
npm start -- --reset-cache
# or
npx react-native start --reset-cache
```

**2. Android build fails**
```bash
cd android
./gradlew clean
cd ..
npm run android
```

**3. API connection error (Android)**
- Use `10.0.2.2` instead of `localhost`
- Ensure backend is running on port 8000
- Check Android emulator has internet access

**4. iOS build fails**
```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

**5. "Unable to resolve module" error**
```bash
npm install
npm start -- --reset-cache
```

## 📚 Additional Resources

- **Main Documentation**: `../README.md`
- **Backend Setup**: See backend folder
- **Deployment Guide**: `../DIGITAL_OCEAN_DEPLOYMENT.md`
- **AI Instructions**: `../.github/copilot-instructions.md`

## 🆘 Support

- **React Native Docs**: https://reactnative.dev/docs/getting-started
- **Troubleshooting**: https://reactnative.dev/docs/troubleshooting
- **Android Setup**: `../ANDROID_SETUP.md`
- **Backend API**: http://localhost:8000/admin/ (development)

## 📄 License

Proprietary - AstroTamil Platform

---

**Built with ❤️ for AstroTamil customers**
