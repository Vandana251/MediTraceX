package com.meditracex.app.data.repository

import com.meditracex.app.data.api.RequestApiService
import com.meditracex.app.data.model.MedicineRequestCreate
import com.meditracex.app.data.model.MedicineRequestItem
import com.meditracex.app.data.model.MedicineRequestStatusUpdate
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class RequestRepository(private val requestApi: RequestApiService) {

    fun createRequest(request: MedicineRequestCreate): Flow<Resource<MedicineRequestItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = requestApi.createRequest(request)
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to submit request (${response.code()})"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun getMyRequests(): Flow<Resource<List<MedicineRequestItem>>> = flow {
        emit(Resource.Loading())
        try {
            val response = requestApi.getMyRequests()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch requests"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun getPharmacyRequests(): Flow<Resource<List<MedicineRequestItem>>> = flow {
        emit(Resource.Loading())
        try {
            val response = requestApi.getPharmacyRequests()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch pharmacy requests"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun updateStatus(requestId: Int, status: String): Flow<Resource<MedicineRequestItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = requestApi.updateRequestStatus(requestId, MedicineRequestStatusUpdate(status = status))
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Status update failed"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }
}
