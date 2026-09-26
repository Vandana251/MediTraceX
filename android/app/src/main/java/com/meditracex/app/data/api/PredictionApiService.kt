package com.meditracex.app.data.api

import com.meditracex.app.data.model.DemandPredictionResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface PredictionApiService {
    @GET("api/predictions/{pharmacy_id}/{medicine_id}")
    suspend fun getDemandPrediction(
        @Path("pharmacy_id") pharmacyId: Int,
        @Path("medicine_id") medicineId: Int,
        @Query("forecast_days") forecastDays: Int = 7
    ): Response<DemandPredictionResponse>
}
