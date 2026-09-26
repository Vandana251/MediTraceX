package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.TokenResponse
import com.meditracex.app.data.model.UserProfile
import com.meditracex.app.data.model.UserRegisterRequest
import com.meditracex.app.data.repository.AuthRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class AuthViewModel(private val authRepository: AuthRepository) : ViewModel() {

    private val _authState = MutableStateFlow<Resource<TokenResponse>>(Resource.Idle())
    val authState: StateFlow<Resource<TokenResponse>> = _authState.asStateFlow()

    private val _profileState = MutableStateFlow<Resource<UserProfile>>(Resource.Idle())
    val profileState: StateFlow<Resource<UserProfile>> = _profileState.asStateFlow()

    val accessToken: StateFlow<String?> = authRepository.accessTokenFlow.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = null
    )

    val userRole: StateFlow<String> = authRepository.userRoleFlow.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = "customer"
    )

    val userName: StateFlow<String> = authRepository.userNameFlow.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = ""
    )

    fun login(email: String, pass: String) {
        viewModelScope.launch {
            authRepository.login(email, pass).collect {
                _authState.value = it
            }
        }
    }

    fun register(name: String, email: String, phone: String, pass: String, role: String) {
        viewModelScope.launch {
            val req = UserRegisterRequest(name = name, email = email, phone = phone, password = pass, role = role)
            authRepository.register(req).collect {
                _authState.value = it
            }
        }
    }

    fun fetchProfile() {
        viewModelScope.launch {
            authRepository.getProfile().collect {
                _profileState.value = it
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _authState.value = Resource.Idle()
        }
    }

    fun resetAuthState() {
        _authState.value = Resource.Idle()
    }
}
