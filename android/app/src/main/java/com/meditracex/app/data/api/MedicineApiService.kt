package com.meditracex.app.data.api

import com.meditracex.app.data.model.MedicineItem
import com.meditracex.app.data.model.MedicineListResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface MedicineApiService {
    @GET("api/medicines/search")
    suspend fun searchMedicines(
        @Query("q") query: String,
        @Query("limit") limit: Int = 15
    ): Response<List<MedicineItem>>

    @GET("api/medicines/{medicine_id}")
    suspend fun getMedicineById(
        @Path("medicine_id") medicineId: Int
    ): Response<MedicineItem>

    @GET("api/medicines")
    suspend fun listMedicines(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20,
        @Query("category") category: String? = null
    ): Response<MedicineListResponse>
}
