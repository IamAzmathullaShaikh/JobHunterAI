package com.jobhunterai.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface JobDao {
    @Query("SELECT * FROM jobs ORDER BY dateScraped DESC")
    fun getAllJobs(): Flow<List<JobListingEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertJobs(jobs: List<JobListingEntity>)

    @Query("DELETE FROM jobs")
    suspend fun deleteAll()
}
