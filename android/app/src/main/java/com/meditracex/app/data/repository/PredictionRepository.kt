package com.meditracex.app.data.repository

import com.meditracex.app.data.api.PredictionApiService
import com.meditracex.app.data.model.DemandPredictionResponse
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class PredictionRepository(private val predictionApi: PredictionApiService) {

    fun getDemandPrediction(
        pharmacyId: Int,
        medicineId: Int,
        forecastDays: Int = 7
    ): Flow<Resource<DemandPredictionResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = predictionApi.getDemandPrediction(
                pharmacyId = pharmacyId,
                medicineId = medicineId,
                forecastDays = forecastDays
            )
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("ML Prediction failed (${response.code()})"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Failed to connect to ML prediction service"))
        }
    }
}
