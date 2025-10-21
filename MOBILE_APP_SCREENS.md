# EpiWatch Mobile App - Complete Screen Implementations

## 📊 TRENDS SCREEN (7-Day Bar Charts)

### File: `ui/trends/TrendsViewModel.kt`

```kotlin
package com.epiwatch.mobile.ui.trends

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.epiwatch.mobile.data.model.DiseaseTrend
import com.epiwatch.mobile.data.repository.EpiWatchRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class TrendsUiState(
    val isLoading: Boolean = false,
    val trends: List<DiseaseTrend> = emptyList(),
    val selectedDisease: String? = null,
    val error: String? = null
)

class TrendsViewModel(
    private val repository: EpiWatchRepository = EpiWatchRepository()
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(TrendsUiState(isLoading = true))
    val uiState: StateFlow<TrendsUiState> = _uiState.asStateFlow()
    
    init {
        loadTrends()
    }
    
    fun loadTrends(diseases: String? = null) {
        viewModelScope.launch {
            _uiState.value = TrendsUiState(isLoading = true)
            
            val result = repository.getTrends(diseases)
            
            _uiState.value = TrendsUiState(
                isLoading = false,
                trends = result.getOrElse { emptyList() },
                error = result.exceptionOrNull()?.message
            )
        }
    }
    
    fun selectDisease(disease: String) {
        _uiState.value = _uiState.value.copy(selectedDisease = disease)
    }
}
```

### File: `ui/trends/TrendsScreen.kt`

```kotlin
package com.epiwatch.mobile.ui.trends

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.patrykandpatrick.vico.compose.axis.horizontal.rememberBottomAxis
import com.patrykandpatrick.vico.compose.axis.vertical.rememberStartAxis
import com.patrykandpatrick.vico.compose.chart.Chart
import com.patrykandpatrick.vico.compose.chart.column.columnChart
import com.patrykandpatrick.vico.compose.m3.style.m3ChartStyle
import com.patrykandpatrick.vico.compose.style.ProvideChartStyle
import com.patrykandpatrick.vico.core.entry.entryModelOf

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrendsScreen(
    viewModel: TrendsViewModel = viewModel(),
    onNavigateBack: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("7-Day Trends") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
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
                verticalArrangement = Arrangement.spacedBy(16.dp),
                contentPadding = PaddingValues(16.dp)
            ) {
                items(uiState.trends) { trend ->
                    TrendCard(trend = trend)
                }
            }
        }
    }
}

@Composable
fun TrendCard(trend: com.epiwatch.mobile.data.model.DiseaseTrend) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = trend.disease,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Total: ${trend.totalCount} cases",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                TrendBadge(
                    direction = trend.trendDirection,
                    changePct = trend.changePct
                )
            }
            
            // Description (if available)
            trend.description?.let { description ->
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Chart
            TrendChart(trendData = trend.trendData)
            
            // Severity badge (if available)
            trend.severity?.let { severity ->
                SeverityChip(severity = severity)
            }
        }
    }
}

@Composable
fun TrendBadge(direction: String, changePct: Double) {
    val (icon, color, text) = when (direction) {
        "up" -> Triple(
            Icons.Default.TrendingUp,
            MaterialTheme.colorScheme.error,
            "+${changePct}%"
        )
        "down" -> Triple(
            Icons.Default.TrendingDown,
            MaterialTheme.colorScheme.tertiary,
            "${changePct}%"
        )
        else -> Triple(
            Icons.Default.TrendingFlat,
            MaterialTheme.colorScheme.outline,
            "${changePct}%"
        )
    }
    
    Surface(
        color = color.copy(alpha = 0.2f),
        shape = MaterialTheme.shapes.small
    ) {
        Row(
            modifier = Modifier.padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(16.dp)
            )
            Text(
                text = text,
                style = MaterialTheme.typography.labelMedium,
                color = color,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun TrendChart(trendData: List<com.epiwatch.mobile.data.model.TrendPoint>) {
    // Convert trend data to chart entries
    val chartEntryModel = entryModelOf(
        *trendData.mapIndexed { index, point ->
            index.toFloat() to point.count.toFloat()
        }.toTypedArray()
    )
    
    ProvideChartStyle(chartStyle = m3ChartStyle()) {
        Chart(
            chart = columnChart(),
            model = chartEntryModel,
            startAxis = rememberStartAxis(),
            bottomAxis = rememberBottomAxis(),
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
        )
    }
}

@Composable
fun SeverityChip(severity: String) {
    val color = when (severity.lowercase()) {
        "significant" -> MaterialTheme.colorScheme.error
        "moderate" -> Color(0xFFFFA726)
        else -> MaterialTheme.colorScheme.outline
    }
    
    AssistChip(
        onClick = { },
        label = { Text("Severity: ${severity.capitalize()}") },
        colors = AssistChipDefaults.assistChipColors(
            containerColor = color.copy(alpha = 0.2f),
            labelColor = color
        )
    )
}
```

---

## 🚨 ALERTS SCREEN (Recent Alerts)

### File: `ui/alerts/AlertsViewModel.kt`

