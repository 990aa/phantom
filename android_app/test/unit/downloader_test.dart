import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Download URL parsing logic', () {
    final url = 'https://huggingface.co/unsloth/Qwen3.5-0.8B-GGUF/resolve/main/qwen3.5-0.8b-q4_k_m.gguf';
    final parts = url.split('/');
    final filename = parts.last;
    final repoIdx = parts.indexOf('huggingface.co') + 1;
    final hfRepo = parts[repoIdx] + '/' + parts[repoIdx + 1];
    
    expect(filename, 'qwen3.5-0.8b-q4_k_m.gguf');
    expect(hfRepo, 'unsloth/Qwen3.5-0.8B-GGUF');
  });
}