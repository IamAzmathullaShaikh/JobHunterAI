package com.jobhunterai.data

import android.util.Log
import com.jobhunterai.api.JobHunterApi
import kotlinx.coroutines.flow.Flow

class JobRepository(
    private val api: JobHunterApi,
    private val dao: JobDao
) {
    fun getLocalJobs(): Flow<List<JobListingEntity>> = dao.getAllJobs()

    suspend fun refreshJobs() {
        try {
            val remoteJobs = api.getJobs()
            if (remoteJobs.isNotEmpty()) {
                dao.deleteAll()
                dao.insertJobs(remoteJobs)
            }
        } catch (e: Exception) {
            Log.e("JobRepository", "Failed to refresh jobs from API", e)
            throw e
        }
    }
}
