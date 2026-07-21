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

    suspend fun refreshJobs() {
        try {
            val remoteJobs = api.getJobs()
            if (remoteJobs.isNotEmpty()) {
                dao.deleteAll()
                dao.insertJobs(remoteJobs)
            }
        } catch (e: Exception) {
            Log.e("JobRepository", "Failed to refresh jobs", e)
            throw e
        }
    }
}
