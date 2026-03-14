import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';
import 'dart:async';
import 'dart:isolate';

typedef PhantomLoadModelC = Int64 Function(Pointer<Utf8> modelPath);
typedef PhantomLoadModelDart = int Function(Pointer<Utf8> modelPath);

typedef NativeCallback = Void Function(Pointer<Utf8> token);

typedef PhantomRunInferenceC =
    Void Function(
      Int64 ctx,
      Pointer<Utf8> prompt,
      Pointer<NativeFunction<NativeCallback>> callback,
    );
typedef PhantomRunInferenceDart =
    void Function(
      int ctx,
      Pointer<Utf8> prompt,
      Pointer<NativeFunction<NativeCallback>> callback,
    );

typedef PhantomRunVisionInferenceC =
    Void Function(
      Int64 ctx,
      Pointer<Utf8> imagePath,
      Pointer<Utf8> prompt,
      Pointer<NativeFunction<NativeCallback>> callback,
    );
typedef PhantomRunVisionInferenceDart =
    void Function(
      int ctx,
      Pointer<Utf8> imagePath,
      Pointer<Utf8> prompt,
      Pointer<NativeFunction<NativeCallback>> callback,
    );

typedef PhantomUnloadModelC = Void Function(Int64 ctx);
typedef PhantomUnloadModelDart = void Function(int ctx);

class LlamaEngine {
  late DynamicLibrary _lib;
  late PhantomLoadModelDart _loadModel;
  late PhantomRunInferenceDart _runInference;
  late PhantomRunVisionInferenceDart _runVisionInference;
  late PhantomUnloadModelDart _unloadModel;

  int _ctx = 0;

  static SendPort? _sendPort;

  LlamaEngine() {
    _lib = Platform.isAndroid
        ? DynamicLibrary.open('libphantom_llama.so')
        : DynamicLibrary.process();

    _loadModel = _lib.lookupFunction<PhantomLoadModelC, PhantomLoadModelDart>(
      'phantom_load_model',
    );
    _runInference = _lib
        .lookupFunction<PhantomRunInferenceC, PhantomRunInferenceDart>(
          'phantom_run_inference',
        );
    _runVisionInference = _lib
        .lookupFunction<
          PhantomRunVisionInferenceC,
          PhantomRunVisionInferenceDart
        >('phantom_run_vision_inference');
    _unloadModel = _lib
        .lookupFunction<PhantomUnloadModelC, PhantomUnloadModelDart>(
          'phantom_unload_model',
        );
  }

  void load(String modelPath) {
    if (_ctx != 0) unload();
    final pathPtr = modelPath.toNativeUtf8();
    _ctx = _loadModel(pathPtr);
    calloc.free(pathPtr);
  }

  Stream<String> generate(String prompt) {
    final controller = StreamController<String>();

    final receivePort = ReceivePort();
    _sendPort = receivePort.sendPort;

    receivePort.listen((message) {
      final token = message as String;
      if (token == '[DONE]') {
        controller.close();
        receivePort.close();
      } else {
        controller.add(token);
      }
    });

    // In a real app, we'd use Isolate.spawn to avoid blocking the UI thread
    // during C++ inference if it's synchronous. For this stub, we call it.
    final promptPtr = prompt.toNativeUtf8();
    _runInference(
      _ctx,
      promptPtr,
      Pointer.fromFunction<NativeCallback>(_nativeCallback),
    );
    calloc.free(promptPtr);

    return controller.stream;
  }

  Stream<String> generateVision(String imagePath, String prompt) {
    final controller = StreamController<String>();

    final receivePort = ReceivePort();
    _sendPort = receivePort.sendPort;

    receivePort.listen((message) {
      final token = message as String;
      if (token == '[DONE]') {
        controller.close();
        receivePort.close();
      } else {
        controller.add(token);
      }
    });

    final promptPtr = prompt.toNativeUtf8();
    final imagePtr = imagePath.toNativeUtf8();
    _runVisionInference(
      _ctx,
      imagePtr,
      promptPtr,
      Pointer.fromFunction<NativeCallback>(_nativeCallback),
    );
    calloc.free(promptPtr);
    calloc.free(imagePtr);

    return controller.stream;
  }

  void unload() {
    if (_ctx != 0) {
      _unloadModel(_ctx);
      _ctx = 0;
    }
  }

  static void _nativeCallback(Pointer<Utf8> tokenPtr) {
    final token = tokenPtr.toDartString();
    _sendPort?.send(token);
  }
}
