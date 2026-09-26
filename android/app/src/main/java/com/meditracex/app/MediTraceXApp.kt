package com.meditracex.app

import android.app.Application
import com.meditracex.app.data.api.ApiClient
import com.meditracex.app.data.local.TokenDataStore
import com.meditracex.app.data.repository.*

class MediTraceXApp : Application() {

    lateinit var tokenDataStore: TokenDataStore
    lateinit var apiClient: ApiClient

    lateinit var authRepository: AuthRepository
    lateinit var medicineRepository: MedicineRepository
    lateinit var pharmacyRepository: PharmacyRepository
    lateinit var inventoryRepository: InventoryRepository
    lateinit var predictionRepository: PredictionRepository
    lateinit var requestRepository: RequestRepository
    lateinit var watchlistRepository: WatchlistRepository

    override fun onCreate() {
        super.onCreate()

        tokenDataStore = TokenDataStore(this)
        apiClient = ApiClient.getInstance(this)

        authRepository = AuthRepository(apiClient.authApi, tokenDataStore)
        medicineRepository = MedicineRepository(apiClient.medicineApi)
        pharmacyRepository = PharmacyRepository(apiClient.pharmacyApi)
        inventoryRepository = InventoryRepository(apiClient.inventoryApi)
        predictionRepository = PredictionRepository(apiClient.predictionApi)
        requestRepository = RequestRepository(apiClient.requestApi)
        watchlistRepository = WatchlistRepository(apiClient.watchlistApi)
    }
}
