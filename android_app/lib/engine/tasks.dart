import 'model_manager.dart';

class InferenceTasks {
  static String _trimContext(String text, {int maxTokens = 800}) {
    final lines = text.split('\n');
    final List<String> trimmedLines = [];
    int currentTokens = 0;
    
    for (var i = lines.length - 1; i >= 0; i--) {
      final line = lines[i];
      final tokens = line.length ~/ 4;
      if (currentTokens + tokens > maxTokens) break;
      trimmedLines.insert(0, line);
      currentTokens += tokens;
    }
    
    return trimmedLines.join('\n');
  }

  static Stream<String> summarize(String text) {
    final prompt =
        "System: Produce a concise 3-sentence summary of the following text.\nUser: $text\nAssistant:";
    return ModelManager.instance.runInference('summarize', prompt);
  }

  static Stream<String> simplify(String text) {
    final prompt =
        "System: Rewrite the following text in simpler, plain language.\nUser: $text\nAssistant:";
    return ModelManager.instance.runInference('simplify', prompt);
  }

  static Stream<String> explain(String text) {
    final prompt =
        "System: Clearly explain the following text.\nUser: $text\nAssistant:";
    return ModelManager.instance.runInference('explain', prompt);
  }

  static Stream<String> custom(String text, String customPrompt) {
    final prompt = "System: $customPrompt\nUser: $text\nAssistant:";
    return ModelManager.instance.runInference('custom', prompt);
  }

  static Stream<String> reply(String contextMessages, String styleRules) {
    final trimmedContext = _trimContext(contextMessages);
    final prompt =
        "System: $styleRules\nUser: Respond to this conversation:\n$trimmedContext\nAssistant:";
    return ModelManager.instance.runInference('reply', prompt);
  }

  static Stream<String> continueText(String text, String styleRules) {
    final prompt =
        "System: $styleRules\nUser: Continue writing the following text:\n$text\nAssistant:";
    return ModelManager.instance.runInference('continue', prompt);
  }

  static Stream<String> caption(String imagePath) {
    final prompt = "System: Provide a short caption for the image.\nAssistant:";
    return ModelManager.instance.runInference(
      'caption',
      prompt,
      imagePath: imagePath,
    );
  }

  static Stream<String> navigate(String imagePath, String question) {
    final prompt =
        "System: Analyze the UI and answer the question.\nUser: $question\nAssistant:";
    return ModelManager.instance.runInference(
      'navigate',
      prompt,
      imagePath: imagePath,
    );
  }

  static Stream<String> distillStyle(String messages) {
    final prompt =
        "System: Extract a 50-word rulebook on the user's writing style based on these messages.\nUser: $messages\nAssistant:";
    return ModelManager.instance.runInference('distillStyle', prompt);
  }
}
