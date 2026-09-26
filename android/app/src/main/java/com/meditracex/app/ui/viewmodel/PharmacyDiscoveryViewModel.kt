package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.NearbyPharmacyDiscoveryResponse
import com.meditracex.app.data.repository.PharmacyRepository
import com.meditracex.app.utils.Constants
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class PharmacyDiscoveryViewModel(private val pharmacyRepository: PharmacyRepository) : ViewModel() {

    private val _discoveryState = MutableStateFlow<Resource<NearbyPharmacyDiscoveryResponse>>(Resource.Idle())
    val discoveryState: StateFlow<Resource<NearbyPharmacyDiscoveryResponse>> = _discoveryState.asStateFlow()

    fun discoverNearbyPharmacies(
        medicineId: Int,
        latitude: Double = Constants.DEFAULT_LATITUDE,
        longitude: Double = Constants.DEFAULT_LONGITUDE,
        radiusKm: Double = Constants.DEFAULT_SEARCH_RADIUS_KM
    ) {
        viewModelScope.launch {
            pharmacyRepository.getNearbyRankedPharmacies(
                latitude = latitude,
                longitude = longitude,
                medicineId = medicineId,
                radiusKm = radiusKm,
                limit = 15
            ).collect {
                _discoveryState.value = it
            }
        }
    }
}
