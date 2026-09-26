package com.meditracex.app.ui.navigation

import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.meditracex.app.ui.screens.auth.LoginScreen
import com.meditracex.app.ui.screens.auth.RegisterScreen
import com.meditracex.app.ui.screens.discovery.NearbyPharmacyScreen
import com.meditracex.app.ui.screens.inventory.PharmacyInventoryScreen
import com.meditracex.app.ui.screens.prediction.DemandPredictionScreen
import com.meditracex.app.ui.screens.requests.MedicineRequestsScreen
import com.meditracex.app.ui.screens.search.MedicineSearchScreen
import com.meditracex.app.ui.screens.watchlist.WatchlistScreen
import com.meditracex.app.ui.viewmodel.*

@Composable
fun MediTraceXNavGraph(
    navController: NavHostController,
    authViewModel: AuthViewModel,
    medicineSearchViewModel: MedicineSearchViewModel,
    pharmacyDiscoveryViewModel: PharmacyDiscoveryViewModel,
    inventoryViewModel: InventoryViewModel,
    predictionViewModel: PredictionViewModel,
    requestViewModel: RequestViewModel,
    watchlistViewModel: WatchlistViewModel
) {
    val token by authViewModel.accessToken.collectAsState()
    val userRole by authViewModel.userRole.collectAsState()
    val userName by authViewModel.userName.collectAsState()

    val startDestination = if (!token.isNullOrBlank()) Screen.Search.route else Screen.Login.route

    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // 1. Auth Flow
        composable(Screen.Login.route) {
            LoginScreen(
                viewModel = authViewModel,
                onNavigateToRegister = { navController.navigate(Screen.Register.route) },
                onLoginSuccess = {
                    navController.navigate(Screen.Search.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Register.route) {
            RegisterScreen(
                viewModel = authViewModel,
                onNavigateToLogin = { navController.popBackStack() },
                onRegisterSuccess = {
                    navController.navigate(Screen.Search.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        // 2. Core Search & Availability Discovery
        composable(Screen.Search.route) {
            MedicineSearchScreen(
                viewModel = medicineSearchViewModel,
                userRole = userRole,
                userName = userName,
                onMedicineSelected = { medicineId, medicineName ->
                    val encodedName = Uri.encode(medicineName)
                    navController.navigate(Screen.Discovery.createRoute(medicineId, encodedName))
                },
                onNavigateToRequests = { navController.navigate(Screen.Requests.route) },
                onNavigateToWatchlist = { navController.navigate(Screen.Watchlist.route) },
                onNavigateToInventory = {
                    navController.navigate(Screen.Inventory.createRoute(1, Uri.encode("MediCare Plus")))
                },
                onLogout = {
                    authViewModel.logout()
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }

        composable(
            route = Screen.Discovery.route,
            arguments = listOf(
                navArgument("medicineId") { type = NavType.IntType },
                navArgument("medicineName") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val medicineId = backStackEntry.arguments?.getInt("medicineId") ?: 1
            val rawName = backStackEntry.arguments?.getString("medicineName") ?: "Medicine"
            val medicineName = Uri.decode(rawName)

            NearbyPharmacyScreen(
                medicineId = medicineId,
                medicineName = medicineName,
                viewModel = pharmacyDiscoveryViewModel,
                watchlistViewModel = watchlistViewModel,
                requestViewModel = requestViewModel,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToPrediction = { pharmacyId, targetMedId ->
                    navController.navigate(Screen.Prediction.createRoute(pharmacyId, targetMedId))
                }
            )
        }

        // 3. ML Demand Prediction Screen
        composable(
            route = Screen.Prediction.route,
            arguments = listOf(
                navArgument("pharmacyId") { type = NavType.IntType },
                navArgument("medicineId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val pharmacyId = backStackEntry.arguments?.getInt("pharmacyId") ?: 1
            val medicineId = backStackEntry.arguments?.getInt("medicineId") ?: 2

            DemandPredictionScreen(
                pharmacyId = pharmacyId,
                medicineId = medicineId,
                viewModel = predictionViewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 4. Pharmacy Inventory Screen
        composable(
            route = Screen.Inventory.route,
            arguments = listOf(
                navArgument("pharmacyId") { type = NavType.IntType },
                navArgument("pharmacyName") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val pharmacyId = backStackEntry.arguments?.getInt("pharmacyId") ?: 1
            val rawName = backStackEntry.arguments?.getString("pharmacyName") ?: "Pharmacy"
            val pharmacyName = Uri.decode(rawName)

            PharmacyInventoryScreen(
                pharmacyId = pharmacyId,
                pharmacyName = pharmacyName,
                viewModel = inventoryViewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 5. Medicine Procurement Requests
        composable(Screen.Requests.route) {
            MedicineRequestsScreen(
                viewModel = requestViewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }

        // 6. Restock Watchlist (Notify Me)
        composable(Screen.Watchlist.route) {
            WatchlistScreen(
                viewModel = watchlistViewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
