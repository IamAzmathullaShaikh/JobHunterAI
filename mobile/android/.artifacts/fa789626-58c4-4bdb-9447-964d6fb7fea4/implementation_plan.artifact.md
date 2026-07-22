# Implementation Plan - Fix Missing Job Listings & UI Enhancement

The app currently shows an empty list without any feedback. This is likely due to a silent network error or a missing data binding layer. I will implement a robust architecture using the Repository/ViewModel pattern to handle data fetching, local caching, and UI states.

## User Review Required

> [!IMPORTANT]
> **Network Connectivity**: If you are testing on a **physical device** (not an emulator), you must change the `BASE_URL` in `ApiClient.kt` from `10.0.2.2` to your computer's local IP address (e.g., `192.168.1.x`).

## Proposed Changes

### 1. Data & Logic Layer (Architecture)

#### [NEW] [JobRepository.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/data/JobRepository.kt)
- Implements coordination between API and Room database.
- Provides a fallback to local cache if the network request fails.

#### [NEW] [DatabaseProvider.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/data/DatabaseProvider.kt)
- Singleton provider for the Room database.

#### [NEW] [JobViewModel.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/ui/JobViewModel.kt)
- Manages `JobUiState`: `Loading`, `Success`, and `Error`.
- Handles data fetching logic and exposes it to the UI.

### 2. UI Layer (Feedback & Styling)

#### [MODIFY] [JobBoardScreen.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/ui/screens/JobBoardScreen.kt)
- Support `JobUiState` to show a **Loading Spinner** or **Error Message** with a "Retry" button.
- Redesign `JobCard` with modern Material 3 styling (ElevatedCard, Better Typography).

#### [MODIFY] [MainActivity.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/MainActivity.kt)
- Integrate `JobViewModel` and observe states.

## Verification Plan

### Automated Tests
- `gradle_build(":app:assembleDebug")`: Ensure the project compiles with the new architecture.

### Manual Verification
- Verify the **Loading Spinner** appears on startup.
- Verify that jobs are displayed once fetched.
- Verify that an **Error Message** appears if the backend is unreachable.
