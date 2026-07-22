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
                repository.refreshJobs()
            } catch (e: Exception) {
                // Network error, but we'll try to show local data if available
            }

            repository.getLocalJobs().collect { jobs ->
                if (jobs.isEmpty()) {
                    _uiState.value = JobUiState.Error("No jobs found. Check your connection.")
                } else {
                    _uiState.value = JobUiState.Success(jobs)
                }
            }
        }
    }
}
