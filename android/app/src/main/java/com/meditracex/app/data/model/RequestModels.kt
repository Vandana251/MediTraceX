package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class MedicineRequestCreate(
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("pharmacy_id") val pharmacyId: Int? = null,
    @SerializedName("quantity_requested") val quantityRequested: Int = 1,
    @SerializedName("notes") val notes: String? = null
)

data class MedicineRequestStatusUpdate(
    @SerializedName("status") val status: String
)

data class MedicineRequestItem(
    @SerializedName("id") val id: Int,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("user_name") val userName: String?,
    @SerializedName("user_phone") val userPhone: String?,
    @SerializedName("pharmacy_id") val pharmacyId: Int?,
    @SerializedName("pharmacy_name") val pharmacyName: String?,
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("medicine_name") val medicineName: String?,
    @SerializedName("quantity_requested") val quantityRequested: Int,
    @SerializedName("status") val status: String, // PENDING, ACCEPTED, FULFILLED, CANCELLED, NOT_AVAILABLE
    @SerializedName("notes") val notes: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)
