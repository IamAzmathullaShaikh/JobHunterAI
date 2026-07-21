package com.jobhunterai.data

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [JobListingEntity::class, JobApplicationEntity::class], version = 2)
abstract class AppDatabase : RoomDatabase() {
    abstract fun jobDao(): JobDao
}
