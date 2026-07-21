package com.jobhunterai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.jobhunterai.api.ApiClient
import com.jobhunterai.data.DatabaseProvider
import com.jobhunterai.data.JobRepository
import com.jobhunterai.ui.JobViewModel
import com.jobhunterai.ui.screens.JobBoardScreen
import com.jobhunterai.ui.theme.JobHunterAITheme

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.Box
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Briefcase
import androidx.compose.material.icons.filled.ListAlt
import androidx.compose.material3.*
import androidx.compose.runtime.getValue
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController

class MainActivity : ComponentActivity() {

    private val viewModel: JobViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                val database = DatabaseProvider.getDatabase(applicationContext)
                val repository = JobRepository(ApiClient.instance, database.jobDao())
                return JobViewModel(repository) as T
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val uiState by viewModel.uiState.collectAsState()
            val navController = rememberNavController()

            JobHunterAITheme {
                Scaffold(
                    bottomBar = {
                        NavigationBar {
                            val navBackStackEntry by navController.currentBackStackEntryAsState()
                            val currentRoute = navBackStackEntry?.destination?.route

                            NavigationBarItem(
                                icon = { Icon(Icons.Default.Briefcase, contentDescription = null) },
                                label = { Text("Jobs") },
                                selected = currentRoute == "jobs",
                                onClick = {
                                    navController.navigate("jobs") {
                                        popUpTo(navController.graph.startDestinationId)
                                        launchSingleTop = true
                                    }
                                }
                            )
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.ListAlt, contentDescription = null) },
                                label = { Text("Tracker") },
                                selected = currentRoute == "tracker",
                                onClick = {
                                    navController.navigate("tracker") {
                                        popUpTo(navController.graph.startDestinationId)
                                        launchSingleTop = true
                                    }
                                }
                            )
                        }
                    }
                ) { padding ->
                    NavHost(navController, startDestination = "jobs", modifier = Modifier.padding(padding)) {
                        composable("jobs") {
                            JobBoardScreen(
                                uiState = uiState,
                                onRetry = { viewModel.loadData() }
                            )
                        }
                        composable("tracker") {
                            if (uiState is JobUiState.Success) {
                                TrackerScreen(applications = (uiState as JobUiState.Success).applications)
                            } else {
                                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                    CircularProgressIndicator()
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
