import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';
import '../engine/tasks.dart';

final overlayInferenceProvider = StateNotifierProvider<InferenceNotifier, String>((ref) {
  return InferenceNotifier();
});

class InferenceNotifier extends StateNotifier<String> {
  InferenceNotifier() : super('');

  void generate(String task, String contextText, String customPrompt) {
    state = 'Waiting...';
    Stream<String> stream;
    
    switch (task) {
      case 'Summarize':
        stream = InferenceTasks.summarize(contextText);
        break;
      case 'Simplify':
        stream = InferenceTasks.simplify(contextText);
        break;
      case 'Explain':
        stream = InferenceTasks.explain(contextText);
        break;
      case 'Custom':
        stream = InferenceTasks.custom(contextText, customPrompt);
        break;
      default:
        stream = Stream.value('Task not supported yet.');
    }

    state = '';
    stream.listen((token) {
      state += token;
    }, onError: (err) {
      state += '\nError: $err';
    });
  }

  void reset() {
    state = '';
  }
}

class OverlayScreen extends ConsumerStatefulWidget {
  const OverlayScreen({super.key});

  @override
  ConsumerState<OverlayScreen> createState() => _OverlayScreenState();
}

class _OverlayScreenState extends ConsumerState<OverlayScreen> {
  String _activeTask = 'Summarize';
  final _customPromptController = TextEditingController();
  final String _mockContextText = 'This is the context text grabbed from the underlying app.';

  final List<String> _tasks = [
    'Summarize', 'Simplify', 'Explain', 'Reply', 'Continue', 'Caption', 'Navigate', 'Custom'
  ];

  @override
  Widget build(BuildContext context) {
    final outputText = ref.watch(overlayInferenceProvider);
    final isGenerating = outputText == 'Waiting...' || (outputText.isNotEmpty && !outputText.endsWith('[DONE]'));

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Align(
        alignment: Alignment.bottomCenter,
        child: Container(
          height: 260,
          width: double.infinity,
          decoration: const BoxDecoration(
            color: Color(0xFF1E1E1E),
            borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
          ),
          child: Column(
            children: [
              // Top Bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Phantom', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white),
                      onPressed: () => SystemNavigator.pop(),
                    ),
                  ],
                ),
              ),
              
              // Task Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  children: _tasks.map((task) {
                    final isVision = task == 'Caption' || task == 'Navigate';
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: ChoiceChip(
                        label: Text(task),
                        selected: _activeTask == task,
                        selectedColor: isVision ? Colors.blue.withOpacity(0.3) : Colors.red.withOpacity(0.3),
                        onSelected: (selected) {
                          if (selected) {
                            setState(() => _activeTask = task);
                          }
                        },
                      ),
                    );
                  }).toList(),
                ),
              ),

              if (_activeTask == 'Custom')
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: TextField(
                    controller: _customPromptController,
                    decoration: const InputDecoration(
                      hintText: 'Enter instruction...',
                      filled: true,
                      fillColor: Colors.black26,
                      border: OutlineInputBorder(borderSide: BorderSide.none),
                      isDense: true,
                    ),
                    style: const TextStyle(color: Colors.white),
                  ),
                ),

              // Output Area
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    outputText.replaceAll('[DONE]', ''),
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ),

              // Bottom Actions
              if (outputText.isNotEmpty && !isGenerating)
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    TextButton.icon(
                      icon: const Icon(Icons.copy),
                      label: const Text('Copy'),
                      onPressed: () {
                        Clipboard.setData(ClipboardData(text: outputText.replaceAll('[DONE]', '')));
                      },
                    ),
                    TextButton.icon(
                      icon: const Icon(Icons.insert_drive_file),
                      label: const Text('Insert'),
                      onPressed: () {
                        const MethodChannel('com.phantom/native').invokeMethod('injectText', {'text': outputText.replaceAll('[DONE]', '')});
                      },
                    ),
                  ],
                )
              else
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: isGenerating
                          ? null
                          : () {
                              ref.read(overlayInferenceProvider.notifier).generate(_activeTask, _mockContextText, _customPromptController.text);
                            },
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFFF4757)),
                      child: Text(isGenerating ? 'Generating...' : 'Generate', style: const TextStyle(color: Colors.white)),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}