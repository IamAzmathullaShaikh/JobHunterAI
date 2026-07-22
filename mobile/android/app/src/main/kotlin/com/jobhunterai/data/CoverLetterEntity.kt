package com.jobhunterai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "cover_letters")
data class CoverLetterEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val jobId: Int,
    val content: String,
    val createdAt: String
)
