# Testing Patterns

Comprehensive guide to testing Swift applications with XCTest and Swift Testing frameworks.

## XCTest

```swift
import XCTest
@testable import MyModule

final class MyTests: XCTestCase {
    private var sut: MyService!

    override func setUp() {
        super.setUp()
        sut = MyService()
    }

    func testExample() throws {
        let result = sut.process("input")
        XCTAssertEqual(result, "expected")
    }

    func testAsync() async throws {
        let result = try await sut.fetchData()
        XCTAssertNotNil(result)
    }
}
```

## Swift Testing (Xcode 16+)

```swift
import Testing
@testable import MyModule

@Suite("Feature Tests")
struct FeatureTests {
    let service = MyService()  // Shared across tests in suite

    @Test("Basic calculation")
    func basicCalc() {
        #expect(Calculator().add(2, 3) == 5)
    }

    @Test("Parameterized", arguments: [1, 2, 3])
    func squares(value: Int) {
        #expect(value * value > 0)
    }

    @Test("Async operation")
    func asyncTest() async throws {
        let result = try await service.fetchData()
        #expect(result != nil)
    }

    @Test("Throwing function")
    func throwingTest() throws {
        #expect(throws: MyError.invalid) {
            try service.validate("invalid")
        }
    }

    @Test("Require precondition")
    func requireTest() throws {
        let config = try #require(loadConfig())  // Fails test if nil
        #expect(config.isValid)
    }
}

// Custom test with multiple expectations
@Test("Value in range")
func valueInRange() {
    let value = 42
    #expect(value > 40)
    #expect(value < 50)
}

// Test organization with tags
@Suite("User Service", .tags(.integration))
struct UserServiceTests {
    let service = UserService()

    @Test("Create user")
    func createUser() async throws {
        let user = try await service.createUser(name: "Test")
        #expect(user.id != nil)
    }
}

extension Tag {
    @Tag static var integration: Self
}
```
