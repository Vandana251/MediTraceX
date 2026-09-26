package com.meditracex.app.data.repository

import com.meditracex.app.data.api.MedicineApiService
import com.meditracex.app.data.model.MedicineItem
import com.meditracex.app.data.model.MedicineListResponse
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class MedicineRepository(private val medicineApi: MedicineApiService) {

    fun searchMedicines(query: String, limit: Int = 15): Flow<Resource<List<MedicineItem>>> = flow {
        if (query.isBlank()) {
            emit(Resource.Success(emptyList()))
            return@flow
        }
        emit(Resource.Loading())
        try {
            val response = medicineApi.searchMedicines(query = query.trim(), limit = limit)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to search medicines (${response.code()})"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Error connecting to search engine"))
        }
    }

    fun getMedicineById(medicineId: Int): Flow<Resource<MedicineItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = medicineApi.getMedicineById(medicineId)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Medicine not found"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun listMedicines(page: Int = 1, pageSize: Int = 20, category: String? = null): Flow<Resource<MedicineListResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = medicineApi.listMedicines(page = page, pageSize = pageSize, category = category)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to list catalog"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }
}
