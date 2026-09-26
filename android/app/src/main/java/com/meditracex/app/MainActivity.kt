package com.meditracex.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.compose.rememberNavController
import com.meditracex.app.ui.navigation.MediTraceXNavGraph
import com.meditracex.app.ui.theme.BackgroundLight
import com.meditracex.app.ui.theme.MediTraceXTheme
import com.meditracex.app.ui.viewmodel.*

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = application as MediTraceXApp

        val authViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { AuthViewModel(app.authRepository) }
        )[AuthViewModel::class.java]

        val medicineSearchViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { MedicineSearchViewModel(app.medicineRepository) }
        )[MedicineSearchViewModel::class.java]

        val pharmacyDiscoveryViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { PharmacyDiscoveryViewModel(app.pharmacyRepository) }
        )[PharmacyDiscoveryViewModel::class.java]

        val inventoryViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { InventoryViewModel(app.inventoryRepository) }
        )[InventoryViewModel::class.java]

        val predictionViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { PredictionViewModel(app.predictionRepository) }
        )[PredictionViewModel::class.java]

        val requestViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { RequestViewModel(app.requestRepository) }
        )[RequestViewModel::class.java]

        val watchlistViewModel = ViewModelProvider(
            this,
            GenericViewModelFactory { WatchlistViewModel(app.watchlistRepository) }
        )[WatchlistViewModel::class.java]

        setContent {
            MediTraceXTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = BackgroundLight
                ) {
                    val navController = rememberNavController()
                    MediTraceXNavGraph(
                        navController = navController,
                        authViewModel = authViewModel,
                        medicineSearchViewModel = medicineSearchViewModel,
                        pharmacyDiscoveryViewModel = pharmacyDiscoveryViewModel,
                        inventoryViewModel = inventoryViewModel,
                        predictionViewModel = predictionViewModel,
                        requestViewModel = requestViewModel,
                        watchlistViewModel = watchlistViewModel
                    )
                }
            }
        }
    }
}

class GenericViewModelFactory<T : ViewModel>(
    private val creator: () -> T
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <VM : ViewModel> create(modelClass: Class<VM>): VM {
        return creator() as VM
    }
}
