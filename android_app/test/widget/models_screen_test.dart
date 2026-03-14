import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phantom_android/screens/models_screen.dart';

void main() {
  testWidgets('Models screen renders layout', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: ModelsScreen())),
    );

    expect(find.text('Models'), findsOneWidget);
    expect(find.text('Add Custom GGUF'), findsOneWidget);
    expect(find.byType(ExpansionTile), findsOneWidget);
  });
}
