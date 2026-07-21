package com.jobhunterai.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jobhunterai.data.JobListingEntity
import com.jobhunterai.data.JobRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

import com.jobhunterai.data.JobApplicationEntity
import kotlinx.coroutines.flow.combine

sealed class JobUiState {
    object Loading : JobUiState()
    data class Success(val jobs: List<JobListingEntity>, val applications: List<JobApplicationEntity>) : JobUiState()
    data class Error(val message: String) : JobUiState()
}

class JobViewModel(private val repository: JobRepository) : ViewModel() {

    private val _uiState = MutableStateFlow<JobUiState>(JobUiState.Loading)
    val uiState: StateFlow<JobUiState> = _uiState.asStateFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = JobUiState.Loading
            try {
                repository.refreshJobs()
            } catch (e: Exception) {}

            combine(
                repository.getLocalJobs(),
                repository.getLocalApplications()
            ) { jobs, apps ->
                JobUiState.Success(jobs, apps)
            }.collect { state ->
                _uiState.value = state
            }
        }
    }

    fun loadJobs() = loadData()
}
