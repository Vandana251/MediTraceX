package com.meditracex.app.data.api

import com.meditracex.app.data.model.TokenResponse
import com.meditracex.app.data.model.UserLoginRequest
import com.meditracex.app.data.model.UserProfile
import com.meditracex.app.data.model.UserRegisterRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApiService {
    @POST("api/auth/register")
    suspend fun register(@Body request: UserRegisterRequest): Response<TokenResponse>

    @POST("api/auth/login")
    suspend fun login(@Body request: UserLoginRequest): Response<TokenResponse>

    @GET("api/auth/me")
    suspend fun getProfile(): Response<UserProfile>
}
