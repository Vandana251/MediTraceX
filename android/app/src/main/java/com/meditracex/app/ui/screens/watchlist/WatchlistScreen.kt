package com.meditracex.app.ui.screens.watchlist

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.NotificationsActive
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
import com.meditracex.app.ui.viewmodel.WatchlistViewModel
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WatchlistScreen(
    viewModel: WatchlistViewModel,
    onNavigateBack: () -> Unit
) {
    val watchlistState by viewModel.watchlistState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadWatchlist()
    }

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                title = { Text("Restock Watchlist (Notify Me)", fontSize = 17.sp, fontWeight = FontWeight.Bold, color = TextPrimary) },
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
            when (val state = watchlistState) {
                is Resource.Loading -> {
                    LoadingSpinner("Loading restock subscriptions...")
                }
                is Resource.Error -> {
                    ErrorStateView(
                        message = state.message ?: "Failed to fetch watchlist",
                        onRetry = { viewModel.loadWatchlist() }
                    )
                }
                is Resource.Success -> {
                    val list = state.data ?: emptyList()
                    if (list.isEmpty()) {
                        EmptyStateView(
                            title = "Watchlist is empty",
                            subtitle = "Tap 'Notify Me' on any out-of-stock medicine to receive restock notifications."
                        )
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                            contentPadding = PaddingValues(vertical = 14.dp)
                        ) {
                            items(list) { item ->
                                Card(
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(12.dp),
                                    colors = CardDefaults.cardColors(containerColor = SurfaceLight),
                                    border = BorderStroke(1.dp, DividerColor)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(14.dp).fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                            Icon(
                                                Icons.Default.NotificationsActive,
                                                contentDescription = null,
                                                tint = PrimaryTeal,
                                                modifier = Modifier.size(24.dp)
                                            )
                                            Spacer(modifier = Modifier.width(10.dp))
                                            Column {
                                                Text(
                                                    text = item.medicineName ?: "Medicine #${item.medicineId}",
                                                    fontWeight = FontWeight.Bold,
                                                    fontSize = 14.sp,
                                                    color = TextPrimary
                                                )
                                                Text(
                                                    text = "Store: ${item.pharmacyName ?: "All Nearby Pharmacies"}",
                                                    fontSize = 12.sp,
                                                    color = TextSecondary
                                                )
                                            }
                                        }

                                        IconButton(onClick = { viewModel.removeItem(item.id) }) {
                                            Icon(Icons.Default.Delete, contentDescription = "Remove", tint = StockOutRed)
                                        }
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
