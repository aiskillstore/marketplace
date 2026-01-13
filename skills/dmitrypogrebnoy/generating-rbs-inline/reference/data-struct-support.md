# Data and Struct Support

Source: https://github.com/soutaro/rbs-inline/wiki/Data-Struct-support

## Overview

RBS::Inline generates type definitions for `Data.define` and `Struct.new` calls by detecting constant assignments.

## Basic Example

**Input Code:**

```ruby
Account = Data.define(
  :id,   #: Integer
  :email #: String
)

Group = Struct.new(
  :accounts #: Array[Account]
)
```

**Generated RBS:**

```ruby
class Account < Data
  attr_reader id(): Integer
  attr_reader email(): String
  def initialize: (Integer id, String email) -> void
                | (id: Integer, email: String) -> void
end

class Group < Struct[untyped]
  attr_accessor accounts(): Array[Account]
  def initialize: (?Array[Account] accounts) -> void
                | (?accounts: Array[Account]) -> void
end
```

## Struct.new Configuration

### keyword_init Option

The tool detects `keyword_init:` options with literal values:

- `keyword_init: true` - omits positional parameter initializer
- `keyword_init: false` - omits keyword parameter initializer
- Other values - generates both versions

### Annotations

Two special annotations modify generation behavior:

```ruby
# @rbs %a{rbs-inline:new-args=required}
# @rbs %a{rbs-inline:readonly-attributes=true}
Group = Struct.new(:accounts #: Array[Account])
```

- `new-args=required` - generates required parameters despite optional implementation
- `readonly-attributes=true` - generates `attr_reader` instead of `attr_accessor`

## Adding Custom Methods

Define additional methods using the class syntax after assignment:

```ruby
Account = Data.define(:id, :email)

class Account
  # @rbs (String) -> void
  def send_email(body)
    # Implementation
  end
end
```

## Steep Integration

Use `__skip__` annotations to suppress type checking errors:

```ruby
Account = __skip__ = Data.define(
  :id,   #: Integer
  :email #: String
)
```
