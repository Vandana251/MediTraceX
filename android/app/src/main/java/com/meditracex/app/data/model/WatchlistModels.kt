package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class WatchlistCreate(
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("pharmacy_id") val pharmacyId: Int? = null,
    @SerializedName("notify_on_restock") val notifyOnRestock: Boolean = true
)

data class WatchlistItem(
    @SerializedName("id") val id: Int,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("medicine_name") val medicineName: String?,
    @SerializedName("pharmacy_id") val pharmacyId: Int?,
    @SerializedName("pharmacy_name") val pharmacyName: String?,
    @SerializedName("notify_on_restock") val notifyOnRestock: Boolean,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("created_at") val createdAt: String
)
