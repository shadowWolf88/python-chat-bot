# Healing Space - Multi-Platform Deployment Plan

**Document Created:** January 25, 2026
**Project:** Healing Space - AI Mental Health Companion
**Current Status:** Web app running on Railway
**Goal:** Deploy to iOS, Android, Desktop while maintaining web app

---

## Executive Summary

This document provides a complete step-by-step guide to deploy Healing Space across:
- **iOS** (iPhone/iPad via App Store)
- **Android** (phones/tablets via Play Store)
- **Desktop** (Windows, macOS, Linux)
- **Web** (keep Railway deployment running)

**Recommended Approach:** Use **Capacitor** for iOS/Android and **Electron** for Desktop. All platforms share the same backend API on Railway - only the frontend wrapper changes.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Phase 1: Prepare Backend for Multi-Platform](#3-phase-1-prepare-backend-for-multi-platform)
4. [Phase 2: iOS App Development](#4-phase-2-ios-app-development)
5. [Phase 3: Android App Development](#5-phase-3-android-app-development)
6. [Phase 4: Desktop App Development](#6-phase-4-desktop-app-development)
7. [Phase 5: PWA Enhancement](#7-phase-5-pwa-enhancement)
8. [Feature Compatibility Matrix](#8-feature-compatibility-matrix)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment & Publishing](#10-deployment--publishing)
11. [Maintenance & Updates](#11-maintenance--updates)
12. [Cost Breakdown](#12-cost-breakdown)
13. [Timeline Overview](#13-timeline-overview)

---

## 1. Architecture Overview

### Current Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     RAILWAY (Cloud)                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Flask API (api.py)  ◄──── GROQ AI API                  ││
│  │  └── SQLite DB (therapist_app.db, pet_game.db)          ││
│  │  └── 65 API endpoints                                   ││
│  └─────────────────────────────────────────────────────────┘│
│                           ▲                                  │
│                           │ HTTPS                            │
│                           │                                  │
└───────────────────────────┼─────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │      Web Browser          │
              │  (templates/index.html)   │
              └───────────────────────────┘
```

### Target Multi-Platform Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     RAILWAY (Cloud)                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Flask API (api.py)  ◄──── GROQ AI API                  ││
│  │  └── SQLite DB (with Railway volume)                    ││
│  │  └── 65 API endpoints                                   ││
│  │  └── Push Notification Service (Firebase/APNs)          ││
│  └─────────────────────────────────────────────────────────┘│
│                           ▲                                  │
│                           │ HTTPS                            │
└───────────────────────────┼─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Web App     │  │  Mobile Apps  │  │  Desktop App  │
│  (Browser)    │  │ (Capacitor)   │  │  (Electron)   │
│               │  │ iOS / Android │  │ Win/Mac/Linux │
└───────────────┘  └───────────────┘  └───────────────┘
```

### Why This Approach?

| Approach | Pros | Cons |
|----------|------|------|
| **Capacitor (Chosen)** | No code rewrite, same web frontend, native features | Requires Node.js setup |
| React Native | Better performance | Complete rewrite needed |
| Flutter | Cross-platform | Complete rewrite needed |
| PWA Only | Simplest | Limited native features, no App Store |

**Decision:** Capacitor + Electron gives us native apps on all platforms with minimal code changes.

---

## 2. Prerequisites

### Required for All Platforms

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | Package management, Capacitor CLI |
| npm | 9+ | Dependency installation |
| Git | Latest | Version control |

**Installation:**
```bash
# Check versions
node --version   # Should be v18+
npm --version    # Should be v9+
git --version

# Install Node.js if needed (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### iOS Development Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| macOS | Ventura 13+ | Required for Xcode |
| Xcode | 15+ | iOS build tools |
| Apple Developer Account | - | App Store publishing ($99/year) |
| CocoaPods | Latest | iOS dependency manager |

**Installation:**
```bash
# Install Xcode from Mac App Store

# Install command line tools
xcode-select --install

# Install CocoaPods
sudo gem install cocoapods
```

### Android Development Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Android Studio | Latest | Build tools, emulator |
| JDK | 17 | Java compilation |
| Android SDK | 33+ | Android platform |

**Installation:**
```bash
# Install JDK 17
sudo apt install openjdk-17-jdk -y

# Download Android Studio from:
# https://developer.android.com/studio

# Set environment variables (~/.bashrc)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Desktop Development Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | Electron runtime |
| Electron | 27+ | Desktop framework |
| electron-builder | Latest | Packaging/distribution |

---

## 3. Phase 1: Prepare Backend for Multi-Platform

### Step 1.1: API Hardening

The current API needs minor adjustments for multi-platform support.

**File:** `api.py`

Add CORS headers for mobile apps:
```python
# Already in place, but verify:
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://www.healing-space.org.uk",
            "https://healing-space.org.uk",
            "capacitor://localhost",      # iOS Capacitor
            "http://localhost",           # Android Capacitor
            "file://"                     # Desktop Electron
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Step 1.2: Push Notification Setup (Firebase)

Create `push_notifications.py`:
```python
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Initialize Firebase (one-time)
cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
if cred_path and os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body, data=None):
    """Send push notification to mobile device."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data or {},
        token=token
    )
    try:
        response = messaging.send(message)
        return {"success": True, "message_id": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_to_topic(topic, title, body):
    """Send notification to all subscribers of a topic."""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        topic=topic
    )
    return messaging.send(message)
```

### Step 1.3: Add Push Token Storage

Add to database schema:
```sql
ALTER TABLE users ADD COLUMN push_token TEXT;
ALTER TABLE users ADD COLUMN device_type TEXT;  -- 'ios', 'android', 'web'
```

Add API endpoint:
```python
@app.route('/api/push/register', methods=['POST'])
def register_push_token():
    data = request.json
    username = data.get('username')
    token = data.get('token')
    device_type = data.get('device_type')

    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET push_token=?, device_type=? WHERE username=?',
        (token, device_type, username)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "registered"})
```

### Step 1.4: Environment Variables for Multi-Platform

Add to Railway environment:
```
# Existing
GROQ_API_KEY=your_groq_key
ENCRYPTION_KEY=your_fernet_key
PIN_SALT=your_salt

# New for mobile
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
APPLE_PUSH_KEY_ID=your_apns_key
APPLE_TEAM_ID=your_team_id
```

---

## 4. Phase 2: iOS App Development

### Step 2.1: Initialize Capacitor Project

```bash
cd "/home/computer001/Documents/Healing Space UK"

# Initialize npm if not done
npm init -y

# Install Capacitor
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios

# Initialize Capacitor
npx cap init "Healing Space" "com.healingspace.app" --web-dir=templates
```

### Step 2.2: Configure Capacitor

Create/edit `capacitor.config.json`:
```json
{
  "appId": "com.healingspace.app",
  "appName": "Healing Space",
  "webDir": "templates",
  "server": {
    "url": "https://www.healing-space.org.uk",
    "cleartext": false
  },
  "ios": {
    "contentInset": "automatic",
    "preferredContentMode": "mobile",
    "scheme": "Healing Space"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#667eea",
      "showSpinner": false
    },
    "PushNotifications": {
      "presentationOptions": ["badge", "sound", "alert"]
    },
    "Keyboard": {
      "resize": "body",
      "style": "dark"
    }
  }
}
```

### Step 2.3: Add iOS Platform

```bash
npx cap add ios
```

This creates an `ios/` folder with a full Xcode project.

### Step 2.4: Install Required Plugins

```bash
# Push notifications
npm install @capacitor/push-notifications
npm install @capacitor/local-notifications

# Biometric auth (Face ID/Touch ID)
npm install @capacitor-community/biometric

# Haptic feedback
npm install @capacitor/haptics

# Status bar styling
npm install @capacitor/status-bar

# App badge
npm install @capacitor/badge

# Sync all plugins
npx cap sync ios
```

### Step 2.5: Configure iOS App

**Edit `ios/App/App/Info.plist`:**
```xml
<!-- Add these keys -->
<key>NSFaceIDUsageDescription</key>
<string>Enable Face ID for secure login</string>

<key>NSCameraUsageDescription</key>
<string>Take photos for your journal entries</string>

<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

### Step 2.6: Create App Icons and Splash Screen

Required assets:
```
ios/App/App/Assets.xcassets/AppIcon.appiconset/
├── Icon-20.png (20x20)
├── Icon-20@2x.png (40x40)
├── Icon-20@3x.png (60x60)
├── Icon-29.png (29x29)
├── Icon-29@2x.png (58x58)
├── Icon-29@3x.png (87x87)
├── Icon-40.png (40x40)
├── Icon-40@2x.png (80x80)
├── Icon-40@3x.png (120x120)
├── Icon-60@2x.png (120x120)
├── Icon-60@3x.png (180x180)
├── Icon-76.png (76x76)
├── Icon-76@2x.png (152x152)
├── Icon-83.5@2x.png (167x167)
└── Icon-1024.png (1024x1024)
```

**Tool:** Use https://appicon.co/ to generate all sizes from one 1024x1024 PNG.

### Step 2.7: Integrate Push Notifications (iOS)

Add to `templates/index.html` (or create `js/push.js`):
```javascript
// iOS Push Notification Setup
import { PushNotifications } from '@capacitor/push-notifications';

async function initPushNotifications() {
    // Check if running in Capacitor
    if (!window.Capacitor) return;

    // Request permission
    const permStatus = await PushNotifications.requestPermissions();

    if (permStatus.receive === 'granted') {
        await PushNotifications.register();
    }

    // Get token
    PushNotifications.addListener('registration', async (token) => {
        console.log('Push token:', token.value);

        // Send token to backend
        await fetch('/api/push/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: localStorage.getItem('username'),
                token: token.value,
                device_type: 'ios'
            })
        });
    });

    // Handle incoming notifications
    PushNotifications.addListener('pushNotificationReceived', (notification) => {
        console.log('Push received:', notification);
        // Show in-app notification
        showNotification(notification.title, notification.body);
    });

    // Handle notification tap
    PushNotifications.addListener('pushNotificationActionPerformed', (notification) => {
        console.log('Push action:', notification);
        // Navigate to relevant screen
        handleNotificationAction(notification.notification.data);
    });
}

// Initialize on app load
document.addEventListener('DOMContentLoaded', initPushNotifications);
```

### Step 2.8: Add Biometric Authentication (iOS)

```javascript
import { BiometricAuth } from '@capacitor-community/biometric';

async function biometricLogin() {
    try {
        // Check if available
        const available = await BiometricAuth.isAvailable();

        if (!available.has) {
            return { success: false, reason: 'not_available' };
        }

        // Authenticate
        const result = await BiometricAuth.authenticate({
            reason: 'Log in to Healing Space',
            title: 'Biometric Login',
            subtitle: 'Use Face ID or Touch ID',
            description: 'Authenticate to access your account'
        });

        if (result.verified) {
            // Get stored credentials and auto-login
            const username = localStorage.getItem('bio_username');
            const token = localStorage.getItem('bio_token');

            if (username && token) {
                return await autoLogin(username, token);
            }
        }

        return { success: false };
    } catch (error) {
        console.error('Biometric error:', error);
        return { success: false, error: error.message };
    }
}
```

### Step 2.9: Build and Test iOS

```bash
# Sync changes
npx cap sync ios

# Open in Xcode
npx cap open ios
```

**In Xcode:**
1. Select your development team (Signing & Capabilities)
2. Select a simulator or connected iPhone
3. Click Run (▶️)

### Step 2.10: Prepare for App Store

1. **Create App Store Connect listing**
   - Go to https://appstoreconnect.apple.com
   - Create new app
   - Bundle ID: `com.healingspace.app`

2. **Required assets:**
   - App icon (1024x1024)
   - Screenshots for each device size
   - App description, keywords
   - Privacy policy URL
   - Support URL

3. **Archive and upload:**
   - In Xcode: Product → Archive
   - Distribute App → App Store Connect
   - Upload

4. **Submit for review**

---

## 5. Phase 3: Android App Development

Refer to existing `ANDROID_APP_GUIDE.md` for detailed steps. Summary:

### Step 3.1: Add Android Platform

```bash
npm install @capacitor/android
npx cap add android
```

### Step 3.2: Install Same Plugins as iOS

```bash
npm install @capacitor/push-notifications
npm install @capacitor-community/biometric
npm install @capacitor/haptics
npx cap sync android
```

### Step 3.3: Configure Android

**Edit `android/app/src/main/AndroidManifest.xml`:**
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.USE_BIOMETRIC" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.VIBRATE" />
```

### Step 3.4: Firebase Setup for Android

1. Create project at https://console.firebase.google.com
2. Add Android app with package: `com.healingspace.app`
3. Download `google-services.json`
4. Place in `android/app/`

**Edit `android/app/build.gradle`:**
```gradle
apply plugin: 'com.google.gms.google-services'

dependencies {
    implementation platform('com.google.firebase:firebase-bom:32.0.0')
    implementation 'com.google.firebase:firebase-messaging'
}
```

### Step 3.5: Build Release APK/AAB

```bash
cd android
./gradlew assembleRelease   # APK
./gradlew bundleRelease     # AAB for Play Store
```

### Step 3.6: Publish to Play Store

1. Create developer account ($25 one-time)
2. Create app listing
3. Upload AAB
4. Fill out content questionnaire
5. Submit for review

---

## 6. Phase 4: Desktop App Development

### Step 6.1: Create Electron Project

```bash
cd "/home/computer001/Documents/Healing Space UK"

# Create desktop directory
mkdir desktop-app
cd desktop-app

# Initialize
npm init -y

# Install Electron
npm install electron --save-dev
npm install electron-builder --save-dev
```

### Step 6.2: Create Main Process

**Create `desktop-app/main.js`:**
```javascript
const { app, BrowserWindow, Menu, Tray, shell, ipcMain } = require('electron');
const path = require('path');

// Configuration
const PRODUCTION_URL = 'https://www.healing-space.org.uk';
const DEV_URL = 'http://localhost:5000';

let mainWindow;
let tray;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        icon: path.join(__dirname, 'assets/icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        titleBarStyle: 'hiddenInset',
        backgroundColor: '#667eea'
    });

    // Load the web app
    const url = app.isPackaged ? PRODUCTION_URL : DEV_URL;
    mainWindow.loadURL(url);

    // Open external links in browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith('http')) {
            shell.openExternal(url);
            return { action: 'deny' };
        }
        return { action: 'allow' };
    });

    // Handle window close
    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
}

function createTray() {
    tray = new Tray(path.join(__dirname, 'assets/tray-icon.png'));

    const contextMenu = Menu.buildFromTemplate([
        { label: 'Open Healing Space', click: () => mainWindow.show() },
        { type: 'separator' },
        { label: 'Quick Mood Log', click: () => openQuickMood() },
        { label: 'Breathing Exercise', click: () => openBreathing() },
        { type: 'separator' },
        {
            label: 'Quit',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('Healing Space');
    tray.setContextMenu(contextMenu);

    tray.on('click', () => mainWindow.show());
}

function createMenu() {
    const template = [
        {
            label: 'File',
            submenu: [
                { role: 'reload' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        },
        {
            label: 'Edit',
            submenu: [
                { role: 'undo' },
                { role: 'redo' },
                { type: 'separator' },
                { role: 'cut' },
                { role: 'copy' },
                { role: 'paste' }
            ]
        },
        {
            label: 'View',
            submenu: [
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { role: 'resetZoom' },
                { type: 'separator' },
                { role: 'togglefullscreen' }
            ]
        },
        {
            label: 'Help',
            submenu: [
                {
                    label: 'Crisis Resources',
                    click: () => shell.openExternal('https://www.samaritans.org/')
                },
                {
                    label: 'About',
                    click: () => showAbout()
                }
            ]
        }
    ];

    if (process.platform === 'darwin') {
        template.unshift({
            label: 'Healing Space',
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' }
            ]
        });
    }

    Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

app.whenReady().then(() => {
    createWindow();
    createTray();
    createMenu();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        } else {
            mainWindow.show();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Desktop notifications
ipcMain.handle('show-notification', (event, { title, body }) => {
    const { Notification } = require('electron');
    new Notification({ title, body }).show();
});
```

### Step 6.3: Create Preload Script

**Create `desktop-app/preload.js`:**
```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    showNotification: (title, body) =>
        ipcRenderer.invoke('show-notification', { title, body }),
    getPlatform: () => process.platform,
    getVersion: () => require('./package.json').version
});
```

### Step 6.4: Configure Package.json

**Edit `desktop-app/package.json`:**
```json
{
  "name": "healing-space",
  "version": "1.0.0",
  "description": "Healing Space - AI Mental Health Companion",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build:win": "electron-builder --win",
    "build:mac": "electron-builder --mac",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder --win --mac --linux"
  },
  "build": {
    "appId": "com.healingspace.desktop",
    "productName": "Healing Space",
    "copyright": "Copyright 2026 Healing Space",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main.js",
      "preload.js",
      "assets/**/*"
    ],
    "win": {
      "target": ["nsis", "portable"],
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": ["dmg", "zip"],
      "icon": "assets/icon.icns",
      "category": "public.app-category.healthcare-fitness"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png",
      "category": "Office"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "installerIcon": "assets/icon.ico"
    }
  },
  "devDependencies": {
    "electron": "^27.0.0",
    "electron-builder": "^24.0.0"
  }
}
```

### Step 6.5: Create Required Assets

```bash
mkdir -p desktop-app/assets
```

Required files:
```
desktop-app/assets/
├── icon.png      (512x512 for Linux)
├── icon.ico      (Windows icon - use https://icoconvert.com/)
├── icon.icns     (macOS icon - use iconutil on Mac)
└── tray-icon.png (16x16 or 32x32)
```

### Step 6.6: Build Desktop Apps

```bash
cd desktop-app

# Development
npm start

# Build for current platform
npm run build:linux   # On Linux
npm run build:mac     # On macOS
npm run build:win     # On Windows (or use Wine)

# Build for all platforms (on macOS)
npm run build:all
```

**Output locations:**
```
desktop-app/dist/
├── Healing Space-1.0.0.AppImage    (Linux)
├── Healing Space-1.0.0.dmg         (macOS)
├── Healing Space Setup 1.0.0.exe   (Windows installer)
└── Healing Space 1.0.0.exe         (Windows portable)
```

### Step 6.7: Desktop-Specific Features

**Auto-start on login:**
```javascript
const { app } = require('electron');

app.setLoginItemSettings({
    openAtLogin: true,
    openAsHidden: true
});
```

**Mood reminder notifications:**
```javascript
const schedule = require('node-schedule');

// Remind at 8 PM daily
schedule.scheduleJob('0 20 * * *', () => {
    new Notification({
        title: 'Healing Space',
        body: "Don't forget to log your mood today!"
    }).show();
});
```

---

## 7. Phase 5: PWA Enhancement

Make the web app installable directly from browsers.

### Step 7.1: Create Web App Manifest

**Create `templates/manifest.json`:**
```json
{
  "name": "Healing Space",
  "short_name": "Healing",
  "description": "AI Mental Health Companion",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/static/icons/icon-72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/icons/icon-384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "screenshots": [
    {
      "src": "/static/screenshots/chat.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide",
      "label": "AI Therapy Chat"
    },
    {
      "src": "/static/screenshots/mood.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide",
      "label": "Mood Tracking"
    }
  ],
  "categories": ["health", "lifestyle", "medical"],
  "shortcuts": [
    {
      "name": "Log Mood",
      "url": "/?action=mood",
      "description": "Quick mood logging",
      "icons": [{ "src": "/static/icons/mood-shortcut.png", "sizes": "96x96" }]
    },
    {
      "name": "Chat",
      "url": "/?action=chat",
      "description": "Start therapy session",
      "icons": [{ "src": "/static/icons/chat-shortcut.png", "sizes": "96x96" }]
    }
  ]
}
```

### Step 7.2: Create Service Worker

**Create `templates/sw.js`:**
```javascript
const CACHE_NAME = 'healing-space-v1';
const OFFLINE_URL = '/offline.html';

const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// Install
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch - Network first, fallback to cache
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache successful responses
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      })
      .catch(() => {
        // Return cached version or offline page
        return caches.match(event.request).then((cached) => {
          return cached || caches.match(OFFLINE_URL);
        });
      })
  );
});

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {};

  event.waitUntil(
    self.registration.showNotification(data.title || 'Healing Space', {
      body: data.body || 'You have a new notification',
      icon: '/static/icons/icon-192.png',
      badge: '/static/icons/badge-72.png',
      data: data.url || '/'
    })
  );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data)
  );
});
```

### Step 7.3: Add to index.html

```html
<!-- In <head> -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#667eea">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Healing Space">
<link rel="apple-touch-icon" href="/static/icons/icon-152.png">

<!-- Before </body> -->
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.error('SW failed:', err));
}
</script>
```

### Step 7.4: Serve Static Files

**Add to `api.py`:**
```python
from flask import send_from_directory

@app.route('/manifest.json')
def manifest():
    return send_from_directory('templates', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('templates', 'sw.js')

@app.route('/static/icons/<path:filename>')
def icons(filename):
    return send_from_directory('static/icons', filename)
```

---

## 8. Feature Compatibility Matrix

| Feature | Web | iOS | Android | Desktop |
|---------|-----|-----|---------|---------|
| AI Therapy Chat | ✅ | ✅ | ✅ | ✅ |
| Mood Logging | ✅ | ✅ | ✅ | ✅ |
| Pet Game | ✅ | ✅ | ✅ | ✅ |
| Clinical Assessments | ✅ | ✅ | ✅ | ✅ |
| Community Posts | ✅ | ✅ | ✅ | ✅ |
| CBT Tools | ✅ | ✅ | ✅ | ✅ |
| Safety Planning | ✅ | ✅ | ✅ | ✅ |
| Clinician Dashboard | ✅ | ✅ | ✅ | ✅ |
| **Push Notifications** | Limited | ✅ | ✅ | ✅ |
| **Biometric Login** | ❌ | ✅ | ✅ | ❌ |
| **Offline Mode** | PWA | ✅ | ✅ | ✅ |
| **System Tray** | ❌ | N/A | N/A | ✅ |
| **App Store** | N/A | ✅ | ✅ | ❌ |

---

## 9. Testing Strategy

### Unit Tests (Backend)
```bash
# Run existing tests
pytest tests/ -v
```

### Mobile Testing

**iOS:**
1. Xcode Simulator (iPhone 14, iPad Pro)
2. Physical device via TestFlight
3. Accessibility testing (VoiceOver)

**Android:**
1. Android Studio emulator (Pixel 5)
2. Physical device via APK sideload
3. TalkBack accessibility testing

### Desktop Testing

| Platform | Test Environment |
|----------|------------------|
| Windows | Windows 10/11 VM |
| macOS | Physical Mac or cloud Mac |
| Linux | Ubuntu 22.04, Fedora 38 |

### Cross-Platform Test Cases

1. **Authentication Flow**
   - Login with username/password
   - 2FA PIN entry
   - Biometric login (mobile)
   - Session persistence

2. **Core Features**
   - AI chat responsiveness
   - Mood logging and sync
   - Pet game interactions
   - Clinical assessments

3. **Notifications**
   - Push notification receipt
   - In-app notification display
   - Badge count updates

4. **Offline Behavior**
   - Graceful degradation
   - Reconnection handling
   - Data sync on reconnect

---

## 10. Deployment & Publishing

### Web (Railway) - Current
- Already deployed at https://www.healing-space.org.uk
- No changes needed
- Automatic deploy on git push

### iOS App Store

**Requirements:**
- Apple Developer Account ($99/year)
- App Store Connect listing
- Privacy policy URL
- App Review compliance

**Steps:**
1. Archive in Xcode
2. Upload to App Store Connect
3. Complete app information
4. Submit for review (1-7 days)

### Google Play Store

**Requirements:**
- Google Play Developer Account ($25 one-time)
- Play Console listing
- Privacy policy URL
- Content rating

**Steps:**
1. Build signed AAB
2. Create Play Console listing
3. Upload to production track
4. Submit for review (1-3 days)

### Desktop Distribution

**Windows:**
- Self-hosted installer download
- Optional: Microsoft Store ($19 one-time)
- Code signing certificate (recommended)

**macOS:**
- Self-hosted DMG download
- Optional: Mac App Store ($99/year via Apple Developer)
- Notarization required for outside App Store

**Linux:**
- Self-hosted AppImage/deb
- Optional: Snapcraft Store (free)
- Optional: Flathub (free)

---

## 11. Maintenance & Updates

### Update Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Backend    │     │   Frontend   │     │ Native Apps  │
│  (api.py)    │     │ (index.html) │     │ (Capacitor)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Push to Git ──────► Railway Deploy      App Store Update
       │                    │              (version bump)
       │                    │                    │
       ▼                    ▼                    ▼
   Instant            Instant              1-7 day review
```

### Backend Updates
- Push to GitHub → Railway auto-deploys
- All clients get updates immediately

### Frontend Updates
- Push to GitHub → Railway auto-deploys
- Web and mobile clients get updates immediately (live URL)
- Desktop app refreshes automatically

### Native App Updates
- Only needed for:
  - New native plugins
  - Icon/splash changes
  - App Store metadata
- Requires new version upload and review

### Version Numbering

```
1.0.0
│ │ │
│ │ └── Patch: Bug fixes
│ └──── Minor: New features
└────── Major: Breaking changes
```

- Web: No version displayed (always latest)
- Mobile: versionCode (Play) / Build Number (iOS)
- Desktop: package.json version

---

## 12. Cost Breakdown

| Item | One-Time | Annual | Notes |
|------|----------|--------|-------|
| **Development** |
| Capacitor | Free | - | MIT license |
| Electron | Free | - | MIT license |
| Node.js | Free | - | Required tools |
| **iOS** |
| Xcode | Free | - | macOS only |
| Apple Developer | - | $99 | Required for App Store |
| TestFlight | Free | - | Beta testing |
| **Android** |
| Android Studio | Free | - | |
| Play Developer | $25 | - | One-time fee |
| **Desktop** |
| electron-builder | Free | - | |
| Code signing (Win) | ~$200 | - | Optional but recommended |
| Notarization (Mac) | - | $99 | Part of Apple Developer |
| **Infrastructure** |
| Railway | - | ~$60 | Current plan |
| Firebase (Push) | Free | - | Up to 1M messages |
| **Total (Minimum)** | **$25** | **$99** | iOS only |
| **Total (All Platforms)** | **$225** | **$159** | All stores + signing |

---

## 13. Timeline Overview

### Phase 1: Backend Preparation (1-2 days)
- [ ] Add CORS for native apps
- [ ] Set up Firebase project
- [ ] Add push notification endpoints
- [ ] Add push token storage

### Phase 2: iOS Development (3-5 days)
- [ ] Initialize Capacitor
- [ ] Configure iOS project
- [ ] Add native plugins
- [ ] Create app icons and splash
- [ ] Test on simulator
- [ ] Test on physical device
- [ ] Submit to App Store

### Phase 3: Android Development (2-3 days)
- [ ] Add Android platform
- [ ] Configure Firebase for Android
- [ ] Create app icons
- [ ] Test on emulator
- [ ] Test on physical device
- [ ] Submit to Play Store

### Phase 4: Desktop Development (2-3 days)
- [ ] Set up Electron project
- [ ] Create main process
- [ ] Add tray functionality
- [ ] Create installers
- [ ] Test on all platforms
- [ ] Create download page

### Phase 5: PWA Enhancement (1 day)
- [ ] Create manifest.json
- [ ] Create service worker
- [ ] Add offline page
- [ ] Test installation

### Phase 6: Testing & Polish (2-3 days)
- [ ] Cross-platform testing
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Documentation updates

**Total Estimated Timeline: 11-17 days**

---

## Quick Start Commands

```bash
# 1. Install dependencies
cd "/home/computer001/Documents/Healing Space UK"
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android

# 2. Initialize Capacitor
npx cap init "Healing Space" "com.healingspace.app" --web-dir=templates

# 3. Add platforms
npx cap add ios
npx cap add android

# 4. Sync and open
npx cap sync
npx cap open ios      # Opens Xcode
npx cap open android  # Opens Android Studio

# 5. Desktop app
mkdir desktop-app && cd desktop-app
npm init -y
npm install electron electron-builder --save-dev
# Create main.js, preload.js, then:
npm start            # Development
npm run build:all    # Build installers
```

---

## Checklist Summary

### Before Starting
- [ ] Node.js 18+ installed
- [ ] Git configured
- [ ] Railway deployment working

### iOS
- [ ] macOS with Xcode installed
- [ ] Apple Developer account active
- [ ] CocoaPods installed
- [ ] App icons created (1024x1024 source)

### Android
- [ ] Android Studio installed
- [ ] JDK 17 installed
- [ ] Firebase project created
- [ ] Play Developer account active

### Desktop
- [ ] Electron project created
- [ ] Icons for all platforms (PNG, ICO, ICNS)
- [ ] Code signing certificates (optional)

### PWA
- [ ] manifest.json created
- [ ] Service worker created
- [ ] Icons in all sizes
- [ ] Offline page created

---

## Support Resources

- **Capacitor Docs:** https://capacitorjs.com/docs
- **Electron Docs:** https://www.electronjs.org/docs
- **Firebase Console:** https://console.firebase.google.com
- **App Store Connect:** https://appstoreconnect.apple.com
- **Play Console:** https://play.google.com/console

---

**Document Version:** 1.0.0
**Last Updated:** January 25, 2026
**Author:** Claude Code Assistant
