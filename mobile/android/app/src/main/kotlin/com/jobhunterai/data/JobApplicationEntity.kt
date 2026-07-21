package com.jobhunterai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "job_applications")
data class JobApplicationEntity(
    @PrimaryKey val id: Int,
    val jobTitle: String,
    val companyName: String,
    val status: String,
    val matchScore: Float,
    val platform: String,
    val appliedDate: String?,
    val notes: String?
)
