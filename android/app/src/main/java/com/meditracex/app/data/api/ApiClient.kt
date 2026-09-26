package com.meditracex.app.data.api

import android.content.Context
import com.meditracex.app.data.local.TokenDataStore
import com.meditracex.app.utils.Constants
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class ApiClient private constructor(context: Context) {

    private val tokenDataStore = TokenDataStore(context)

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val authInterceptor = AuthInterceptor(tokenDataStore)

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(Constants.BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val authApi: AuthApiService = retrofit.create(AuthApiService::class.java)
    val medicineApi: MedicineApiService = retrofit.create(MedicineApiService::class.java)
    val pharmacyApi: PharmacyApiService = retrofit.create(PharmacyApiService::class.java)
    val inventoryApi: InventoryApiService = retrofit.create(InventoryApiService::class.java)
    val predictionApi: PredictionApiService = retrofit.create(PredictionApiService::class.java)
    val requestApi: RequestApiService = retrofit.create(RequestApiService::class.java)
    val watchlistApi: WatchlistApiService = retrofit.create(WatchlistApiService::class.java)

    companion object {
        @Volatile
        private var INSTANCE: ApiClient? = null

        fun getInstance(context: Context): ApiClient {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: ApiClient(context.applicationContext).also { INSTANCE = it }
            }
        }
    }
}
