package com.meditracex.app.ui.screens.search

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
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
import com.meditracex.app.ui.components.MedicineItemCard
import com.meditracex.app.ui.theme.*
import com.meditracex.app.ui.viewmodel.MedicineSearchViewModel
import com.meditracex.app.utils.Constants
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedicineSearchScreen(
    viewModel: MedicineSearchViewModel,
    userRole: String,
    userName: String,
    onMedicineSelected: (medicineId: Int, medicineName: String) -> Unit,
    onNavigateToRequests: () -> Unit,
    onNavigateToWatchlist: () -> Unit,
    onNavigateToInventory: () -> Unit,
    onLogout: () -> Unit
) {
    val searchQuery by viewModel.searchQuery.collectAsState()
    val searchResults by viewModel.searchResults.collectAsState()

    val categories = listOf("All", "Analgesic", "Antibiotic", "Antihistamine", "Cardiovascular", "Antidiabetic", "Gastrointestinal", "Supplements")
    var selectedCategory by remember { mutableStateOf("All") }

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("MediTraceX", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                            Spacer(modifier = Modifier.width(6.dp))
                            Surface(
                                shape = RoundedCornerShape(4.dp),
                                color = PrimaryTealContainer
                            ) {
                                Text(
                                    text = if (userRole.contains("admin", ignoreCase = true)) "PHARMACY" else "CUSTOMER",
                                    fontSize = 9.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = OnPrimaryTealContainer,
                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                )
                            }
                        }
                        Text(Constants.APP_TAGLINE, fontSize = 11.sp, color = PrimaryTeal, fontWeight = FontWeight.Medium)
                    }
                },
                actions = {
                    IconButton(onClick = onNavigateToRequests) {
                        Icon(Icons.Default.ReceiptLong, contentDescription = "Requests", tint = TextSecondary)
                    }
                    IconButton(onClick = onNavigateToWatchlist) {
                        Icon(Icons.Default.Notifications, contentDescription = "Watchlist", tint = TextSecondary)
                    }
                    if (userRole.contains("admin", ignoreCase = true) || userRole.contains("pharmacy", ignoreCase = true)) {
                        IconButton(onClick = onNavigateToInventory) {
                            Icon(Icons.Default.Inventory2, contentDescription = "Inventory", tint = PrimaryTeal)
                        }
                    }
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.Logout, contentDescription = "Sign Out", tint = TextTertiary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = SurfaceLight)
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // Search Input Field
            Surface(
                color = SurfaceLight,
                shadowElevation = 2.dp,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp)) {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = { viewModel.onSearchQueryChanged(it) },
                        placeholder = { Text("Search medicine name, generic, or brand (e.g., 'para', 'dolo')...", fontSize = 13.sp) },
                        leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = PrimaryTeal) },
                        trailingIcon = {
                            if (searchQuery.isNotEmpty()) {
                                IconButton(onClick = { viewModel.onSearchQueryChanged("") }) {
                                    Icon(Icons.Default.Clear, contentDescription = "Clear")
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = PrimaryTeal,
                            unfocusedBorderColor = DividerColor,
                            focusedContainerColor = BackgroundLight,
                            unfocusedContainerColor = BackgroundLight
                        )
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Category Pill Chips
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .horizontalScroll(rememberScrollState()),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        categories.forEach { cat ->
                            FilterChip(
                                selected = selectedCategory == cat,
                                onClick = {
                                    selectedCategory = cat
                                    if (cat == "All") {
                                        viewModel.onSearchQueryChanged(searchQuery.ifBlank { "para" })
                                    } else {
                                        viewModel.onSearchQueryChanged(cat.take(4).lowercase())
                                    }
                                },
                                label = { Text(cat, fontSize = 12.sp) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = PrimaryTealContainer,
                                    selectedLabelColor = OnPrimaryTealContainer
                                )
                            )
                        }
                    }
                }
            }

            // Results List
            Box(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
                when (val state = searchResults) {
                    is Resource.Loading -> {
                        LoadingSpinner("Running Trie sub-millisecond search...")
                    }
                    is Resource.Error -> {
                        ErrorStateView(
                            message = state.message ?: "Failed to query medicines",
                            onRetry = { viewModel.onSearchQueryChanged(searchQuery) }
                        )
                    }
                    is Resource.Success -> {
                        val list = state.data ?: emptyList()
                        if (list.isEmpty()) {
                            EmptyStateView(
                                title = "No medicines found",
                                subtitle = "Try searching for active molecule names like 'Paracetamol', 'Amoxicillin', or 'Cetirizine'."
                            )
                        } else {
                            LazyColumn(
                                modifier = Modifier.fillMaxSize(),
                                verticalArrangement = Arrangement.spacedBy(10.dp),
                                contentPadding = PaddingValues(vertical = 14.dp)
                            ) {
                                item {
                                    Text(
                                        text = "${list.size} Medicines Found (Trie Prefix & Typo Match)",
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = TextSecondary,
                                        modifier = Modifier.padding(bottom = 4.dp)
                                    )
                                }

                                items(list) { medicine ->
                                    MedicineItemCard(
                                        medicine = medicine,
                                        onClick = { onMedicineSelected(medicine.id, medicine.name) }
                                    )
                                }
                            }
                        }
                    }
                    is Resource.Idle -> {}
                }
            }
        }
    }
}
