package com.meditracex.app.data.model

import com.google.gson.annotations.SerializedName

data class DailyForecast(
    @SerializedName("date") val date: String,
    @SerializedName("day_name") val dayName: String,
    @SerializedName("predicted_demand") val predictedDemand: Double
)

data class DemandPredictionResponse(
    @SerializedName("medicine_id") val medicineId: Int,
    @SerializedName("medicine_name") val medicineName: String,
    @SerializedName("medicine_category") val medicineCategory: String,
    @SerializedName("pharmacy_id") val pharmacyId: Int,
    @SerializedName("pharmacy_name") val pharmacyName: String,
    @SerializedName("pharmacy_address") val pharmacyAddress: String,
    @SerializedName("current_stock") val currentStock: Int,
    @SerializedName("safety_threshold") val safetyThreshold: Int,
    @SerializedName("predicted_next_day_demand") val predictedNextDayDemand: Double,
    @SerializedName("predicted_7_day_demand") val predicted7DayDemand: Double,
    @SerializedName("stock_out_risk") val stockOutRisk: String, // "HIGH", "MEDIUM", "LOW"
    @SerializedName("risk_reason") val riskReason: String,
    @SerializedName("suggested_restock_quantity") val suggestedRestockQuantity: Int,
    @SerializedName("daily_forecasts") val dailyForecasts: List<DailyForecast>,
    @SerializedName("model_used") val modelUsed: String,
    @SerializedName("disclaimer") val disclaimer: String = "This prediction is for supply chain and inventory planning only, not medical advice."
)
