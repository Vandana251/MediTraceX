package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class InventoryItem(
    @SerializedName("id") val id: Int,
    @SerializedName("pharmacy_id") val pharmacyId: Int,
    @SerializedName("pharmacy_name") val pharmacyName: String?,
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("medicine_name") val medicineName: String?,
    @SerializedName("generic_name") val genericName: String?,
    @SerializedName("stock_quantity") val stockQuantity: Int,
    @SerializedName("safety_stock_threshold") val safetyStockThreshold: Int,
    @SerializedName("reorder_quantity") val reorderQuantity: Int,
    @SerializedName("batch_number") val batchNumber: String,
    @SerializedName("expiry_date") val expiryDate: String,
    @SerializedName("stock_status") val stockStatus: String,
    @SerializedName("last_restocked_at") val lastRestockedAt: String?,
    @SerializedName("updated_at") val updatedAt: String
)

data class InventoryUpdateRequest(
    @SerializedName("stock_quantity") val stockQuantity: Int,
    @SerializedName("safety_stock_threshold") val safetyStockThreshold: Int? = 15,
    @SerializedName("batch_number") val batchNumber: String? = null,
    @SerializedName("expiry_date") val expiryDate: String? = null
)
