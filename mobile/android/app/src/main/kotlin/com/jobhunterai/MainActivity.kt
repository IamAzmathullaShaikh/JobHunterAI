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

            JobHunterAITheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    JobBoardScreen(
                        uiState = uiState,
                        onRetry = { viewModel.loadJobs() }
                    )
                }
            }
        }
    }
}
