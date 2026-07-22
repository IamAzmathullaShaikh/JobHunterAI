package com.jobhunterai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "user_profile")
data class UserProfileEntity(
    @PrimaryKey val id: Int = 1, // Single user mode
    val fullName: String?,
    val totalExperienceYears: Float?,
    val rawResumeText: String?,
    val keySkills: String?, // Store as comma-separated or JSON string
    val updatedAt: String
)
