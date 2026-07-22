package com.jobhunterai.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Assignment
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Jobs : Screen("jobs", "Jobs", Icons.Default.List)
    object ATS : Screen("ats", "ATS Matcher", Icons.Default.Assignment)
    object Prep : Screen("prep", "Prep", Icons.Default.Description)
    object Profile : Screen("profile", "Profile", Icons.Default.Person)
}
