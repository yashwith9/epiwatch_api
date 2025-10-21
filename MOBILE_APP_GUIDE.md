# EpiWatch Mobile App - Development Roadmap

## 🎯 PROJECT OVERVIEW
Build an Android mobile application for real-time disease outbreak monitoring using the EpiWatch API.

---

## 📱 PHASE 1: PROJECT SETUP (Day 1)

### Step 1.1: Install Required Tools
- [ ] Install Android Studio (latest version)
  - Download from: https://developer.android.com/studio
  - Choose "Android Studio Hedgehog" or later
  
- [ ] Install Java Development Kit (JDK 17)
  - Required for Kotlin/Android development
  
- [ ] Set up Android SDK
  - Target API: Android 13 (API level 33) or higher
  - Min API: Android 8.0 (API level 26)

### Step 1.2: Create New Android Project
```
1. Open Android Studio
2. Click "New Project"
3. Select "Empty Activity" template
4. Configure project:
   - Name: EpiWatch
   - Package: com.epiwatch.mobile
   - Language: Kotlin
   - Minimum SDK: API 26 (Android 8.0)
   - Build configuration: Kotlin DSL (build.gradle.kts)
5. Click "Finish"
```

### Step 1.3: Project Structure
```
EpiWatch/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/epiwatch/mobile/
│   │   │   │   ├── ui/
│   │   │   │   │   ├── dashboard/      # Dashboard screen
│   │   │   │   │   ├── trends/         # 7-Day Trends screen
│   │   │   │   │   ├── alerts/         # Recent Alerts screen
│   │   │   │   │   └── theme/          # App theme/styling
│   │   │   │   ├── data/
│   │   │   │   │   ├── model/          # Data models
│   │   │   │   │   ├── repository/     # Data repositories
│   │   │   │   │   └── api/            # API service
│   │   │   │   └── util/               # Utilities
│   │   │   ├── res/
│   │   │   │   ├── layout/             # XML layouts
│   │   │   │   ├── drawable/           # Icons, images
│   │   │   │   └── values/             # Colors, strings
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   └── build.gradle.kts
└── build.gradle.kts
```

---

## 🔧 PHASE 2: DEPENDENCIES & CONFIGURATION (Day 1)

### Step 2.1: Add Dependencies to build.gradle.kts (app level)

```kotlin
dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    
    // Jetpack Compose (Modern UI)
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")
    
    // Networking - Retrofit & OkHttp
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    
    // Coroutines (Async operations)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // ViewModel & LiveData
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")
    
    // Google Maps
    implementation("com.google.maps.android:maps-compose:4.3.0")
    implementation("com.google.android.gms:play-services-maps:18.2.0")
    
    // Charts (for 7-day trends)
    implementation("com.patrykandpatrick.vico:compose:1.13.1")
    implementation("com.patrykandpatrick.vico:compose-m3:1.13.1")
    
    // Firebase (Push notifications)
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-messaging-ktx")
    implementation("com.google.firebase:firebase-analytics-ktx")
    
    // Coil (Image loading)
    implementation("io.coil-kt:coil-compose:2.5.0")
    
    // Testing
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
```

### Step 2.2: Configure AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:name=".EpiWatchApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.EpiWatch"
        android:usesCleartextTraffic="true">  <!-- For localhost API during dev -->
        
        <!-- Google Maps API Key -->
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="${MAPS_API_KEY}" />
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.EpiWatch">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

## 💾 PHASE 3: DATA LAYER - API INTEGRATION (Day 2)

### Step 3.1: Create Data Models

**File: `data/model/ApiModels.kt`**

