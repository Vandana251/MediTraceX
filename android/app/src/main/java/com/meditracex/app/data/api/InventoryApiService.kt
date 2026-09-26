package com.meditracex.app.data.api

import com.meditracex.app.data.model.InventoryItem
import com.meditracex.app.data.model.InventoryUpdateRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PUT
import retrofit2.http.Path

interface InventoryApiService {
    @GET("api/inventory/pharmacy/{pharmacy_id}")
    suspend fun getInventoryByPharmacy(
        @Path("pharmacy_id") pharmacyId: Int
    ): Response<List<InventoryItem>>

    @GET("api/inventory/{pharmacy_id}/{medicine_id}")
    suspend fun getSpecificStock(
        @Path("pharmacy_id") pharmacyId: Int,
        @Path("medicine_id") medicineId: Int
    ): Response<InventoryItem>

    @PUT("api/inventory/{inventory_id}")
    suspend fun updateInventory(
        @Path("inventory_id") inventoryId: Int,
        @Body request: InventoryUpdateRequest
    ): Response<InventoryItem>
}
