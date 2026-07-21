package com.jobhunterai.data

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [JobListingEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun jobDao(): JobDao
}
