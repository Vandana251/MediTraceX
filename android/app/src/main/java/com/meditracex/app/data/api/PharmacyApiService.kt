package com.meditracex.app.data.api

import com.meditracex.app.data.model.NearbyPharmacyDiscoveryResponse
import com.meditracex.app.data.model.PharmacyBase
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface PharmacyApiService {
    @GET("api/pharmacies/nearby")
    suspend fun getNearbyRankedPharmacies(
        @Query("latitude") latitude: Double,
        @Query("longitude") longitude: Double,
        @Query("medicine_id") medicineId: Int,
        @Query("radius_km") radiusKm: Double = 25.0,
        @Query("limit") limit: Int = 10
    ): Response<NearbyPharmacyDiscoveryResponse>

    @GET("api/pharmacies/{pharmacy_id}")
    suspend fun getPharmacyById(
        @Path("pharmacy_id") pharmacyId: Int
    ): Response<PharmacyBase>

    @GET("api/pharmacies")
    suspend fun listPharmacies(): Response<List<PharmacyBase>>
}
