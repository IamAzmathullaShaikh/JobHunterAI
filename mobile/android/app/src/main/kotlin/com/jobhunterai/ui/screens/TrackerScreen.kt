package com.jobhunterai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.jobhunterai.data.JobApplicationEntity

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrackerScreen(applications: List<JobApplicationEntity>) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Application CRM", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(applications) { app ->
                ApplicationCard(app)
            }
        }
    }
}

@Composable
fun ApplicationCard(app: JobApplicationEntity) {
    ElevatedCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(app.jobTitle, style = MaterialTheme.typography.titleMedium)
            Text(app.companyName, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                SuggestionChip(onClick = {}, label = { Text(app.status) })
                Text("${app.matchScore.toInt()}% Match", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
