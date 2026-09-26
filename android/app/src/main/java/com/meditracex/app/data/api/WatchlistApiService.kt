package com.meditracex.app.data.api

import com.meditracex.app.data.model.WatchlistCreate
import com.meditracex.app.data.model.WatchlistItem
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface WatchlistApiService {
    @POST("api/watchlist")
    suspend fun addToWatchlist(@Body request: WatchlistCreate): Response<WatchlistItem>

    @GET("api/watchlist")
    suspend fun getMyWatchlist(): Response<List<WatchlistItem>>

    @DELETE("api/watchlist/{watchlist_id}")
    suspend fun removeFromWatchlist(@Path("watchlist_id") watchlistId: Int): Response<Map<String, String>>
}
