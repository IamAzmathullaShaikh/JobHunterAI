package com.jobhunterai.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jobhunterai.data.JobListingEntity
import com.jobhunterai.data.JobRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class JobUiState {
    object Loading : JobUiState()
    data class Success(val jobs: List<JobListingEntity>) : JobUiState()
    data class Error(val message: String) : JobUiState()
}

class JobViewModel(private val repository: JobRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<JobUiState>(JobUiState.Loading)
    val uiState: StateFlow<JobUiState> = _uiState.asStateFlow()

    init {
        loadJobs()
    }

    fun loadJobs() {
        viewModelScope.launch {
            _uiState.value = JobUiState.Loading
            try {
                // First try to refresh from API
                repository.refreshJobs()
            } catch (e: Exception) {
                // If API fails, we still have local data (handled by flow)
                // but we might want to show an error message if local is also empty
            }

            // Observe local database
            repository.getLocalJobs().collect { jobs ->
                if (jobs.isEmpty()) {
                    _uiState.value = JobUiState.Error("No jobs found. Please try again later.")
                } else {
                    _uiState.value = JobUiState.Success(jobs)
                }
            }
        }
    }
}
