package com.jobhunterai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "job_applications")
data class JobApplicationEntity(
    @PrimaryKey val id: Int,
    val jobId: Int,
    val status: String, // Identified, Applied, etc.
    val notes: String?,
    val dateCreated: String,
    val dateUpdated: String
)
