import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:phantom_android/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Basic inference integration test', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();
    expect(find.text('Phantom Android'), findsNothing);
  });
}
