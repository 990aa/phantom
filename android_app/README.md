# Phantom Android App

A Flutter-based mobile application that provides system-wide AI assistance on Android.

## Purposes
- **Context Awareness**: Uses an Accessibility Service to read text from other apps (like WhatsApp).
- **Native Inference**: Runs `llama.cpp` directly on the device via JNI/Dart FFI.
- **Overlay UI**: Provides a floating bottom-sheet interface that appears over any application.
- **Background Tasks**: Periodically distills writing style when the device is idle and charging.

## Implementation Details
- **`lib/main.dart`**: Entry point and MethodChannel handler for native-to-dart communication.
- **`lib/engine/llama_ffi.dart`**: Dart FFI bindings for the native C++ inference engine.
- **`lib/screens/overlay_screen.dart`**: The interactive AI panel that renders in a system overlay window.
- **`android/app/src/main/cpp/phantom_jni.cpp`**: JNI bridge for `llama.cpp`.
- **`android/app/src/main/kotlin/com/phantom/phantom_android/PhantomAccessibilityService.kt`**: Reads UI nodes and injects generated text back into fields.

## Run / Build Instructions

### Prerequisites
- Flutter SDK (Stable)
- Android SDK & NDK (26.1.10909125)
- CMake 3.22.1+

### Development
1. `cd android_app`
2. `flutter pub get`
3. Connect an Android device (arm64-v8a or x86_64)
4. `flutter run`

### Build (Release APK)
```bash
flutter build apk --release
```
The APK is located at `build/app/outputs/flutter-apk/app-release.apk`.

## Post-Install Setup
After installing the APK, you MUST manually grant these permissions in Android Settings:
1. **Accessibility**: Enable "Phantom" to allow context reading and text injection.
2. **Display over other apps**: Allow "Phantom" to show the floating overlay.

## Testing
- **Unit/Widget Tests**: `flutter test`
- **Integration Tests**: `flutter test integration_test/` (requires device)
