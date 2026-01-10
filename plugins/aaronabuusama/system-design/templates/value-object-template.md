# Value Object Template

## Characteristics

- **Immutable**: Once created, cannot be changed
- **Equality by value**: Two instances with same values are equal
- **Self-validating**: Validates on construction
- **No identity**: No ID field

## Basic Structure

```typescript
// src/domain/value-objects/[ValueObjectName].ts

export class [ValueObjectName] {
  private constructor(
    public readonly /* fields */
  ) {}

  // Factory method with validation
  static of(/* args */): [ValueObjectName] {
    // Validate
    // Return new instance
  }

  // Alternative factory for common cases
  static from(/* different args */): [ValueObjectName] {
    // Parse/convert
    // Delegate to of()
  }

  // Equality
  equals(other: [ValueObjectName]): boolean {
    return /* compare all fields */;
  }

  // Serialization
  toString(): string {
    return /* string representation */;
  }

  // Operations return NEW instances
  someOperation(/* args */): [ValueObjectName] {
    return new [ValueObjectName](/* new values */);
  }
}
```

## Example: Money

```typescript
// src/domain/value-objects/Money.ts

export type Currency = 'USD' | 'EUR' | 'GBP';

export class Money {
  private constructor(
    public readonly amount: number,
    public readonly currency: Currency
  ) {}

  // ===== Factory Methods =====

  static of(amount: number, currency: Currency): Money {
    if (!Number.isFinite(amount)) {
      throw new Error('Amount must be a finite number');
    }
    if (amount < 0) {
      throw new Error('Amount cannot be negative');
    }
    // Round to 2 decimal places
    const rounded = Math.round(amount * 100) / 100;
    return new Money(rounded, currency);
  }

  static zero(currency: Currency): Money {
    return new Money(0, currency);
  }

  static fromCents(cents: number, currency: Currency): Money {
    return Money.of(cents / 100, currency);
  }

  // ===== Operations (return new instances) =====

  add(other: Money): Money {
    this.ensureSameCurrency(other);
    return Money.of(this.amount + other.amount, this.currency);
  }

  subtract(other: Money): Money {
    this.ensureSameCurrency(other);
    const result = this.amount - other.amount;
    if (result < 0) {
      throw new Error('Result cannot be negative');
    }
    return Money.of(result, this.currency);
  }

  multiply(factor: number): Money {
    return Money.of(this.amount * factor, this.currency);
  }

  // ===== Queries =====

  get cents(): number {
    return Math.round(this.amount * 100);
  }

  isZero(): boolean {
    return this.amount === 0;
  }

  isGreaterThan(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount > other.amount;
  }

  isLessThan(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount < other.amount;
  }

  // ===== Equality =====

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  // ===== Serialization =====

  toString(): string {
    return `${this.currency} ${this.amount.toFixed(2)}`;
  }

  toJSON(): { amount: number; currency: Currency } {
    return { amount: this.amount, currency: this.currency };
  }

  // ===== Private =====

  private ensureSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new Error(
        `Currency mismatch: ${this.currency} vs ${other.currency}`
      );
    }
  }
}
```

## Example: Email

```typescript
// src/domain/value-objects/Email.ts

export class Email {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  private constructor(public readonly value: string) {}

  static of(value: string): Email {
    const normalized = value.trim().toLowerCase();

    if (!normalized) {
      throw new Error('Email cannot be empty');
    }

    if (!Email.EMAIL_REGEX.test(normalized)) {
      throw new Error(`Invalid email format: ${value}`);
    }

    return new Email(normalized);
  }

  get domain(): string {
    return this.value.split('@')[1];
  }

  get localPart(): string {
    return this.value.split('@')[0];
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}
```

## Example: DateRange

