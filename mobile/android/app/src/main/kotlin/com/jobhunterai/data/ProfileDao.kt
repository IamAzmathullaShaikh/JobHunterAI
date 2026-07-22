package com.jobhunterai.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface ProfileDao {
    @Query("SELECT * FROM user_profile WHERE id = 1")
    fun getProfile(): Flow<UserProfileEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun updateProfile(profile: UserProfileEntity)

    @Query("SELECT * FROM cover_letters WHERE jobId = :jobId")
    suspend fun getCoverLetterForJob(jobId: Int): CoverLetterEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCoverLetter(coverLetter: CoverLetterEntity)
}
