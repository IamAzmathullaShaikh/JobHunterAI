package com.jobhunterai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "jobs")
data class JobListingEntity(
    @PrimaryKey val id: Int,
    val title: String,
    val companyName: String,
    val location: String,
    val source: String,
    val url: String,
    val matchScore: Float?,
    val status: String?,
    val dateScraped: String
)
