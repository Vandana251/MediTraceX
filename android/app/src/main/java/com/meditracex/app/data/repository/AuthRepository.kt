package com.meditracex.app.data.repository

import com.meditracex.app.data.api.AuthApiService
import com.meditracex.app.data.local.TokenDataStore
import com.meditracex.app.data.model.TokenResponse
import com.meditracex.app.data.model.UserLoginRequest
import com.meditracex.app.data.model.UserProfile
import com.meditracex.app.data.model.UserRegisterRequest
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class AuthRepository(
    private val authApi: AuthApiService,
    private val tokenDataStore: TokenDataStore
) {
    val accessTokenFlow: Flow<String?> = tokenDataStore.accessTokenFlow
    val userRoleFlow: Flow<String> = tokenDataStore.userRoleFlow
    val userNameFlow: Flow<String> = tokenDataStore.userNameFlow
    val userEmailFlow: Flow<String> = tokenDataStore.userEmailFlow

    fun register(request: UserRegisterRequest): Flow<Resource<TokenResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = authApi.register(request)
            if (response.isSuccessful && response.body() != null) {
                val data = response.body()!!
                tokenDataStore.saveAuthSession(
                    token = data.accessToken,
                    userId = data.userId,
                    name = data.name,
                    email = data.email,
                    role = data.role
                )
                emit(Resource.Success(data))
            } else {
                val errorMsg = response.errorBody()?.string() ?: "Registration failed (${response.code()})"
                emit(Resource.Error(errorMsg))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error during registration"))
        }
    }

    fun login(email: String, password: String): Flow<Resource<TokenResponse>> = flow {
        emit(Resource.Loading())
        try {
            val response = authApi.login(UserLoginRequest(email = email, password = password))
            if (response.isSuccessful && response.body() != null) {
                val data = response.body()!!
                tokenDataStore.saveAuthSession(
                    token = data.accessToken,
                    userId = data.userId,
                    name = data.name,
                    email = data.email,
                    role = data.role
                )
                emit(Resource.Success(data))
            } else {
                val errorMsg = response.errorBody()?.string() ?: "Invalid login credentials"
                emit(Resource.Error(errorMsg))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network connection error"))
        }
    }

    fun getProfile(): Flow<Resource<UserProfile>> = flow {
        emit(Resource.Loading())
        try {
            val response = authApi.getProfile()
            if (response.isSuccessful && response.body() != null) {
                emit(Resource.Success(response.body()!!))
            } else {
                emit(Resource.Error("Failed to fetch profile"))
            }
        } catch (e: Exception) {
            emit(Resource.Error(e.localizedMessage ?: "Network error"))
        }
    }

    suspend fun logout() {
        tokenDataStore.clearAuthSession()
    }
}
