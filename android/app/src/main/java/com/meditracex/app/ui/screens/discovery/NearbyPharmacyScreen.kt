package com.meditracex.app.ui.screens.discovery

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.meditracex.app.ui.components.EmptyStateView
import com.meditracex.app.ui.components.ErrorStateView
import com.meditracex.app.ui.components.LoadingSpinner
import com.meditracex.app.ui.components.PharmacyRankCard
import com.meditracex.app.ui.theme.*
import com.meditracex.app.ui.viewmodel.PharmacyDiscoveryViewModel
import com.meditracex.app.ui.viewmodel.RequestViewModel
import com.meditracex.app.ui.viewmodel.WatchlistViewModel
import com.meditracex.app.utils.Constants
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NearbyPharmacyScreen(
    medicineId: Int,
    medicineName: String,
    viewModel: PharmacyDiscoveryViewModel,
    watchlistViewModel: WatchlistViewModel,
    requestViewModel: RequestViewModel,
    onNavigateBack: () -> Unit,
    onNavigateToPrediction: (pharmacyId: Int, medicineId: Int) -> Unit
) {
    val discoveryState by viewModel.discoveryState.collectAsState()
    val watchlistActionState by watchlistViewModel.actionState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    var showRequestDialog by remember { mutableStateOf(false) }
    var requestQuantity by remember { mutableStateOf("1") }
    var requestNotes by remember { mutableStateOf("") }

    LaunchedEffect(medicineId) {
        viewModel.discoverNearbyPharmacies(medicineId = medicineId)
    }

    LaunchedEffect(watchlistActionState) {
        if (watchlistActionState is Resource.Success) {
            snackbarHostState.showSnackbar(watchlistActionState.data ?: "Watchlist updated")
            watchlistViewModel.resetActionState()
        }
    }

    Scaffold(
        containerColor = BackgroundLight,
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(medicineName, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                        Text("Nearby Pharmacies (Min-Heap Ranked)", fontSize = 11.sp, color = PrimaryTeal)
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(onClick = { watchlistViewModel.addToWatchlist(medicineId) }) {
                        Icon(Icons.Default.BookmarkAdd, contentDescription = "Notify Me", tint = PrimaryTeal)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceLight)
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = { showRequestDialog = true },
                icon = { Icon(Icons.Default.AddShoppingCart, contentDescription = null) },
                text = { Text("Request Medicine", fontSize = 13.sp) },
                containerColor = PrimaryTeal,
                contentColor = SurfaceLight
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp)
        ) {
            when (val state = discoveryState) {
                is Resource.Loading -> {
                    LoadingSpinner("Calculating Haversine distances & Min-Heap ranking...")
                }
                is Resource.Error -> {
                    ErrorStateView(
                        message = state.message ?: "Failed to find nearby pharmacies",
                        onRetry = { viewModel.discoverNearbyPharmacies(medicineId) }
                    )
                }
                is Resource.Success -> {
                    val data = state.data
                    val pharmacies = data?.rankedPharmacies ?: emptyList()

                    if (pharmacies.isEmpty()) {
                        EmptyStateView(
                            title = "No pharmacies found in range",
                            subtitle = "Try expanding search radius or subscribe to Notify Me restock alerts."
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                            contentPadding = PaddingValues(vertical = 14.dp)
                        ) {
                            item {
                                Surface(
                                    shape = RoundedCornerShape(12.dp),
                                    color = PrimaryTealContainer,
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(Icons.Default.CheckCircle, contentDescription = null, tint = OnPrimaryTealContainer, modifier = Modifier.size(18.dp))
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "Ranked ${pharmacies.size} stores by In-Stock availability & closest distance",
                                            fontSize = 12.sp,
                                            fontWeight = FontWeight.Medium,
                                            color = OnPrimaryTealContainer
                                        )
                                    }
                                }
                            }

                            items(pharmacies) { pharmacy ->
                                PharmacyRankCard(
                                    pharmacy = pharmacy,
                                    onViewPrediction = {
                                        onNavigateToPrediction(pharmacy.pharmacyId, medicineId)
                                    }
                                )
                            }
                        }
                    }
                }
                is Resource.Idle -> {}
            }
        }
    }

    // Request Medicine Dialog
    if (showRequestDialog) {
        AlertDialog(
            onDismissRequest = { showRequestDialog = false },
            title = { Text("Request Medicine", fontWeight = FontWeight.Bold, fontSize = 16.sp) },
            text = {
                Column {
                    Text("Medicine: $medicineName", fontSize = 13.sp, color = TextPrimary)
                    Spacer(modifier = Modifier.height(10.dp))
                    OutlinedTextField(
                        value = requestQuantity,
                        onValueChange = { requestQuantity = it },
                        label = { Text("Quantity Needed") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    OutlinedTextField(
                        value = requestNotes,
                        onValueChange = { requestNotes = it },
                        label = { Text("Notes / Prescription upload note") },
                        maxLines = 3,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val qty = requestQuantity.toIntOrNull() ?: 1
                        requestViewModel.submitRequest(medicineId = medicineId, qty = qty, notes = requestNotes)
                        showRequestDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryTeal)
                ) {
                    Text("Submit Request")
                }
            },
            dismissButton = {
                TextButton(onClick = { showRequestDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
