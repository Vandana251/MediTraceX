package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class RankedPharmacy(
    @SerializedName("rank") val rank: Int,
    @SerializedName("pharmacy_id") val pharmacyId: Int,
    @SerializedName("pharmacy_name") val pharmacyName: String,
    @SerializedName("address") val address: String,
    @SerializedName("city") val city: String,
    @SerializedName("distance_km") val distanceKm: Double,
    @SerializedName("availability_status") val availabilityStatus: String, // "Available", "Low Stock", "Out of Stock"
    @SerializedName("stock_quantity") val stockQuantity: Int,
    @SerializedName("stock_freshness") val stockFreshness: String = "Live Synced",
    @SerializedName("safety_stock_threshold") val safetyStockThreshold: Int = 15,
    @SerializedName("contact_phone") val contactPhone: String,
    @SerializedName("is_24_7") val is24x7: Boolean,
    @SerializedName("operating_hours") val operatingHours: String,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double
)

data class NearbyPharmacyDiscoveryResponse(
    @SerializedName("target_medicine_id") val targetMedicineId: Int,
    @SerializedName("target_medicine_name") val targetMedicineName: String,
    @SerializedName("user_latitude") val userLatitude: Double,
    @SerializedName("user_longitude") val userLongitude: Double,
    @SerializedName("search_radius_km") val searchRadiusKm: Double,
    @SerializedName("total_found") val totalFound: Int,
    @SerializedName("ranked_pharmacies") val rankedPharmacies: List<RankedPharmacy>
)

data class PharmacyBase(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("license_number") val licenseNumber: String,
    @SerializedName("address") val address: String,
    @SerializedName("city") val city: String,
    @SerializedName("pincode") val pincode: String,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("contact_phone") val contactPhone: String,
    @SerializedName("contact_email") val contactEmail: String,
    @SerializedName("is_24_7") val is24x7: Boolean,
    @SerializedName("is_active") val isActive: Boolean
)
