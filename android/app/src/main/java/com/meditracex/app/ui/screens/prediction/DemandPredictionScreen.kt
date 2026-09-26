package com.meditracex.app.ui.screens.prediction

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.meditracex.app.ui.components.ErrorStateView
import com.meditracex.app.ui.components.LoadingSpinner
import com.meditracex.app.ui.components.PredictionResultCard
import com.meditracex.app.ui.theme.*
import com.meditracex.app.ui.viewmodel.PredictionViewModel
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DemandPredictionScreen(
    pharmacyId: Int,
    medicineId: Int,
    viewModel: PredictionViewModel,
    onNavigateBack: () -> Unit
) {
    val predictionState by viewModel.predictionState.collectAsState()

    LaunchedEffect(pharmacyId, medicineId) {
        viewModel.fetchDemandPrediction(pharmacyId, medicineId, forecastDays = 7)
    }

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("ML Demand Forecast", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                        Text("Predictive Inventory Intelligence", fontSize = 11.sp, color = PrimaryTeal)
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceLight)
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            when (val state = predictionState) {
                is Resource.Loading -> {
                    LoadingSpinner("Running Gradient Boosting time-series inference...")
                }
                is Resource.Error -> {
                    ErrorStateView(
                        message = state.message ?: "Prediction failed",
                        onRetry = { viewModel.fetchDemandPrediction(pharmacyId, medicineId) }
                    )
                }
                is Resource.Success -> {
                    val prediction = state.data
                    if (prediction != null) {
                        Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
                            PredictionResultCard(prediction = prediction)
                        }
                    }
                }
                is Resource.Idle -> {}
            }
        }
    }
}
