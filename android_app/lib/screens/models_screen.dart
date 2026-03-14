import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../db.dart';
import '../engine/model_manager.dart';
import 'dart:io';

final modelListProvider = FutureProvider<List<Map<String, dynamic>>>((
  ref,
) async {
  final db = await DatabaseHelper.instance.database;
  return await db.query('models');
});

class ModelsScreen extends ConsumerStatefulWidget {
  const ModelsScreen({super.key});

  @override
  ConsumerState<ModelsScreen> createState() => _ModelsScreenState();
}

class _ModelsScreenState extends ConsumerState<ModelsScreen> {
  bool _isDownloading = false;
  double _downloadProgress = 0.0;

  final _nameController = TextEditingController();
  final _urlController = TextEditingController();
  String _selectedType = 'text';

  void _downloadCustomModel() {
    final url = _urlController.text;
    final name = _nameController.text;
    if (!url.endsWith('.gguf') || !url.contains('huggingface.co')) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid HuggingFace GGUF URL')),
      );
      return;
    }

    // Parse repo and filename from url
    // https://huggingface.co/repo/id/resolve/main/filename.gguf
    try {
      final parts = url.split('/');
      final filename = parts.last;
      final repoIdx = parts.indexOf('huggingface.co') + 1;
      final hfRepo = '${parts[repoIdx]}/${parts[repoIdx + 1]}';

      setState(() {
        _isDownloading = true;
        _downloadProgress = 0.0;
      });

      ModelManager.instance
          .downloadModel(name, hfRepo, filename)
          .listen(
            (progress) {
              setState(() {
                _downloadProgress = progress;
              });
            },
            onDone: () {
              setState(() {
                _isDownloading = false;
              });
              ref.refresh(modelListProvider);
            },
            onError: (err) {
              setState(() {
                _isDownloading = false;
              });
              ScaffoldMessenger.of(
                context,
              ).showSnackBar(SnackBar(content: Text('Download failed: $err')));
            },
          );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Could not parse URL')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final modelsAsyncValue = ref.watch(modelListProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Models')),
      body: Column(
        children: [
          // RAM Warning
          Container(
            padding: const EdgeInsets.all(8),
            color: Colors.orange.withOpacity(0.2),
            child: const Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Device RAM check: Use models < 2GB if you have limited RAM.',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ),
          ),

          if (_isDownloading) LinearProgressIndicator(value: _downloadProgress),

          Expanded(
            child: modelsAsyncValue.when(
              data: (models) {
                if (models.isEmpty) {
                  return const Center(child: Text('No models found.'));
                }
                return ListView.builder(
                  itemCount: models.length,
                  itemBuilder: (context, index) {
                    final model = models[index];
                    return Card(
                      margin: const EdgeInsets.all(8),
                      child: ListTile(
                        title: Text(model['filename']),
                        subtitle: Text(model['hf_repo']),
                        trailing: model['is_downloaded'] == 1
                            ? const Icon(
                                Icons.check_circle,
                                color: Colors.green,
                              )
                            : const Icon(Icons.download),
                      ),
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => Center(child: Text('Error: $err')),
            ),
          ),

          ExpansionTile(
            title: const Text('Add Custom GGUF'),
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    TextField(
                      controller: _nameController,
                      decoration: const InputDecoration(
                        labelText: 'Model Name',
                      ),
                    ),
                    TextField(
                      controller: _urlController,
                      decoration: const InputDecoration(
                        labelText: 'HuggingFace GGUF URL',
                      ),
                    ),
                    DropdownButton<String>(
                      value: _selectedType,
                      items: const [
                        DropdownMenuItem(value: 'text', child: Text('Text')),
                        DropdownMenuItem(
                          value: 'vision',
                          child: Text('Vision'),
                        ),
                      ],
                      onChanged: (val) => setState(() {
                        _selectedType = val!;
                      }),
                    ),
                    ElevatedButton(
                      onPressed: _isDownloading ? null : _downloadCustomModel,
                      child: const Text('Add & Download'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
