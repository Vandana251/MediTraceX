package com.meditracex.app.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.meditracex.app.data.model.InventoryItem
import com.meditracex.app.data.model.InventoryUpdateRequest
import com.meditracex.app.data.repository.InventoryRepository
import com.meditracex.app.utils.Resource
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class InventoryViewModel(private val inventoryRepository: InventoryRepository) : ViewModel() {

    private val _inventoryListState = MutableStateFlow<Resource<List<InventoryItem>>>(Resource.Idle())
    val inventoryListState: StateFlow<Resource<List<InventoryItem>>> = _inventoryListState.asStateFlow()

    private val _updateState = MutableStateFlow<Resource<InventoryItem>>(Resource.Idle())
    val updateState: StateFlow<Resource<InventoryItem>> = _updateState.asStateFlow()

    fun fetchPharmacyInventory(pharmacyId: Int) {
        viewModelScope.launch {
            inventoryRepository.getInventoryByPharmacy(pharmacyId).collect {
                _inventoryListState.value = it
            }
        }
    }

    fun updateStock(inventoryId: Int, newQuantity: Int, safetyThreshold: Int = 15) {
        viewModelScope.launch {
            val req = InventoryUpdateRequest(stockQuantity = newQuantity, safetyStockThreshold = safetyThreshold)
            inventoryRepository.updateStock(inventoryId, req).collect {
                _updateState.value = it
                if (it is Resource.Success) {
                    // Refresh local inventory list item
                    val curList = _inventoryListState.value.data?.toMutableList()
                    if (curList != null) {
                        val idx = curList.indexOfFirst { item -> item.id == inventoryId }
                        if (idx != -1) {
                            curList[idx] = it.data!!
                            _inventoryListState.value = Resource.Success(curList)
                        }
                    }
                }
            }
        }
    }
}
