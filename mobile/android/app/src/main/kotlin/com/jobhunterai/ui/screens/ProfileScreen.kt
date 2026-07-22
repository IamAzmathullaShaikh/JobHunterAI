package com.jobhunterai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen() {
    var resumeText by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Candidate Profile", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            Text("Shared Resume (Sync with Web Pro)", style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(
                value = resumeText,
                onValueChange = { resumeText = it },
                modifier = Modifier.fillMaxWidth().weight(1f),
                label = { Text("Resume Content") }
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(
                onClick = { /* Sync logic */ },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Update Global Profile")
            }
        }
    }
}