```kotlin
package com.epiwatch.mobile.data.model

import com.google.gson.annotations.SerializedName

// Map Outbreak
data class MapOutbreak(
    val id: String,
    val disease: String,
    val country: String,
    val iso3: String,
    val latitude: Double,
    val longitude: Double,
    @SerializedName("outbreak_count") val outbreakCount: Int,
    @SerializedName("risk_level") val riskLevel: String,
    val year: Int
)

// Alert
data class Alert(
    val id: String,
    val timestamp: String,
    val disease: String,
    val location: String,
    @SerializedName("city_location") val cityLocation: String?,
    @SerializedName("context_description") val contextDescription: String?,
    val date: String,
    @SerializedName("actual_count") val actualCount: Int,
    @SerializedName("expected_count") val expectedCount: Double,
    val deviation: Double,
    @SerializedName("deviation_pct") val deviationPct: Double,
    val severity: Double,
    @SerializedName("severity_level") val severityLevel: String,
    @SerializedName("anomaly_type") val anomalyType: String,
    @SerializedName("z_score") val zScore: Double,
    val message: String
)

// Trend Point
data class TrendPoint(
    val date: String,
    val count: Int
)

// Disease Trend
data class DiseaseTrend(
    val disease: String,
    @SerializedName("total_count") val totalCount: Int,
    @SerializedName("trend_data") val trendData: List<TrendPoint>,
    @SerializedName("change_pct") val changePct: Double,
    @SerializedName("trend_direction") val trendDirection: String,
    val severity: String?,
    val description: String?
)

// Disease Statistic
data class DiseaseStatistic(
    val disease: String,
    @SerializedName("current_count") val currentCount: Int,
    @SerializedName("change_pct") val changePct: Double,
    val trend: String
)

// Dashboard Stats
data class DashboardStats(
    @SerializedName("total_outbreaks") val totalOutbreaks: Int,
    @SerializedName("active_diseases") val activeDiseases: Int,
    @SerializedName("affected_countries") val affectedCountries: Int,
    @SerializedName("last_updated") val lastUpdated: String,
    @SerializedName("top_diseases") val topDiseases: List<DiseaseStatistic>
)

// Health Check
data class HealthCheck(
    val status: String,
    val timestamp: String,
    val service: String,
    val version: String
)
```

### Step 3.2: Create API Service

**File: `data/api/EpiWatchApiService.kt`**

```kotlin
package com.epiwatch.mobile.data.api

import com.epiwatch.mobile.data.model.*
import retrofit2.http.*

interface EpiWatchApiService {
    
    @GET("api/v1/health")
    suspend fun getHealth(): HealthCheck
    
    @GET("api/v1/statistics")
    suspend fun getStatistics(): DashboardStats
    
    @GET("api/v1/map")
    suspend fun getMapData(
        @Query("year") year: Int? = null,
        @Query("disease") disease: String? = null
    ): List<MapOutbreak>
    
    @GET("api/v1/trends")
    suspend fun getTrends(
        @Query("diseases") diseases: String? = null
    ): List<DiseaseTrend>
    
    @GET("api/v1/alerts")
    suspend fun getAlerts(
        @Query("limit") limit: Int = 20,
        @Query("severity") severity: String? = null,
        @Query("disease") disease: String? = null
    ): List<Alert>
    
    @GET("api/v1/diseases")
    suspend fun getDiseases(): List<String>
    
    companion object {
        // Change this to your computer's IP address when testing on real device
        // For emulator: use 10.0.2.2
        // For real device: use your computer's local IP (e.g., 192.168.1.100)
        const val BASE_URL = "http://10.0.2.2:8000/"  // For emulator
        // const val BASE_URL = "http://192.168.1.100:8000/"  // For real device
    }
}
```

### Step 3.3: Create Retrofit Client

**File: `data/api/RetrofitClient.kt`**

```kotlin
package com.epiwatch.mobile.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(EpiWatchApiService.BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    val apiService: EpiWatchApiService = retrofit.create(EpiWatchApiService::class.java)
}
```

### Step 3.4: Create Repository

**File: `data/repository/EpiWatchRepository.kt`**

```kotlin
package com.epiwatch.mobile.data.repository

import com.epiwatch.mobile.data.api.RetrofitClient
import com.epiwatch.mobile.data.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class EpiWatchRepository {
    
    private val api = RetrofitClient.apiService
    
    suspend fun getHealth(): Result<HealthCheck> = withContext(Dispatchers.IO) {
        try {
            Result.success(api.getHealth())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getStatistics(): Result<DashboardStats> = withContext(Dispatchers.IO) {
        try {
            Result.success(api.getStatistics())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getMapData(year: Int? = null, disease: String? = null): Result<List<MapOutbreak>> = 
        withContext(Dispatchers.IO) {
            try {
                Result.success(api.getMapData(year, disease))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    
    suspend fun getTrends(diseases: String? = null): Result<List<DiseaseTrend>> = 
        withContext(Dispatchers.IO) {
            try {
                Result.success(api.getTrends(diseases))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    
    suspend fun getAlerts(
        limit: Int = 20,
        severity: String? = null,
        disease: String? = null
    ): Result<List<Alert>> = withContext(Dispatchers.IO) {
        try {
            Result.success(api.getAlerts(limit, severity, disease))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

## 🎨 PHASE 4: UI LAYER - SCREENS (Days 3-5)

### Step 4.1: Dashboard Screen ViewModel

**File: `ui/dashboard/DashboardViewModel.kt`**

```kotlin
package com.epiwatch.mobile.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.epiwatch.mobile.data.model.DashboardStats
import com.epiwatch.mobile.data.model.MapOutbreak
import com.epiwatch.mobile.data.repository.EpiWatchRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class DashboardUiState(
    val isLoading: Boolean = false,
    val stats: DashboardStats? = null,
    val mapData: List<MapOutbreak> = emptyList(),
    val error: String? = null
)

