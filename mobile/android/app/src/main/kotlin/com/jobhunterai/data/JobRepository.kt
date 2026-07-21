package com.jobhunterai.data

import com.jobhunterai.api.JobHunterApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import android.util.Log

class JobRepository(
    private val api: JobHunterApi,
    private val dao: JobDao
) {
    fun getLocalJobs(): Flow<List<JobListingEntity>> = dao.getAllJobs()
    fun getLocalApplications(): Flow<List<JobApplicationEntity>> = dao.getAllApplications()

    suspend fun refreshJobs() {
        try {
            val remoteJobs = api.getJobs()
            // Map remote DTOs to local entities if needed
            // For now assuming api.getJobs() returns List<JobListingEntity> as per previous mock
            dao.insertJobs(remoteJobs)
        } catch (e: Exception) {
            Log.e("JobRepository", "Failed to refresh jobs", e)
            throw e
        }
    }

    suspend fun syncApplications() {
        // Implementation for syncing applications with FastAPI
    }
}
