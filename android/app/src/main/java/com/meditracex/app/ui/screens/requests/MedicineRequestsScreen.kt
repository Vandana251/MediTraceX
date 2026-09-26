package com.meditracex.app.ui.screens.requests

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.meditracex.app.ui.components.EmptyStateView
import com.meditracex.app.ui.components.ErrorStateView
import com.meditracex.app.ui.components.LoadingSpinner
import com.meditracex.app.ui.theme.*
import com.meditracex.app.ui.viewmodel.RequestViewModel
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedicineRequestsScreen(
    viewModel: RequestViewModel,
    onNavigateBack: () -> Unit
) {
    val requestsState by viewModel.myRequestsState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadMyRequests()
    }

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                title = { Text("My Medicine Requests", fontSize = 17.sp, fontWeight = FontWeight.Bold, color = TextPrimary) },
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
                .padding(horizontal = 16.dp)
        ) {
            when (val state = requestsState) {
                is Resource.Loading -> {
                    LoadingSpinner("Fetching procurement requests...")
                }
                is Resource.Error -> {
                    ErrorStateView(
                        message = state.message ?: "Failed to fetch requests",
                        onRetry = { viewModel.loadMyRequests() }
                    )
                }
                is Resource.Success -> {
                    val list = state.data ?: emptyList()
                    if (list.isEmpty()) {
                        EmptyStateView(
                            title = "No requests submitted",
                            subtitle = "When you cannot find a medicine, place a request from the Nearby Discovery screen."
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                            contentPadding = PaddingValues(vertical = 14.dp)
                        ) {
                            items(list) { req ->
                                Card(
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp),
                                    colors = CardDefaults.cardColors(containerColor = SurfaceLight),
                                    border = BorderStroke(1.dp, DividerColor)
                                ) {
                                    Column(modifier = Modifier.padding(14.dp)) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Text(
                                                text = req.medicineName ?: "Medicine #${req.medicineId}",
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 15.sp,
                                                color = TextPrimary
                                            )
                                            Surface(
                                                shape = RoundedCornerShape(6.dp),
                                                color = when (req.status) {
                                                    "FULFILLED" -> StockAvailableBg
                                                    "ACCEPTED" -> PrimaryTealContainer
                                                    else -> StockLowBg
                                                }
                                            ) {
                                                Text(
                                                    text = req.status,
                                                    fontSize = 11.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    color = when (req.status) {
                                                        "FULFILLED" -> StockAvailableGreen
                                                        "ACCEPTED" -> OnPrimaryTealContainer
                                                        else -> StockLowAmber
                                                    },
                                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                                )
                                            }
                                        }

                                        Spacer(modifier = Modifier.height(4.dp))

                                        Text(
                                            text = "Target Store: ${req.pharmacyName ?: "Broadcast to All Nearby Stores"}",
                                            fontSize = 12.sp,
                                            color = TextSecondary
                                        )

                                        Text(
                                            text = "Quantity: ${req.quantityRequested} units • Notes: ${req.notes ?: "N/A"}",
                                            fontSize = 11.sp,
                                            color = TextTertiary
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
                is Resource.Idle -> {}
            }
        }
    }
}
