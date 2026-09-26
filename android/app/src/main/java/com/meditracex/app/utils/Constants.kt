package com.meditracex.app.utils

object Constants {
    // Android Emulator loopback to host machine
    const val EMULATOR_BASE_URL = "http://10.0.2.2:8000/"
    // Physical device / localhost fallback
    const val LOCALHOST_BASE_URL = "http://127.0.0.1:8000/"
    
    // Active base URL for Network Client
    const val BASE_URL = EMULATOR_BASE_URL

    const val APP_TAGLINE = "Find. Verify. Reach."
    
    // Default search coordinates (Hyderabad Metro Test Location)
    const val DEFAULT_LATITUDE = 17.4435
    const val DEFAULT_LONGITUDE = 78.3780
    const val DEFAULT_SEARCH_RADIUS_KM = 20.0
}
