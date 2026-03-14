import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB('phantom.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final docsDir = await getApplicationDocumentsDirectory();
    final phantomDir = Directory(join(docsDir.path, '.phantom'));
    if (!await phantomDir.exists()) {
      await phantomDir.create(recursive: true);
    }
    final dbPath = join(phantomDir.path, filePath);

    return await openDatabase(dbPath, version: 1, onCreate: _createDB);
  }

  Future _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        app_context TEXT
      )
    ''');
  }

  Future<void> logMessage(String content, String appContext) async {
    final db = await instance.database;
    final truncatedContent = content.length > 800
        ? content.substring(0, 800)
        : content;

    await db.insert('messages', {
      'role': 'user',
      'content': truncatedContent,
      'app_context': appContext,
    });
  }
}
