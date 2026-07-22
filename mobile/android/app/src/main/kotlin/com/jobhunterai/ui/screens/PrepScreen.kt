package com.jobhunterai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PrepScreen() {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Interview Prep Q&A", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                PrepCard("Behavioral", "STAR method responses for common culture-fit questions.")
            }
            item {
                PrepCard("Technical", "Deep dives into stack-specific concepts and DSA.")
            }
        }
    }
}

@Composable
fun PrepCard(title: String, description: String) {
    ElevatedCard(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
            Text(text = description, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = { /* Navigate to detail */ }) {
                Text("Practice Now")
            }
        }
    }
}
