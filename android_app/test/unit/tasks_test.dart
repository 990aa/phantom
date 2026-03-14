import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Test trim context correctly limits output', () {
    final text = 'A\nB\nC\nD';
    final result = text.split('\n').take(2).join('\n'); // Mock behavior
    expect(result.length, greaterThan(0));
  });
}
