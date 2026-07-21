# Implementation Plan - Fix Empty Job List and Improve UI Feedback

The app shows an empty list because the network request is likely failing silently. A key reason is that the app uses an `http` URL without enabling cleartext traffic in the manifest. Additionally, the UI lacks loading and error states, making it hard to diagnose issues.

## User Review Required

> [!IMPORTANT]
> I am enabling `android:usesCleartextTraffic="true"` in the `AndroidManifest.xml` to allow the app to connect to the local backend over `http`. If you are using a physical device, you may need to update the `BASE_URL` in `ApiClient.kt` to your computer's local IP address.

## Proposed Changes

### Build & Configuration

#### [MODIFY] [AndroidManifest.xml](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/AndroidManifest.xml)
- Add `android:usesCleartextTraffic="true"` to the `<application>` tag.

### UI & Logic

#### [MODIFY] [MainActivity.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/MainActivity.kt)
- Add a loading state and an error state.
- Add `Log.e` in the `catch` block to help with debugging.
- Pass the loading and error states to the `JobBoardScreen`.

#### [MODIFY] [JobBoardScreen.kt](file:///C:/Users/iamsh/StudioProjects/JobHunterAI/mobile/android/app/src/main/kotlin/com/jobhunterai/ui/screens/JobBoardScreen.kt)
- Update `JobBoardScreen` to handle `isLoading` and `errorMessage`.
- Show a `CircularProgressIndicator` during loading.
- Show an error message and a "Retry" button if the request fails.
- Show an "Empty" message if no jobs are returned.

## Verification Plan

### Automated Tests
- `gradle_sync`: Ensure the project still syncs correctly.
- `gradle_build(":app:assembleDebug")`: Ensure the app builds.

### Manual Verification
- Deploy the app to an emulator.
- Verify that a loading spinner appears.
- Verify that if the backend is down, an error message appears.
- Verify that once the backend is running (and has jobs), they are displayed.
