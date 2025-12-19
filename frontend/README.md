# AstroTamil Assistant (Frontend)

This folder contains a React Native app scaffold for the AstroTamil customer care assistant.

Quick start (Windows, emulator)

1. From PowerShell, go to the frontend folder:

```powershell
cd c:\ai-customer-care-assistant\astrotamil-customer-care\frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Start Metro and run on Android emulator (use Android Studio AVD or a connected device):

```powershell
npx react-native start
npx react-native run-android
```

Notes
- When testing on the Android emulator, use `http://10.0.2.2:8000/api` to reach a backend running on your host machine.
- If using a real device, replace `API_BASE_URL` with your PC's LAN IP and ensure the device and PC are on the same network.
- This scaffold includes `src/screens/ChatScreen.tsx` and a minimal `App.tsx`. You still need to finish project setup: Android SDK, emulator, and native dependencies for some React Native libraries (vector icons, reanimated). Follow React Native docs for full environment setup.
 - When testing on the Android emulator, use `http://10.0.2.2:8000/api` to reach a backend running on your host machine.
 - If using a real device, replace `API_BASE_URL` in `src/config.ts` with your PC's LAN IP (for example `http://192.168.1.42:8000/api`) and ensure the device and PC are on the same network.
 - This scaffold includes `src/screens/ChatScreen.tsx`, `src/config.ts`, and a minimal `App.tsx`. To install into the RN project created with the CLI, copy the files from this `frontend/src` directory into your RN project `AstroTamilAssistant/src` (or replace the project's `App.tsx`).
 - Android cleartext: for local testing over HTTP, edit `android/app/src/main/AndroidManifest.xml` in your RN project and add `android:usesCleartextTraffic="true"` to the `<application>` element.
 - To build and run on a connected Android device (USB debugging enabled):

```powershell
cd C:\path\to\AstroTamilAssistant
npm install
npx react-native start
# in another terminal
npx react-native run-android
```

 - If you prefer to build an APK manually:

```powershell
cd C:\path\to\AstroTamilAssistant\android
.\gradlew assembleDebug
adb install -r app\build\outputs\apk\debug\app-debug.apk
```
