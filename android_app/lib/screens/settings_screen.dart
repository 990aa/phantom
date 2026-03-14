import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/services.dart';
import '../db.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  String _triggerMethod = 'Floating bubble';
  bool _learnStyle = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _triggerMethod = prefs.getString('trigger_method') ?? 'Floating bubble';
      _learnStyle = prefs.getBool('learn_style') ?? true;
    });
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('trigger_method', _triggerMethod);
    await prefs.setBool('learn_style', _learnStyle);
  }

  Future<void> _clearData() async {
    final db = await DatabaseHelper.instance.database;
    await db.delete('messages');
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Personalization data deleted')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        children: [
          // Accessibility Banner
          Container(
            color: Colors.red.withOpacity(0.1),
            child: ListTile(
              leading: const Icon(Icons.accessibility, color: Colors.red),
              title: const Text('Accessibility Permission Required'),
              subtitle: const Text('Tap to enable in Settings'),
              onTap: () {
                const MethodChannel(
                  'com.phantom/native',
                ).invokeMethod('openAccessibilitySettings');
              },
            ),
          ),

          ListTile(
            title: const Text('Trigger Method'),
            trailing: DropdownButton<String>(
              value: _triggerMethod,
              items: const [
                DropdownMenuItem(
                  value: 'Floating bubble',
                  child: Text('Floating bubble'),
                ),
                DropdownMenuItem(
                  value: 'Notification action',
                  child: Text('Notification action'),
                ),
              ],
              onChanged: (val) {
                setState(() {
                  _triggerMethod = val!;
                });
                _saveSettings();
              },
            ),
          ),

          SwitchListTile(
            title: const Text('Learn my writing style'),
            value: _learnStyle,
            onChanged: (val) {
              setState(() {
                _learnStyle = val;
              });
              _saveSettings();
            },
          ),

          const ExpansionTile(
            title: Text('View Style Rulebook'),
            children: [
              Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'No rules generated yet.',
                  style: TextStyle(fontStyle: FontStyle.italic),
                ),
              ),
            ],
          ),

          Padding(
            padding: const EdgeInsets.all(16.0),
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(foregroundColor: Colors.red),
              onPressed: _clearData,
              child: const Text('Delete Personalization Data'),
            ),
          ),

          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Privacy Notice: All data is processed entirely on-device using local models.',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
        ],
      ),
    );
  }
}
