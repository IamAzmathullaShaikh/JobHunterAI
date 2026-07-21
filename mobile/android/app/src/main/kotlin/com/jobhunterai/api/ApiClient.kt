package com.jobhunterai.api

import retrofit2.Retrofit
import retrofit2.converter.gson:GsonConverterFactory

object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:8000/" // Default for Android Emulator

    val instance: JobHunterApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(JobHunterApi::class.java)
    }
}
