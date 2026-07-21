package com.jobhunterai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.jobhunterai.data.JobListingEntity

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JobBoardScreen(jobs: List<JobListingEntity>) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Discovered Jobs") })
        }
    ) { padding ->
        LazyColumn(
            contentPadding = padding,
            modifier = Modifier.fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(jobs) { job ->
                JobCard(job)
            }
        }
    }
}

@Composable
fun JobCard(job: JobListingEntity) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = job.title, style = MaterialTheme.typography.titleMedium)
            Text(text = job.companyName, style = MaterialTheme.typography.bodySmall)
            Spacer(modifier = Modifier.height(8.dp))
            job.matchScore?.let {
                LinearProgressIndicator(
                    progress = it / 100f,
                    modifier = Modifier.fillMaxWidth()
                )
                Text(text = "Match: ${it.toInt()}%", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
