package com.meditracex.app.ui.screens.inventory

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.meditracex.app.data.model.InventoryItem
import com.meditracex.app.ui.components.AvailabilityStatusBadge
import com.meditracex.app.ui.components.EmptyStateView
import com.meditracex.app.ui.components.ErrorStateView
import com.meditracex.app.ui.components.LoadingSpinner
import com.meditracex.app.ui.theme.*
import com.meditracex.app.ui.viewmodel.InventoryViewModel
import com.meditracex.app.utils.Resource

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PharmacyInventoryScreen(
    pharmacyId: Int,
    pharmacyName: String,
    viewModel: InventoryViewModel,
    onNavigateBack: () -> Unit
) {
    val inventoryState by viewModel.inventoryListState.collectAsState()
    var selectedItemForEdit by remember { mutableStateOf<InventoryItem?>(null) }
    var newStockQty by remember { mutableStateOf("") }

    LaunchedEffect(pharmacyId) {
        viewModel.fetchPharmacyInventory(pharmacyId)
    }

    Scaffold(
        containerColor = BackgroundLight,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(pharmacyName, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = TextPrimary)
                        Text("Live Store Inventory Manager", fontSize = 11.sp, color = PrimaryTeal)
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
                .padding(horizontal = 16.dp)
        ) {
            when (val state = inventoryState) {
                is Resource.Loading -> {
                    LoadingSpinner("Fetching store inventory catalog...")
                }
                is Resource.Error -> {
                    ErrorStateView(
                        message = state.message ?: "Failed to load inventory",
                        onRetry = { viewModel.fetchPharmacyInventory(pharmacyId) }
                    )
                }
                is Resource.Success -> {
                    val list = state.data ?: emptyList()
                    if (list.isEmpty()) {
                        EmptyStateView("No items in store", "This pharmacy currently has no active inventory rows.")
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
                                        Column(modifier = Modifier.weight(1f)) {
                                            Text(
                                                text = item.medicineName ?: "Medicine #${item.medicineId}",
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 14.sp,
                                                color = TextPrimary
                                            )
                                            Spacer(modifier = Modifier.height(2.dp))
                                            Text(
                                                text = "Batch: ${item.batchNumber} • Exp: ${item.expiryDate}",
                                                fontSize = 11.sp,
                                                color = TextTertiary
                                            )
                                            Spacer(modifier = Modifier.height(4.dp))
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                AvailabilityStatusBadge(status = item.stockStatus)
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(
                                                    text = "Stock: ${item.stockQuantity} units",
                                                    fontSize = 12.sp,
                                                    fontWeight = FontWeight.SemiBold,
                                                    color = TextSecondary
                                                )
                                            }
                                        }

                                        IconButton(onClick = {
                                            selectedItemForEdit = item
                                            newStockQty = item.stockQuantity.toString()
                                        }) {
                                            Icon(Icons.Default.Edit, contentDescription = "Edit Stock", tint = PrimaryTeal)
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

    if (selectedItemForEdit != null) {
        val item = selectedItemForEdit!!
        AlertDialog(
            onDismissRequest = { selectedItemForEdit = null },
            title = { Text("Update Stock Level", fontWeight = FontWeight.Bold) },
            text = {
                Column {
                    Text(item.medicineName ?: "Medicine", fontSize = 13.sp, color = TextPrimary)
                    Spacer(modifier = Modifier.height(10.dp))
                    OutlinedTextField(
                        value = newStockQty,
                        onValueChange = { newStockQty = it },
                        label = { Text("New Stock Quantity") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        val qty = newStockQty.toIntOrNull() ?: item.stockQuantity
                        viewModel.updateStock(item.id, qty, item.safetyStockThreshold)
                        selectedItemForEdit = null
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryTeal)
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { selectedItemForEdit = null }) {
                    Text("Cancel")
                }
            }
        )
    }
}
