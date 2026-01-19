# Healing Space - Android App Guide

## 📱 Convert Your Web App to a Native Android App

This guide shows you how to turn your Healing Space therapy platform into a native Android app that can be installed on phones and published to the Google Play Store.

---

## Why Capacitor?

- **No code rewrite needed** - Uses your existing HTML/JavaScript
- **Free and open source** - MIT licensed
- **Professional quality** - Used by thousands of apps
- **Access native features** - Camera, notifications, biometrics, etc.
- **Your backend stays on Railway** - App just displays your website

---

## Prerequisites

### 1. Install Node.js & npm
```bash
# Check if already installed
node --version  # Should be v16 or higher
npm --version

# If not installed, download from: https://nodejs.org/
# Or on Ubuntu/Debian:
sudo apt update
sudo apt install nodejs npm -y
```

### 2. Install Android Studio
1. Download: https://developer.android.com/studio
2. Install Android Studio
3. During setup, install:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device (for testing)

### 3. Install Java Development Kit (JDK)
```bash
# Ubuntu/Debian
sudo apt install openjdk-17-jdk -y

# Verify
java -version
```

### 4. Set Environment Variables
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

Then reload:
```bash
source ~/.bashrc
```

---

## Step 1: Create Capacitor Project

### Initialize npm project (if not already done)
```bash
cd "/home/computer001/Documents/python chat bot"

# Create package.json
npm init -y
```

### Install Capacitor
```bash
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android
```

### Initialize Capacitor
```bash
npx cap init
```

You'll be asked:
- **App name**: Healing Space
- **App ID**: com.healingspace.app (or your own domain reversed)
- **Web asset directory**: `templates`

This creates `capacitor.config.json`.

---

## Step 2: Configure Capacitor

Edit `capacitor.config.json`:

```json
{
  "appId": "com.healingspace.app",
  "appName": "Healing Space",
  "webDir": "templates",
  "server": {
    "url": "https://www.healing-space.org.uk",
    "cleartext": true
  },
  "android": {
    "buildOptions": {
      "keystorePath": "release-keystore.jks",
      "keystoreAlias": "healing-space"
    }
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#667eea"
    }
  }
}
```

**Important**: The app will load your Railway website (healing-space.org.uk), not local files. This means:
- ✅ No need to bundle Flask backend
- ✅ Updates to website = updates to app instantly
- ✅ All users always on latest version
- ❌ Requires internet connection (add offline fallback if needed)

---

## Step 3: Add Android Platform

```bash
npx cap add android
```

This creates an `android/` folder with a full Android Studio project.

---

## Step 4: Customize Android App

### App Icon
Replace these files in `android/app/src/main/res/`:
- `mipmap-hdpi/ic_launcher.png` (72x72)
- `mipmap-mdpi/ic_launcher.png` (48x48)
- `mipmap-xhdpi/ic_launcher.png` (96x96)
- `mipmap-xxhdpi/ic_launcher.png` (144x144)
- `mipmap-xxxhdpi/ic_launcher.png` (192x192)

**Tip**: Use https://appicon.co/ to generate all sizes from one image.

### Splash Screen
Replace `android/app/src/main/res/drawable/splash.png` with your logo.

### App Name & Permissions
Edit `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    
    <application
        android:label="Healing Space"
        android:icon="@mipmap/ic_launcher"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">
        
        <!-- Rest of file... -->
    </application>
</manifest>
```

---

## Step 5: Build & Test

### Sync Changes
Every time you modify config:
```bash
npx cap sync
```

### Open in Android Studio
```bash
npx cap open android
```

This launches Android Studio with your project.

### In Android Studio:

1. **Wait for Gradle sync** to complete (bottom status bar)
2. **Create virtual device**:
   - Tools → Device Manager → Create Device
   - Choose: Pixel 5 with Android 13
3. **Run app**:
   - Click green ▶️ button
   - Select your virtual device
   - Wait for build (~5 minutes first time)

### Testing Checklist:
- [ ] App opens and loads website
- [ ] Login works
- [ ] Chat interface responsive
- [ ] Notifications appear
- [ ] Appointment system works
- [ ] All tabs accessible
- [ ] Back button behavior correct

---

## Step 6: Build Release APK

### Create Keystore (one-time)
```bash
cd android/app
keytool -genkey -v -keystore release-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias healing-space
```

You'll be asked for:
- **Password**: Choose strong password (save it!)
- **Name**: Your name
- **Organization**: Healing Space
- **City, State, Country**: Your details

**CRITICAL**: Save the keystore file and password somewhere safe! You need it for all future updates.

### Configure Gradle
Edit `android/app/build.gradle`:

