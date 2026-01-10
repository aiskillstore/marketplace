# Dart + flutter_test Template

Template for generating Dart/Flutter test scaffolds.

## Variables

| Variable | Description |
|----------|-------------|
| `{library_name}` | Library name (e.g., `login`) |
| `{import_path}` | Package import path (e.g., `package:my_app/auth/login.dart`) |
| `{class_name}` | Name of class being tested |
| `{function_name}` | Name of function being tested |

## File Template

```dart
/// Tests for {library_name}.
///
/// Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
/// Fill in test implementations and remove TODO comments.
import 'package:flutter_test/flutter_test.dart';

import '{import_path}';

void main() {
  {class_tests}

  {function_tests}
}
```

## Class Test Template

```dart
  group('{ClassName}', () {
    late {ClassName} instance;

    setUp(() {
      // TODO: Configure instance with appropriate test data
      instance = {ClassName}();
    });

    tearDown(() {
      // TODO: Clean up if needed
    });

{method_tests}
  });
```

## Method Test Template

```dart
    group('{methodName}', () {
      test('should handle the happy path', () {
        // TODO: Implement this test
        // - Call instance.{methodName}()
        // - Assert expected behavior
        fail('Test not yet implemented');
      });

      test('should handle edge cases', skip: 'TODO: Implement');

      test('should handle error conditions', skip: 'TODO: Implement');
    });
```

## Function Test Template

```dart
  group('{functionName}', () {
    test('should handle the happy path', () {
      // TODO: Implement this test
      // - Call {functionName}()
      // - Assert expected behavior
      fail('Test not yet implemented');
    });

    test('should handle edge cases', skip: 'TODO: Implement');

    test('should handle error conditions', skip: 'TODO: Implement');
  });
```

## Async Test Template

```dart
    test('should handle the happy path', () async {
      // TODO: Implement this test
      // - Call await {functionName}()
      // - Assert expected behavior
      fail('Test not yet implemented');
    });
```

## Widget Test Template

For Flutter widgets:

```dart
  group('{WidgetName}', () {
    testWidgets('should render correctly', (tester) async {
      // TODO: Implement this test
      await tester.pumpWidget(
        const MaterialApp(
          home: {WidgetName}(),
        ),
      );

      // TODO: Add assertions
      fail('Test not yet implemented');
    });

    testWidgets('should handle user interaction', skip: 'TODO: Implement',
        (tester) async {});
  });
```

## Mock Template

Using `mocktail`:

```dart
import 'package:mocktail/mocktail.dart';

class Mock{ClassName} extends Mock implements {ClassName} {}

// In test:
late Mock{ClassName} mock{ClassName};

setUp(() {
  mock{ClassName} = Mock{ClassName}();
  when(() => mock{ClassName}.{method}()).thenReturn(/* TODO */);
});
```

## Example Output

Given source file `lib/auth/login.dart`:
```dart
class UserSession {
  final String userId;

  UserSession({required this.userId});

  Future<bool> refresh() async { ... }

  void invalidate() { ... }
}

Future<UserSession> authenticate(String username, String password) async { ... }

bool logout(UserSession session) { ... }
```

Generated scaffold `test/auth/login_test.dart`:
```dart
/// Tests for login.
///
/// Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
/// Fill in test implementations and remove TODO comments.
import 'package:flutter_test/flutter_test.dart';

import 'package:my_app/auth/login.dart';

void main() {
  group('UserSession', () {
    late UserSession instance;

    setUp(() {
      // TODO: Configure instance with appropriate test data
      instance = UserSession(userId: 'test-user-id');
    });

    group('refresh', () {
      test('should handle the happy path', () async {
        // TODO: Implement this test
        // - Call await instance.refresh()
        // - Assert expected behavior
        fail('Test not yet implemented');
      });

      test('should handle edge cases', skip: 'TODO: Implement');

      test('should handle error conditions', skip: 'TODO: Implement');
    });

    group('invalidate', () {
      test('should handle the happy path', () {
        // TODO: Implement this test
        // - Call instance.invalidate()
        // - Assert expected behavior
        fail('Test not yet implemented');
      });

      test('should handle edge cases', skip: 'TODO: Implement');

      test('should handle error conditions', skip: 'TODO: Implement');
    });
  });

  group('authenticate', () {
    test('should handle the happy path', () async {
      // TODO: Implement this test
      // - Call await authenticate()
      // - Assert expected behavior
      fail('Test not yet implemented');
    });

    test('should handle edge cases', skip: 'TODO: Implement');

    test('should handle error conditions', skip: 'TODO: Implement');
  });

  group('logout', () {
    test('should handle the happy path', () {
      // TODO: Implement this test
      // - Call logout()
      // - Assert expected behavior
      fail('Test not yet implemented');
    });

    test('should handle edge cases', skip: 'TODO: Implement');

    test('should handle error conditions', skip: 'TODO: Implement');
  });
}
```

## Naming Rules

| Source | Test File |
|--------|-----------|
| `lib/auth/login.dart` | `test/auth/login_test.dart` |
| `lib/utils.dart` | `test/utils_test.dart` |
| `lib/widgets/button.dart` | `test/widgets/button_test.dart` |

## Dart Test Conventions

- Test files must end with `_test.dart`
- Test files go in `test/` directory mirroring `lib/` structure
- Use `group()` to organize related tests
- Use `setUp()` and `tearDown()` for test fixtures
- Use `skip:` parameter for TODO tests
- Use `fail()` to mark unimplemented tests