```typescript
// src/domain/value-objects/DateRange.ts

export class DateRange {
  private constructor(
    public readonly start: Date,
    public readonly end: Date
  ) {}

  static of(start: Date, end: Date): DateRange {
    if (end < start) {
      throw new Error('End date must be after start date');
    }
    return new DateRange(new Date(start), new Date(end));
  }

  static fromNow(durationDays: number): DateRange {
    const start = new Date();
    const end = new Date(start);
    end.setDate(end.getDate() + durationDays);
    return new DateRange(start, end);
  }

  contains(date: Date): boolean {
    return date >= this.start && date <= this.end;
  }

  overlaps(other: DateRange): boolean {
    return this.start <= other.end && this.end >= other.start;
  }

  get durationDays(): number {
    const diff = this.end.getTime() - this.start.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  extend(days: number): DateRange {
    const newEnd = new Date(this.end);
    newEnd.setDate(newEnd.getDate() + days);
    return DateRange.of(this.start, newEnd);
  }

  equals(other: DateRange): boolean {
    return (
      this.start.getTime() === other.start.getTime() &&
      this.end.getTime() === other.end.getTime()
    );
  }

  toString(): string {
    return `${this.start.toISOString()} - ${this.end.toISOString()}`;
  }
}
```

## Example: Address (Composite Value Object)

```typescript
// src/domain/value-objects/Address.ts

export interface AddressProps {
  street: string;
  city: string;
  postalCode: string;
  country: string;
  state?: string;
}

export class Address {
  private constructor(
    public readonly street: string,
    public readonly city: string,
    public readonly postalCode: string,
    public readonly country: string,
    public readonly state: string | undefined
  ) {}

  static of(props: AddressProps): Address {
    if (!props.street.trim()) throw new Error('Street is required');
    if (!props.city.trim()) throw new Error('City is required');
    if (!props.postalCode.trim()) throw new Error('Postal code is required');
    if (!props.country.trim()) throw new Error('Country is required');

    return new Address(
      props.street.trim(),
      props.city.trim(),
      props.postalCode.trim().toUpperCase(),
      props.country.trim().toUpperCase(),
      props.state?.trim()
    );
  }

  withStreet(street: string): Address {
    return Address.of({ ...this.toProps(), street });
  }

  equals(other: Address): boolean {
    return (
      this.street === other.street &&
      this.city === other.city &&
      this.postalCode === other.postalCode &&
      this.country === other.country &&
      this.state === other.state
    );
  }

  toProps(): AddressProps {
    return {
      street: this.street,
      city: this.city,
      postalCode: this.postalCode,
      country: this.country,
      state: this.state,
    };
  }

  toString(): string {
    const parts = [this.street, this.city];
    if (this.state) parts.push(this.state);
    parts.push(this.postalCode, this.country);
    return parts.join(', ');
  }
}
```

## Testing Value Objects

```typescript
// src/domain/value-objects/Money.test.ts

import { describe, test, expect } from 'bun:test';
import { Money } from './Money';

describe('Money', () => {
  describe('of', () => {
    test('creates money with valid amount', () => {
      const money = Money.of(100.50, 'USD');

      expect(money.amount).toBe(100.50);
      expect(money.currency).toBe('USD');
    });

    test('rounds to 2 decimal places', () => {
      const money = Money.of(100.555, 'USD');

      expect(money.amount).toBe(100.56);
    });

    test('throws on negative amount', () => {
      expect(() => Money.of(-10, 'USD')).toThrow();
    });
  });

  describe('add', () => {
    test('adds two money values', () => {
      const a = Money.of(100, 'USD');
      const b = Money.of(50, 'USD');

      const result = a.add(b);

      expect(result.amount).toBe(150);
      expect(result.currency).toBe('USD');
    });

    test('throws on currency mismatch', () => {
      const usd = Money.of(100, 'USD');
      const eur = Money.of(100, 'EUR');

      expect(() => usd.add(eur)).toThrow('Currency mismatch');
    });

    test('does not mutate original', () => {
      const original = Money.of(100, 'USD');
      original.add(Money.of(50, 'USD'));

      expect(original.amount).toBe(100);
    });
  });

  describe('equals', () => {
    test('returns true for same values', () => {
      const a = Money.of(100, 'USD');
      const b = Money.of(100, 'USD');

      expect(a.equals(b)).toBe(true);
    });

    test('returns false for different amounts', () => {
      const a = Money.of(100, 'USD');
      const b = Money.of(200, 'USD');

      expect(a.equals(b)).toBe(false);
    });

    test('returns false for different currencies', () => {
      const a = Money.of(100, 'USD');
      const b = Money.of(100, 'EUR');

      expect(a.equals(b)).toBe(false);
    });
  });
});
```
