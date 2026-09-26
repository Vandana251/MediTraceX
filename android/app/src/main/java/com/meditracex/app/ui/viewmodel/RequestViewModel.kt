package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.MedicineRequestCreate
import com.meditracex.app.data.model.MedicineRequestItem
import com.meditracex.app.data.repository.RequestRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class RequestViewModel(private val requestRepository: RequestRepository) : ViewModel() {

    private val _myRequestsState = MutableStateFlow<Resource<List<MedicineRequestItem>>>(Resource.Idle())
    val myRequestsState: StateFlow<Resource<List<MedicineRequestItem>>> = _myRequestsState.asStateFlow()

    private val _createRequestState = MutableStateFlow<Resource<MedicineRequestItem>>(Resource.Idle())
    val createRequestState: StateFlow<Resource<MedicineRequestItem>> = _createRequestState.asStateFlow()

    fun loadMyRequests() {
        viewModelScope.launch {
            requestRepository.getMyRequests().collect {
                _myRequestsState.value = it
            }
        }
    }

    fun submitRequest(medicineId: Int, pharmacyId: Int? = null, qty: Int = 1, notes: String? = null) {
        viewModelScope.launch {
            val req = MedicineRequestCreate(medicineId = medicineId, pharmacyId = pharmacyId, quantityRequested = qty, notes = notes)
            requestRepository.createRequest(req).collect {
                _createRequestState.value = it
                if (it is Resource.Success) {
                    loadMyRequests()
                }
            }
        }
    }

    fun resetCreateState() {
        _createRequestState.value = Resource.Idle()
    }
}
