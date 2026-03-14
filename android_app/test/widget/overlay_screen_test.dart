import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:phantom_android/screens/overlay_screen.dart';

void main() {
  testWidgets('Overlay screen renders correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(child: MaterialApp(home: OverlayScreen())),
    );

    expect(find.text('Phantom'), findsWidgets);
    expect(find.text('Summarize'), findsOneWidget);
    expect(find.text('Simplify'), findsOneWidget);
    expect(find.text('Explain'), findsOneWidget);
    expect(find.text('Reply'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
    expect(find.text('Caption'), findsOneWidget);
    expect(find.text('Navigate'), findsOneWidget);
    expect(find.text('Custom'), findsOneWidget);

    expect(find.text('Generate'), findsOneWidget);
  });
}
