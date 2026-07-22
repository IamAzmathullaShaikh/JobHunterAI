package com.jobhunterai.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.jobhunterai.ui.JobViewModel
import com.jobhunterai.ui.screens.ATSScreen
import com.jobhunterai.ui.screens.JobBoardScreen
import com.jobhunterai.ui.screens.PrepScreen
import com.jobhunterai.ui.screens.ProfileScreen
import androidx.compose.runtime.collectAsState

@Composable
fun MainNavigation(viewModel: JobViewModel) {
    val navController = rememberNavController()
    val screens = listOf(Screen.Jobs, Screen.ATS, Screen.Prep, Screen.Profile)

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                screens.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = null) },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Jobs.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Jobs.route) {
                val uiState by viewModel.uiState.collectAsState()
                JobBoardScreen(
                    uiState = uiState,
                    onRetry = { viewModel.loadJobs() }
                )
            }
            composable(Screen.ATS.route) { ATSScreen() }
            composable(Screen.Prep.route) { PrepScreen() }
            composable(Screen.Profile.route) { ProfileScreen() }
        }
    }
}
