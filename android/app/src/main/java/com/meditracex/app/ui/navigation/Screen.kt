package com.meditracex.app.ui.navigation

sealed class Screen(val route: String, val title: String) {
    object Login : Screen("login", "Sign In")
    object Register : Screen("register", "Create Account")
    object Search : Screen("search", "Medicine Search")
    object Discovery : Screen("discovery/{medicineId}/{medicineName}", "Nearby Pharmacies") {
        fun createRoute(medicineId: Int, medicineName: String) = "discovery/$medicineId/$medicineName"
    }
    object Inventory : Screen("inventory/{pharmacyId}/{pharmacyName}", "Pharmacy Inventory") {
        fun createRoute(pharmacyId: Int, pharmacyName: String) = "inventory/$pharmacyId/$pharmacyName"
    }
    object Prediction : Screen("prediction/{pharmacyId}/{medicineId}", "Demand Forecast") {
        fun createRoute(pharmacyId: Int, medicineId: Int) = "prediction/$pharmacyId/$medicineId"
    }
    object Requests : Screen("requests", "Medicine Requests")
    object Watchlist : Screen("watchlist", "Restock Watchlist")
}
