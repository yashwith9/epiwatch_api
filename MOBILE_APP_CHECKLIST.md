# EpiWatch Mobile App - Quick Start Checklist

## ✅ STEP-BY-STEP IMPLEMENTATION

### □ STEP 1: Install Tools (30 minutes)
- [ ] Download and install Android Studio: https://developer.android.com/studio
- [ ] Install JDK 17 (comes with Android Studio)
- [ ] Install Android SDK (API 33+)

### □ STEP 2: Create Project (10 minutes)
- [ ] Open Android Studio → New Project
- [ ] Select "Empty Activity"
- [ ] Name: EpiWatch
- [ ] Package: com.epiwatch.mobile
- [ ] Language: **Kotlin**
- [ ] Minimum SDK: API 26 (Android 8.0)
- [ ] Click Finish

### □ STEP 3: Add Dependencies (15 minutes)
- [ ] Open `app/build.gradle.kts`
- [ ] Copy dependencies from `MOBILE_APP_GUIDE.md` Step 2.1
- [ ] Click "Sync Now"
- [ ] Wait for Gradle sync to complete

### □ STEP 4: Configure Permissions (5 minutes)
- [ ] Open `AndroidManifest.xml`
- [ ] Add permissions:
  ```xml
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
  ```

### □ STEP 5: Create Data Layer (30 minutes)
Create these files in order:

1. **Data Models** (`data/model/ApiModels.kt`)
   - [ ] Copy from `MOBILE_APP_GUIDE.md` Step 3.1
   - [ ] Contains: MapOutbreak, Alert, DiseaseTrend, etc.

2. **API Service** (`data/api/EpiWatchApiService.kt`)
   - [ ] Copy from Step 3.2
   - [ ] **IMPORTANT:** Change BASE_URL to:
     - Emulator: `http://10.0.2.2:8000/`
     - Real Device: `http://YOUR_PC_IP:8000/`

3. **Retrofit Client** (`data/api/RetrofitClient.kt`)
   - [ ] Copy from Step 3.3

4. **Repository** (`data/repository/EpiWatchRepository.kt`)
   - [ ] Copy from Step 3.4

### □ STEP 6: Create UI Screens (1-2 hours)
Create these files in order:

1. **Dashboard Screen**
   - [ ] `ui/dashboard/DashboardViewModel.kt` (from MOBILE_APP_GUIDE.md)
   - [ ] `ui/dashboard/DashboardScreen.kt` (from MOBILE_APP_GUIDE.md)

2. **Trends Screen**
   - [ ] `ui/trends/TrendsViewModel.kt` (from MOBILE_APP_SCREENS.md)
   - [ ] `ui/trends/TrendsScreen.kt` (from MOBILE_APP_SCREENS.md)

3. **Alerts Screen**
   - [ ] `ui/alerts/AlertsViewModel.kt` (from MOBILE_APP_SCREENS.md)
   - [ ] `ui/alerts/AlertsScreen.kt` (from MOBILE_APP_SCREENS.md)

### □ STEP 7: Set Up Navigation (15 minutes)
- [ ] Create `navigation/NavGraph.kt` (from MOBILE_APP_SCREENS.md)
- [ ] Update `MainActivity.kt` (from MOBILE_APP_SCREENS.md)

### □ STEP 8: Configure Google Maps (15 minutes)
1. [ ] Get API key from Google Cloud Console:
   - Go to https://console.cloud.google.com/
   - Create project "EpiWatch"
   - Enable "Maps SDK for Android"
   - Create credentials → API key
2. [ ] Add to `local.properties`:
   ```
   MAPS_API_KEY=your_api_key_here
   ```
3. [ ] Add to `build.gradle.kts` (app level):
   ```kotlin
   android {
       defaultConfig {
           manifestPlaceholders["MAPS_API_KEY"] = properties["MAPS_API_KEY"] ?: ""
       }
   }
   ```

### □ STEP 9: Test on Emulator (30 minutes)
1. [ ] Make sure your API server is running:
   ```powershell
   cd C:\Users\Bruger\OneDrive\Desktop\NLP\epiwatch\backend
   python main.py
   ```
2. [ ] Create Android Virtual Device (AVD):
   - Tools → Device Manager → Create Device
   - Select: Pixel 6
   - System Image: API 33 (Android 13)