```gradle
android {
    ...
    
    signingConfigs {
        release {
            storeFile file('release-keystore.jks')
            storePassword 'YOUR_KEYSTORE_PASSWORD'
            keyAlias 'healing-space'
            keyPassword 'YOUR_KEY_PASSWORD'
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Build APK
```bash
cd android
./gradlew assembleRelease
```

Your APK will be at:
```
android/app/build/outputs/apk/release/app-release.apk
```

### Install on Physical Device

#### Via USB:
1. Enable Developer Mode on Android phone:
   - Settings → About Phone → Tap "Build Number" 7 times
2. Enable USB Debugging:
   - Settings → Developer Options → USB Debugging ON
3. Connect phone via USB
4. Install:
   ```bash
   adb install android/app/build/outputs/apk/release/app-release.apk
   ```

#### Via File Transfer:
1. Copy `app-release.apk` to phone
2. Open file on phone
3. Allow "Install from Unknown Sources" if prompted
4. Install

---

## Step 7: Publish to Google Play Store (Optional)

### Prerequisites
- Google Play Developer Account ($25 one-time fee)
- App Store listing assets (screenshots, descriptions)
- Privacy Policy URL

### Create App Bundle (AAB)
Google Play requires AAB format, not APK:
```bash
cd android
./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`

### Upload to Play Store

1. **Go to**: https://play.google.com/console
2. **Create app**:
   - App name: Healing Space
   - Default language: English (UK)
   - App or game: App
   - Free or paid: Free
3. **Fill out Store Listing**:
   - Short description (80 chars)
   - Full description (4000 chars)
   - App icon (512x512 PNG)
   - Feature graphic (1024x500)
   - Screenshots (at least 2)
4. **Content Rating**:
   - Answer questionnaire (mental health app)
5. **App Content**:
   - Privacy Policy: Your URL
   - Ads: No (unless you have ads)
   - Target audience: 18+
6. **Upload AAB**:
   - Production → Create new release
   - Upload `app-release.aab`
7. **Submit for Review**

Review takes 1-7 days.

---

## Adding Native Features

### Push Notifications

Install plugin:
```bash
npm install @capacitor/push-notifications
npx cap sync
```

In your JavaScript:
```javascript
import { PushNotifications } from '@capacitor/push-notifications';

await PushNotifications.requestPermissions();
await PushNotifications.register();

PushNotifications.addListener('pushNotificationReceived', (notification) => {
  alert('Push received: ' + notification.title);
});
```

### Camera Access

Install plugin:
```bash
npm install @capacitor/camera
npx cap sync
```

In your JavaScript:
```javascript
import { Camera } from '@capacitor/camera';

const image = await Camera.getPhoto({
  quality: 90,
  allowEditing: true,
  resultType: 'uri'
});
```

### Biometric Authentication

Install plugin:
```bash
npm install @capacitor-community/biometric
npx cap sync
```

Use for login instead of password.

---

## Offline Support (PWA Features)

### Create Service Worker
Create `templates/service-worker.js`:

```javascript
const CACHE_NAME = 'healing-space-v1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/app.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

### Register in index.html:
```html
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js');
}
</script>
```

---

## Troubleshooting

### "SDK location not found"
```bash
# Create local.properties
echo "sdk.dir=$ANDROID_HOME" > android/local.properties
```

### "Gradle build failed"
```bash
cd android
./gradlew clean
./gradlew build --stacktrace
```

### "App won't load website"
- Check `capacitor.config.json` has correct URL
- Ensure phone has internet
- Check Railway is online
- Try: `npx cap sync android`

### "Certificate errors" on HTTPS
Add to `AndroidManifest.xml`:
```xml
android:usesCleartextTraffic="true"
```

### "App crashes on startup"
Check Android Studio Logcat for errors:
- View → Tool Windows → Logcat

### "Changes not showing"
```bash
npx cap copy android
npx cap sync android
```

---

## Maintenance & Updates

### Update App Version

Edit `android/app/build.gradle`:
```gradle
android {
    defaultConfig {
        versionCode 2        // Increment for each release
        versionName "1.1.0"  // User-visible version
    }
}
```

### Push Updates

**Website updates**: Automatic! Users get them instantly.

**App updates** (icon, permissions, native features):
1. Make changes
2. Increment `versionCode`
3. Build new AAB
4. Upload to Play Store
5. Submit for review

---

## Alternative: Progressive Web App (PWA)

If you don't want to build a native app, make it a PWA:

### 1. Create manifest.json:
```json
{
  "name": "Healing Space",
  "short_name": "Healing",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#667eea",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 2. Link in index.html:
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#667eea">
```

### 3. Add service worker (see above)

Users can now "Add to Home Screen" on Android!

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Capacitor framework | Free |
| Android Studio | Free |
| Development tools | Free |
| Testing on your device | Free |
| APK distribution (self-hosted) | Free |
| Google Play Developer Account | $25 one-time |
| App updates | Free forever |
| **TOTAL** | **$0-25** |

---

## Resources

- **Capacitor Docs**: https://capacitorjs.com/docs
- **Android Studio**: https://developer.android.com/studio
- **Play Console**: https://play.google.com/console
- **Icon Generator**: https://appicon.co/
- **Capacitor Community Plugins**: https://github.com/capacitor-community

---

## Support & Help

If you get stuck:
1. Check Capacitor docs
2. Check Android Studio Logcat
3. Search Stack Overflow
4. Ask in Capacitor Discord: https://discord.gg/UPYYRhtyzp

---

## Next Steps

1. ✅ Install prerequisites (Node.js, Android Studio, Java)
2. ✅ Run `npm install @capacitor/core @capacitor/cli @capacitor/android`
3. ✅ Run `npx cap init`
4. ✅ Configure `capacitor.config.json`
5. ✅ Run `npx cap add android`
6. ✅ Run `npx cap open android`
7. ✅ Test in Android Studio emulator
8. ✅ Build release APK
9. ✅ Test on physical device
10. 🎉 Publish to Play Store (optional)

---

**Time estimate**: 4-8 hours for first build (including learning curve)

**Difficulty**: Medium (follow guide step-by-step)

**Result**: Professional native Android app that users can install from Play Store or directly! 📱✨
