package com.meditracex.app.data.api

import com.meditracex.app.data.model.MedicineRequestCreate
import com.meditracex.app.data.model.MedicineRequestItem
import com.meditracex.app.data.model.MedicineRequestStatusUpdate
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface RequestApiService {
    @POST("api/requests")
    suspend fun createRequest(@Body request: MedicineRequestCreate): Response<MedicineRequestItem>

    @GET("api/requests/my")
    suspend fun getMyRequests(): Response<List<MedicineRequestItem>>

    @GET("api/requests/pharmacy")
    suspend fun getPharmacyRequests(): Response<List<MedicineRequestItem>>

    @GET("api/requests/{request_id}")
    suspend fun getRequestById(@Path("request_id") requestId: Int): Response<MedicineRequestItem>

    @PUT("api/requests/{request_id}/status")
    suspend fun updateRequestStatus(
        @Path("request_id") requestId: Int,
        @Body statusUpdate: MedicineRequestStatusUpdate
    ): Response<MedicineRequestItem>
}