class DashboardViewModel(
    private val repository: EpiWatchRepository = EpiWatchRepository()
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(DashboardUiState(isLoading = true))
    val uiState: StateFlow<DashboardUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = DashboardUiState(isLoading = true)
            
            // Load statistics
            val statsResult = repository.getStatistics()
            val mapResult = repository.getMapData()
            
            _uiState.value = DashboardUiState(
                isLoading = false,
                stats = statsResult.getOrNull(),
                mapData = mapResult.getOrElse { emptyList() },
                error = statsResult.exceptionOrNull()?.message
            )
        }
    }
}
```

### Step 4.2: Dashboard Screen UI

**File: `ui/dashboard/DashboardScreen.kt`**

```kotlin
package com.epiwatch.mobile.ui.dashboard

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = viewModel(),
    onNavigateToTrends: () -> Unit = {},
    onNavigateToAlerts: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("EpiWatch Dashboard") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Statistics Cards
                item {
                    StatsCards(stats = uiState.stats)
                }
                
                // Map
                item {
                    OutbreakMap(outbreaks = uiState.mapData)
                }
                
                // Disease Cards
                item {
                    uiState.stats?.topDiseases?.let { diseases ->
                        DiseaseCards(diseases = diseases)
                    }
                }
                
                // Action Buttons
                item {
                    ActionButtons(
                        onViewTrends = onNavigateToTrends,
                        onViewAlerts = onNavigateToAlerts
                    )
                }
            }
        }
    }
}

@Composable
fun StatsCards(stats: com.epiwatch.mobile.data.model.DashboardStats?) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Total Outbreaks",
            value = stats?.totalOutbreaks?.toString() ?: "0",
            icon = Icons.Default.Warning,
            color = MaterialTheme.colorScheme.errorContainer
        )
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Active Diseases",
            value = stats?.activeDiseases?.toString() ?: "0",
            icon = Icons.Default.LocalHospital,
            color = MaterialTheme.colorScheme.primaryContainer
        )
        StatCard(
            modifier = Modifier.weight(1f),
            title = "Countries",
            value = stats?.affectedCountries?.toString() ?: "0",
            icon = Icons.Default.Public,
            color = MaterialTheme.colorScheme.tertiaryContainer
        )
    }
}

@Composable
fun StatCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = color)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(icon, contentDescription = null)
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                text = title,
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}

@Composable
fun OutbreakMap(outbreaks: List<com.epiwatch.mobile.data.model.MapOutbreak>) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
            .padding(horizontal = 16.dp)
    ) {
        val cameraPositionState = rememberCameraPositionState {
            position = CameraPosition.fromLatLngZoom(LatLng(20.0, 0.0), 2f)
        }
        
        GoogleMap(
            modifier = Modifier.fillMaxSize(),
            cameraPositionState = cameraPositionState
        ) {
            outbreaks.forEach { outbreak ->
                Marker(
                    state = MarkerState(position = LatLng(outbreak.latitude, outbreak.longitude)),
                    title = outbreak.disease,
                    snippet = "${outbreak.country}: ${outbreak.outbreakCount} cases"
                )
            }
        }
    }
}

// Continue in next message...
```

---

## 📱 MORE SCREENS & FINAL STEPS

I'll create the complete implementation files for you. Would you like me to continue with:

1. **Trends Screen** (7-day bar charts)
2. **Alerts Screen** (recent alerts list)
3. **Navigation setup**
4. **Theme & styling**
5. **Push notifications setup**
6. **Testing & deployment**

**Quick Answer:** The main steps are:
1. ✅ Set up Android Studio project
2. ✅ Add dependencies (Retrofit, Compose, Maps, Charts)
3. ✅ Create data models matching your API
4. ✅ Build API service with Retrofit
5. → Build 3 screens (Dashboard, Trends, Alerts)
6. → Add navigation
7. → Style with Material Design 3
8. → Add push notifications
9. → Test & deploy

Should I create all the remaining screen files for you?
