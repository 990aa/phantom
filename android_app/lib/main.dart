import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:convert';
import 'db.dart';
import 'screens/main_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  const platform = MethodChannel('com.phantom/native');
  platform.setMethodCallHandler((call) async {
    if (call.method == 'onContext') {
      final jsonStr = call.arguments as String;
      final data = jsonDecode(jsonStr);
      final packageName = data['packageName'] as String?;
      
      if (packageName == 'com.whatsapp' || packageName == 'com.google.android.apps.messaging') {
        final textNodes = data['textNodes'] as List<dynamic>?;
        if (textNodes != null && textNodes.isNotEmpty) {
          await DatabaseHelper.instance.logMessage(textNodes.last.toString(), packageName!);
        }
      }
    }
  });

  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Phantom Android',
      theme: ThemeData(
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFFF4757),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      home: const MainScreen(),
    );
  }
}