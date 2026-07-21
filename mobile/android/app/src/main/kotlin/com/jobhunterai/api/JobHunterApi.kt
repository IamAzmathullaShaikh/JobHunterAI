package com.jobhunterai.api

import com.jobhunterai.data.JobListingEntity
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface JobHunterApi {
    @GET("api/jobs")
    suspend fun getJobs(): List<JobListingEntity> // Simplified for mapping

    @POST("api/jobs/scrape")
    suspend fun scrapeJobs(@Body payload: Map<String, String>): Any
}
