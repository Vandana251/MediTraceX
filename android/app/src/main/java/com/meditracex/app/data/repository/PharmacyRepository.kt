package com.meditracex.app.data.repository

import com.meditracex.app.data.api.PharmacyApiService
import com.meditracex.app.data.model.NearbyPharmacyDiscoveryResponse
import com.meditracex.app.data.model.PharmacyBase
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class PharmacyRepository(private val pharmacyApi: PharmacyApiService) {

    fun getNearbyRankedPharmacies(
        latitude: Double,
        longitude: Double,
        medicineId: Int,
        radiusKm: Double = 25.0,
        limit: Int = 10
    ): Flow<Resource<NearbyPharmacyDiscoveryResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = pharmacyApi.getNearbyRankedPharmacies(
                latitude = latitude,
                longitude = longitude,
                medicineId = medicineId,
                radiusKm = radiusKm,
                limit = limit
            )
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Discovery query failed (${response.code()})"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network connection error"))
        }
    }

    fun getPharmacyById(pharmacyId: Int): Flow<Resource<PharmacyBase>> = flow {
        emit(Resource.Loading())
        try {
            val response = pharmacyApi.getPharmacyById(pharmacyId)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Pharmacy not found"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun listPharmacies(): Flow<Resource<List<PharmacyBase>>> = flow {
        emit(Resource.Loading())
        try {
            val response = pharmacyApi.listPharmacies()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to list pharmacies"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }
}
