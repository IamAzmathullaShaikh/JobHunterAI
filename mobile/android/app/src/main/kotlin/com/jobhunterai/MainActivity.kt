package com.jobhunterai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.jobhunterai.ui.theme.JobHunterAITheme

import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import com.jobhunterai.api.ApiClient
import com.jobhunterai.data.JobListingEntity
import com.jobhunterai.ui.screens.JobBoardScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val jobsState = remember { mutableStateOf<List<JobListingEntity>>(emptyList()) }

            LaunchedEffect(Unit) {
                try {
                    jobsState.value = ApiClient.instance.getJobs()
                } catch (e: Exception) {
                    // Handle error
                }
            }

            JobHunterAITheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    JobBoardScreen(jobs = jobsState.value)
                }
            }
        }
    }
}