```kotlin
package com.epiwatch.mobile.ui.alerts

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.epiwatch.mobile.data.model.Alert
import com.epiwatch.mobile.data.repository.EpiWatchRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class AlertsUiState(
    val isLoading: Boolean = false,
    val alerts: List<Alert> = emptyList(),
    val selectedSeverity: String? = null,
    val error: String? = null
)

class AlertsViewModel(
    private val repository: EpiWatchRepository = EpiWatchRepository()
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(AlertsUiState(isLoading = true))
    val uiState: StateFlow<AlertsUiState> = _uiState.asStateFlow()
    
    init {
        loadAlerts()
    }
    
    fun loadAlerts(severity: String? = null, limit: Int = 20) {
        viewModelScope.launch {
            _uiState.value = AlertsUiState(isLoading = true)
            
            val result = repository.getAlerts(limit = limit, severity = severity)
            
            _uiState.value = AlertsUiState(
                isLoading = false,
                alerts = result.getOrElse { emptyList() },
                selectedSeverity = severity,
                error = result.exceptionOrNull()?.message
            )
        }
    }
    
    fun filterBySeverity(severity: String?) {
        _uiState.value = _uiState.value.copy(selectedSeverity = severity)
        loadAlerts(severity = severity)
    }
}
```

### File: `ui/alerts/AlertsScreen.kt`

```kotlin
package com.epiwatch.mobile.ui.alerts

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertsScreen(
    viewModel: AlertsViewModel = viewModel(),
    onNavigateBack: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Recent Alerts") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Severity filters
            SeverityFilters(
                selectedSeverity = uiState.selectedSeverity,
                onSeveritySelected = { viewModel.filterBySeverity(it) }
            )
            
            if (uiState.isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    contentPadding = PaddingValues(16.dp)
                ) {
                    items(uiState.alerts) { alert ->
                        AlertCard(alert = alert)
                    }
                }
            }
        }
    }
}

@Composable
fun SeverityFilters(
    selectedSeverity: String?,
    onSeveritySelected: (String?) -> Unit
) {
    val severities = listOf(
        "All" to null,
        "Critical" to "critical",
        "High" to "high",
        "Medium" to "medium",
        "Low" to "low"
    )
    
    LazyRow(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(severities) { (label, value) ->
            FilterChip(
                selected = selectedSeverity == value,
                onClick = { onSeveritySelected(value) },
                label = { Text(label) }
            )
        }
    }
}

@Composable
fun AlertCard(alert: com.epiwatch.mobile.data.model.Alert) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = getSeverityColor(alert.severityLevel).copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Header with severity badge
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = alert.disease,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    
                    // City location (ENHANCED!)
                    alert.cityLocation?.let { city ->
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                imageVector = Icons.Default.LocationOn,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = city,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
                
                SeverityBadge(level = alert.severityLevel, score = alert.severity)
            }
            
            // Context description (ENHANCED!)
            alert.contextDescription?.let { context ->
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = context,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
            
            Divider()
            
            // Cases info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "Actual Cases",
                    value = alert.actualCount.toString(),
                    color = MaterialTheme.colorScheme.error
                )
                MetricItem(
                    label = "Expected",
                    value = String.format("%.1f", alert.expectedCount),
                    color = MaterialTheme.colorScheme.outline
                )
                MetricItem(
                    label = "Deviation",
                    value = "+${String.format("%.0f", alert.deviationPct)}%",
                    color = MaterialTheme.colorScheme.error
                )
            }
            
            // Message
            Text(
                text = alert.message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            // Date
            Text(
                text = "Date: ${alert.date}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline
            )
        }
    }
}

@Composable
fun SeverityBadge(level: String, score: Double) {
    val color = getSeverityColor(level)
    
    Surface(
        color = color,
        shape = MaterialTheme.shapes.small
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = level.uppercase(),
                style = MaterialTheme.typography.labelSmall,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = String.format("%.1f", score),
                style = MaterialTheme.typography.labelSmall,
                color = Color.White
            )
        }
    }
}

@Composable
fun MetricItem(label: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

fun getSeverityColor(level: String): Color {
    return when (level.lowercase()) {
        "critical" -> Color(0xFFD32F2F)
        "high" -> Color(0xFFF57C00)
        "medium" -> Color(0xFFFFA726)
        else -> Color(0xFF757575)
    }
}
```

---

## 🧭 NAVIGATION SETUP

### File: `navigation/NavGraph.kt`

```kotlin
package com.epiwatch.mobile.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.epiwatch.mobile.ui.alerts.AlertsScreen
import com.epiwatch.mobile.ui.dashboard.DashboardScreen
import com.epiwatch.mobile.ui.trends.TrendsScreen

sealed class Screen(val route: String) {
    object Dashboard : Screen("dashboard")
    object Trends : Screen("trends")
    object Alerts : Screen("alerts")
}

@Composable
fun EpiWatchNavGraph(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Dashboard.route
    ) {
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToTrends = {
                    navController.navigate(Screen.Trends.route)
                },
                onNavigateToAlerts = {
                    navController.navigate(Screen.Alerts.route)
                }
            )
        }
        
        composable(Screen.Trends.route) {
            TrendsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Alerts.route) {
            AlertsScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

---

## 🎨 MAIN ACTIVITY

### File: `MainActivity.kt`

```kotlin
package com.epiwatch.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.epiwatch.mobile.navigation.EpiWatchNavGraph
import com.epiwatch.mobile.ui.theme.EpiWatchTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            EpiWatchTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    EpiWatchNavGraph()
                }
            }
        }
    }
}
```

---

**Next Steps:**
1. Copy all code files into your Android Studio project
2. Update `BASE_URL` in `EpiWatchApiService.kt` (use 10.0.2.2 for emulator or your local IP)
3. Get Google Maps API key from Google Cloud Console
4. Run the app on emulator or device
5. Test all 3 screens!

Would you like me to create the theme files and Firebase setup next?
