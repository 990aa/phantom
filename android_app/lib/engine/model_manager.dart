import 'dart:async';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart';
import 'package:dio/dio.dart';
import '../db.dart';
import 'llama_ffi.dart';

class ModelManager {
  static final ModelManager instance = ModelManager._init();
  late LlamaEngine _engine;
  final Dio _dio = Dio();

  ModelManager._init() {
    _engine = LlamaEngine();
  }

  Future<Map<String, dynamic>?> resolveModel(String task) async {
    final db = await DatabaseHelper.instance.database;
    final isVision = task == 'caption' || task == 'navigate';
    final queryCol = isVision ? 'is_default_vision' : 'is_default_text';

    // In a full implementation, we'd also check per-task overrides in SharedPreferences.
    final result = await db.query(
      'models',
      where: '$queryCol = ?',
      whereArgs: [1],
      limit: 1,
    );

    if (result.isNotEmpty) return result.first;
    return null; // No default model found
  }

  Stream<String> runInference(
    String task,
    String prompt, {
    String? imagePath,
  }) async* {
    final modelData = await resolveModel(task);
    if (modelData == null) {
      yield "Error: No default model configured for this task.";
      return;
    }

    final docsDir = await getApplicationDocumentsDirectory();
    final modelPath = join(
      docsDir.path,
      '.phantom',
      'models',
      modelData['filename'] as String,
    );

    if (!File(modelPath).existsSync()) {
      yield "Error: Model file not found on disk. Please download it from Settings.";
      return;
    }

    _engine.load(modelPath);

    if (imagePath != null) {
      yield* _engine.generateVision(imagePath, prompt);
    } else {
      yield* _engine.generate(prompt);
    }
  }

  Stream<double> downloadModel(
    String modelId,
    String hfRepo,
    String filename,
  ) async* {
    final docsDir = await getApplicationDocumentsDirectory();
    final modelsDir = Directory(join(docsDir.path, '.phantom', 'models'));
    if (!await modelsDir.exists()) {
      await modelsDir.create(recursive: true);
    }

    final savePath = join(modelsDir.path, filename);
    final url = 'https://huggingface.co/$hfRepo/resolve/main/$filename';

    final controller = StreamController<double>();

    try {
      await _dio.download(
        url,
        savePath,
        onReceiveProgress: (received, total) {
          if (total != -1) {
            controller.add(received / total);
          }
        },
      );

      final db = await DatabaseHelper.instance.database;
      await db.insert('models', {
        'model_id': modelId,
        'hf_repo': hfRepo,
        'filename': filename,
        'is_downloaded': 1,
        'is_default_text': 0,
        'is_default_vision': 0,
      });

      controller.close();
    } catch (e) {
      controller.addError(e);
      controller.close();
    }

    yield* controller.stream;
  }
}
