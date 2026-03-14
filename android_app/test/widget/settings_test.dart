import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:phantom_android/screens/settings_screen.dart';

void main() {
  testWidgets('Settings screen renders elements', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));

    expect(find.text('Settings'), findsOneWidget);
    expect(find.text('Trigger Method'), findsOneWidget);
    expect(find.text('Learn my writing style'), findsOneWidget);
    expect(find.text('View Style Rulebook'), findsOneWidget);
    expect(find.text('Delete Personalization Data'), findsOneWidget);
  });
}
