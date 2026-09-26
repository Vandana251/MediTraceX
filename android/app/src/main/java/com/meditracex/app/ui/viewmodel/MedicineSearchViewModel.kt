package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.MedicineItem
import com.meditracex.app.data.repository.MedicineRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class MedicineSearchViewModel(private val medicineRepository: MedicineRepository) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _searchResults = MutableStateFlow<Resource<List<MedicineItem>>>(Resource.Success(emptyList()))
    val searchResults: StateFlow<Resource<List<MedicineItem>>> = _searchResults.asStateFlow()

    private var searchJob: Job? = null

    init {
        // Initial popular search on launch
        onSearchQueryChanged("para")
    }

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
        searchJob?.cancel()

        if (query.isBlank()) {
            _searchResults.value = Resource.Success(emptyList())
            return
        }

        searchJob = viewModelScope.launch {
            // Debounce for 250ms
            delay(250)
            medicineRepository.searchMedicines(query.trim(), limit = 20).collect {
                _searchResults.value = it
            }
        }
    }
}