3. [ ] Click Run (green play button)
4. [ ] Wait for app to install and launch
5. [ ] Test all 3 screens:
   - [ ] Dashboard shows map and stats
   - [ ] Trends shows 7-day charts
   - [ ] Alerts shows recent alerts

### □ STEP 10: Test on Real Device (Optional)
1. [ ] Enable Developer Options on your Android phone
2. [ ] Enable USB Debugging
3. [ ] Connect phone via USB
4. [ ] Update BASE_URL to your PC's IP address:
   - Find your IP: `ipconfig` (look for IPv4 Address)
   - Update `EpiWatchApiService.kt`: `http://192.168.1.XXX:8000/`
5. [ ] Select your device in Android Studio
6. [ ] Click Run

---

## 🔥 QUICK TROUBLESHOOTING

### Problem: "Unable to resolve dependency"
**Solution:** 
- File → Invalidate Caches → Invalidate and Restart
- Check internet connection
- Sync Gradle again

### Problem: "Failed to connect to /10.0.2.2:8000"
**Solution:**
- Make sure API server is running: `python backend/main.py`
- Check if server shows "Uvicorn running on http://0.0.0.0:8000"
- For real device, use your PC's actual IP instead of 10.0.2.2

### Problem: "Google Maps not showing"
**Solution:**
- Verify API key is correct in `local.properties`
- Enable "Maps SDK for Android" in Google Cloud Console
- Sync Gradle after adding API key

### Problem: "App crashes on launch"
**Solution:**
- Check Logcat in Android Studio for error messages
- Verify all permissions are in AndroidManifest.xml
- Make sure API server is reachable

---

## 📊 EXPECTED RESULTS

### Dashboard Screen Should Show:
- ✅ 3 stat cards (Total Outbreaks, Active Diseases, Countries)
- ✅ Google Map with outbreak markers
- ✅ Top 4 disease cards
- ✅ Buttons to navigate to Trends and Alerts

### Trends Screen Should Show:
- ✅ List of 4 diseases
- ✅ Bar charts for each disease (7 days)
- ✅ Change percentage badges (↑ or ↓)
- ✅ Severity indicators

### Alerts Screen Should Show:
- ✅ Filter chips (All, Critical, High, Medium, Low)
- ✅ Alert cards with:
  - Disease name
  - City location (e.g., "New York, NY")
  - Context description (e.g., "Rapid spread in schools")
  - Actual vs Expected cases
  - Severity badge

---

## 🎯 ESTIMATED TIME

| Phase | Time | Total |
|-------|------|-------|
| Install tools | 30 min | 30 min |
| Create project | 10 min | 40 min |
| Add dependencies | 15 min | 55 min |
| Data layer | 30 min | 1h 25min |
| UI screens | 1-2 hours | 2h 25min - 3h 25min |
| Navigation | 15 min | 2h 40min - 3h 40min |
| Google Maps | 15 min | 2h 55min - 3h 55min |
| Testing | 30 min | **3h 25min - 4h 25min** |

**Total Time: 3-4 hours** for a fully working app!

---

## 📱 WHAT YOU'LL HAVE

After completing all steps, you'll have:
- ✅ Fully functional Android app
- ✅ 3 screens matching your prototype
- ✅ Real-time data from your API
- ✅ Interactive Google Maps
- ✅ Beautiful Material Design 3 UI
- ✅ Smooth navigation
- ✅ Ready for push notifications (next phase)

---

## 🚀 NEXT ENHANCEMENTS (Optional)

After the basic app works:
1. [ ] Add pull-to-refresh on all screens
2. [ ] Add offline caching with Room database
3. [ ] Set up Firebase Cloud Messaging for push notifications
4. [ ] Add search functionality
5. [ ] Add favorites/bookmarks
6. [ ] Add data export (CSV/PDF)
7. [ ] Add dark mode support
8. [ ] Publish to Google Play Store

---

**Ready to start?** Begin with Step 1! 🎉

**Need help?** Check:
- `MOBILE_APP_GUIDE.md` - Full setup guide
- `MOBILE_APP_SCREENS.md` - Complete screen code
- Android Studio documentation: https://developer.android.com/
