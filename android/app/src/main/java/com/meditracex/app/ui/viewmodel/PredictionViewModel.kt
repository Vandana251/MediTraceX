package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.DemandPredictionResponse
import com.meditracex.app.data.repository.PredictionRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class PredictionViewModel(private val predictionRepository: PredictionRepository) : ViewModel() {

    private val _predictionState = MutableStateFlow<Resource<DemandPredictionResponse>>(Resource.Idle())
    val predictionState: StateFlow<Resource<DemandPredictionResponse>> = _predictionState.asStateFlow()

    fun fetchDemandPrediction(pharmacyId: Int, medicineId: Int, forecastDays: Int = 7) {
        viewModelScope.launch {
            predictionRepository.getDemandPrediction(pharmacyId, medicineId, forecastDays).collect {
                _predictionState.value = it
            }
        }
    }
}
