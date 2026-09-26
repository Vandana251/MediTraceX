package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.WatchlistItem
import com.meditracex.app.data.repository.WatchlistRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class WatchlistViewModel(private val watchlistRepository: WatchlistRepository) : ViewModel() {

    private val _watchlistState = MutableStateFlow<Resource<List<WatchlistItem>>>(Resource.Idle())
    val watchlistState: StateFlow<Resource<List<WatchlistItem>>> = _watchlistState.asStateFlow()

    private val _actionState = MutableStateFlow<Resource<String>>(Resource.Idle())
    val actionState: StateFlow<Resource<String>> = _actionState.asStateFlow()

    fun loadWatchlist() {
        viewModelScope.launch {
            watchlistRepository.getMyWatchlist().collect {
                _watchlistState.value = it
            }
        }
    }

    fun addToWatchlist(medicineId: Int, pharmacyId: Int? = null) {
        viewModelScope.launch {
            watchlistRepository.addToWatchlist(medicineId, pharmacyId).collect {
                when (it) {
                    is Resource.Loading -> _actionState.value = Resource.Loading()
                    is Resource.Success -> {
                        _actionState.value = Resource.Success("Added to Restock Watchlist (Notify Me)")
                        loadWatchlist()
                    }
                    is Resource.Error -> _actionState.value = Resource.Error(it.message ?: "Failed")
                    is Resource.Idle -> _actionState.value = Resource.Idle()
                }
            }
        }
    }

    fun removeItem(watchlistId: Int) {
        viewModelScope.launch {
            watchlistRepository.removeFromWatchlist(watchlistId).collect {
                if (it is Resource.Success) {
                    loadWatchlist()
                }
            }
        }
    }

    fun resetActionState() {
        _actionState.value = Resource.Idle()
    }
}
