package com.meditracex.app.data.repository

import com.meditracex.app.data.api.WatchlistApiService
import com.meditracex.app.data.model.WatchlistCreate
import com.meditracex.app.data.model.WatchlistItem
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class WatchlistRepository(private val watchlistApi: WatchlistApiService) {

    fun addToWatchlist(medicineId: Int, pharmacyId: Int? = null): Flow<Resource<WatchlistItem>> = flow {
        emit(Resource.Loading())
        try {
            val response = watchlistApi.addToWatchlist(
                WatchlistCreate(medicineId = medicineId, pharmacyId = pharmacyId, notifyOnRestock = true)
            )
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to add to watchlist"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun getMyWatchlist(): Flow<Resource<List<WatchlistItem>>> = flow {
        emit(Resource.Loading())
        try {
            val response = watchlistApi.getMyWatchlist()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch watchlist"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    fun removeFromWatchlist(watchlistId: Int): Flow<Resource<Boolean>> = flow {
        emit(Resource.Loading())
        try {
            val response = watchlistApi.removeFromWatchlist(watchlistId)
            if (response.isSuccessful) {
                emit(Resource.Success(true))
            } else {
                emit(Resource.Error("Failed to remove item"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }
}
