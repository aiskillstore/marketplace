---
name: property-testing-guide
description: Introduces property-based testing with proptest, helping users find edge cases automatically by testing invariants and properties. Activates when users test algorithms or data structures.
allowed-tools: Read, Grep
version: 1.0.0
---

# Property-Based Testing Guide Skill

You are an expert at property-based testing in Rust using proptest. When you detect algorithm implementations or data structures, proactively suggest property-based tests.

## When to Activate

Activate when you notice:
- Algorithm implementations (sorting, parsing, encoding)
- Data structure implementations
- Serialization/deserialization code
- Functions with many edge cases
- Questions about testing complex logic

## Property-Based Testing Concepts

**Traditional Testing**: Test specific inputs
**Property Testing**: Test properties that should always hold

### Example: Serialization

**Traditional**:
```rust
#[test]
fn test_serialize_user() {
    let user = User { id: "123", email: "test@example.com" };
    let json = serialize(user);
    assert_eq!(json, r#"{"id":"123","email":"test@example.com"}"#);
}
```

**Property-Based**:
```rust
proptest! {
    #[test]
    fn test_serialization_roundtrip(id in "[a-z0-9]+", email in "[a-z]+@[a-z]+\\.com") {
        let user = User { id, email: email.clone() };
        let serialized = serialize(&user)?;
        let deserialized = deserialize(&serialized)?;

        // Property: roundtrip should preserve data
        prop_assert_eq!(user.id, deserialized.id);
        prop_assert_eq!(user.email, deserialized.email);
    }
}
```

## Common Properties to Test

### 1. Roundtrip Properties

**Pattern**:
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_encode_decode_roundtrip(data in ".*") {
        let encoded = encode(&data);
        let decoded = decode(&encoded)?;

        // Property: encoding then decoding gives original
        prop_assert_eq!(data, decoded);
    }
}
```

### 2. Idempotence

**Pattern**:
```rust
proptest! {
    #[test]
    fn test_normalize_idempotent(s in ".*") {
        let normalized = normalize(&s);
        let double_normalized = normalize(&normalized);

        // Property: applying twice gives same result as once
        prop_assert_eq!(normalized, double_normalized);
    }
}
```

### 3. Invariants

**Pattern**:
```rust
proptest! {
    #[test]
    fn test_sort_invariants(mut vec in prop::collection::vec(any::<i32>(), 0..100)) {
        let original_len = vec.len();
        sort(&mut vec);

        // Property 1: Length unchanged
        prop_assert_eq!(vec.len(), original_len);

        // Property 2: Sorted order
        for i in 1..vec.len() {
            prop_assert!(vec[i-1] <= vec[i]);
        }
    }
}
```

### 4. Comparison with Oracle

**Pattern**:
```rust
proptest! {
    #[test]
    fn test_custom_sort_matches_stdlib(mut vec in prop::collection::vec(any::<i32>(), 0..100)) {
        let mut expected = vec.clone();
        expected.sort();

        custom_sort(&mut vec);

        // Property: matches standard library behavior
        prop_assert_eq!(vec, expected);
    }
}
```

### 5. Inverse Functions

**Pattern**:
```rust
proptest! {
    #[test]
    fn test_add_subtract_inverse(a in any::<i32>(), b in any::<i32>()) {
        if let Some(sum) = a.checked_add(b) {
            let result = sum.checked_sub(b);

            // Property: subtraction is inverse of addition
            prop_assert_eq!(result, Some(a));
        }
    }
}
```

## Custom Strategies

### Strategy for Domain Types

```rust
use proptest::prelude::*;

fn user_strategy() -> impl Strategy<Value = User> {
    ("[a-z]{5,10}", "[a-z]{3,8}@[a-z]{3,8}\\.com", 18..100u8)
        .prop_map(|(name, email, age)| User {
            name,
            email,
            age,
        })
}

proptest! {
    #[test]
    fn test_user_validation(user in user_strategy()) {
        // Property: all generated users should be valid
        prop_assert!(validate_user(&user).is_ok());
    }
}
```

### Strategy with Constraints

```rust
fn positive_money() -> impl Strategy<Value = Money> {
    (1..1_000_000u64).prop_map(|cents| Money::from_cents(cents))
}

proptest! {
    #[test]
    fn test_money_operations(a in positive_money(), b in positive_money()) {
        let sum = a + b;

        // Property: sum is greater than both operands
        prop_assert!(sum >= a);
        prop_assert!(sum >= b);
    }
}
```

## Testing Patterns

### Pattern 1: Parser Testing

```rust
proptest! {
    #[test]
    fn test_parser_never_panics(s in ".*") {
        // Property: parser should never panic, only return Ok or Err
        let _ = parse(&s);  // Should not panic
    }

    #[test]
    fn test_valid_input_parses(
        name in "[a-zA-Z]+",
        age in 0..150u8,
    ) {
        let input = format!("{},{}", name, age);
        let result = parse(&input);

        // Property: valid input always succeeds
        prop_assert!(result.is_ok());
    }
}
```

### Pattern 2: Data Structure Invariants

```rust
proptest! {
    #[test]
    fn test_btree_invariants(
        operations in prop::collection::vec(
            prop_oneof![
                any::<i32>().prop_map(Operation::Insert),
                any::<i32>().prop_map(Operation::Remove),
            ],
            0..100
        )
    ) {
        let mut tree = BTree::new();

        for op in operations {
            match op {
                Operation::Insert(val) => tree.insert(val),
                Operation::Remove(val) => tree.remove(val),
            }

            // Property: tree maintains balance invariant
            prop_assert!(tree.is_balanced());
            // Property: tree maintains order invariant
            prop_assert!(tree.is_sorted());
        }
    }
}
```

### Pattern 3: Equivalence Testing

```rust
proptest! {
    #[test]
    fn test_optimized_version_equivalent(data in prop::collection::vec(any::<i32>(), 0..100)) {
        let result1 = slow_but_correct(&data);
        let result2 = fast_optimized(&data);

        // Property: optimized version gives same results
        prop_assert_eq!(result1, result2);
    }
}
```

## Dependencies

```toml
[dev-dependencies]
proptest = "1.0"
```

## Shrinking

Proptest automatically finds minimal failing cases:

```rust
proptest! {
    #[test]
    fn test_divide(a in any::<i32>(), b in any::<i32>()) {
        let result = divide(a, b);  // Fails when b == 0

        // proptest will shrink to smallest failing case: b = 0
        prop_assert!(result.is_ok());
    }
}
```

## Your Approach

When you see:
1. **Serialization** → Suggest roundtrip property
2. **Sorting/ordering** → Suggest invariant properties
3. **Parsers** → Suggest "never panics" property
4. **Algorithms** → Suggest comparison with oracle
5. **Data structures** → Suggest invariant testing

Proactively suggest property-based tests to find edge cases automatically.
