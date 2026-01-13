# RBS-Inline Syntax Guide

Source: https://github.com/soutaro/rbs-inline/wiki/Syntax-guide

## Magic Comment

To enable RBS generation, include `# rbs_inline: enabled` at the start of Ruby files. Alternatively, use `# rbs_inline: disabled` for opt-out scenarios.

## Defining Classes

Classes translate to RBS definitions. Class and superclass names must use constant syntax.

Generic classes require the `# @rbs generic` annotation:

```ruby
# @rbs generic A
# @rbs generic unchecked in B < String
class Foo
end
```

The `# @rbs inherits` annotation specifies superclasses with RBS syntax when Ruby's syntax is insufficient.

## Defining Modules

Module syntax converts to RBS module definitions. Use `# @rbs generic` for generics support and `# @rbs module-self` for self-type constraints.

## Blocks Defining Classes and Modules

Use `@rbs class` and `@rbs module` annotations for implicit class/module definitions within block contexts.

## Mixins

`include`, `prepend`, and `extend` method calls with constant syntax translate to RBS mixin syntax. Generic modules use `#[` syntax.

## Method Definitions

### #: Syntax

Primitive approach for embedding RBS method types:

```ruby
#: () -> String
def to_s
end
```

### # @rbs Syntax

Alternative supporting overloads with pipes:

```ruby
# @rbs () -> String
def to_s
end
```

### Doc Style

Parameter and return type documentation:

```ruby
# @rbs size: Integer
# @rbs return: Section?
def section(size)
end
```

Block types use `# @rbs &block:` with optional syntax (`?`).

### Override Methods

`# @rbs override` indicates superclass method overriding.

### Singleton Methods

`def self.foo` syntax is supported within class/module definitions.

### RBS Annotations

Apply annotations using `# @rbs %a{annotation}` syntax.

## Attributes

Standard attribute methods (`attr_reader`, `attr_writer`, `attr_accessor`) are supported with type declarations:

```ruby
attr_reader :name #: String
attr_writer :age #: Integer
attr_accessor :email #: String?
```

## Instance Variables

Declare instance variable types using `# @rbs @var: Type` annotation:

```ruby
# @rbs @name: String
# @rbs @count: Integer
```

Class instance variables use `self.@var`:

```ruby
# @rbs self.@all_names: Array[String]
```

## Constant Types

Add `#:` syntax to declare constant types:

```ruby
VERSION = "1.0.0" #: String
MAX_SIZE = 100 #: Integer
```

The tool infers simple literal types automatically.

## Alias

Ruby `alias` syntax is detected and generates corresponding RBS declarations.

## Skipping Constructs

Use `# @rbs skip` annotation to exclude definitions from RBS generation:

```ruby
# @rbs skip
def internal_method
end
```

## Embedding RBS Elements

The `# @rbs!` annotation allows direct RBS element inclusion for unsupported constructs:

```ruby
# @rbs!
#   type json = String | Integer | Array[json] | Hash[String, json]
```

## Deprecated Syntaxes (v0.5.0)

- `# @rbs returns T` -> use `# @rbs return: T`
- `# @rbs yields: T` -> use `# @rbs &block: T`
- `#::` -> use `#:`
