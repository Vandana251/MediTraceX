package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class MedicineItem(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("generic_name") val genericName: String,
    @SerializedName("brand_name") val brandName: String,
    @SerializedName("dosage") val dosage: String,
    @SerializedName("dosage_form") val dosageForm: String,
    @SerializedName("category") val category: String,
    @SerializedName("unit_price") val unitPrice: Double,
    @SerializedName("match_type") val matchType: String? = "prefix", // "exact", "prefix", "fuzzy"
    @SerializedName("edit_distance") val editDistance: Int = 0
)

data class MedicineListResponse(
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("page_size") val pageSize: Int,
    @SerializedName("items") val items: List<MedicineItem>
)
