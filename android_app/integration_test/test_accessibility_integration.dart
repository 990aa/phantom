import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:phantom_android/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Accessibility integration stub', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();
    expect(1, 1);
  });
}
