package com.meditracex.app.data.repository

import com.meditracex.app.data.api.InventoryApiService
import com.meditracex.app.data.model.InventoryItem
import com.meditracex.app.data.model.InventoryUpdateRequest
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class InventoryRepository(private val inventoryApi: InventoryApiService) {

    fun getInventoryByPharmacy(pharmacyId: Int): Flow<Resource<List<InventoryItem>>> = flow {
        emit(Resource.Loading())
        try {
            val response = inventoryApi.getInventoryByPharmacy(pharmacyId)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch inventory"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun getSpecificStock(pharmacyId: Int, medicineId: Int): Flow<Resource<InventoryItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = inventoryApi.getSpecificStock(pharmacyId, medicineId)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Stock item not found"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun updateStock(inventoryId: Int, request: InventoryUpdateRequest): Flow<Resource<InventoryItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = inventoryApi.updateInventory(inventoryId, request)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Stock update failed (${response.code()})"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error during stock update"))
        }
    }
}
