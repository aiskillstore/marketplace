#!/usr/bin/env ruby
# frozen_string_literal: true

# Structural validator for JsonLogic rules — stdlib only, no execution.
#
# Checks that a JSON value is well-formed *shape* for a JsonLogic rule: every
# operator node is a single-key object whose value is a list of arguments (or
# a bare value, per the single-argument shorthand). This is NOT a JsonLogic
# evaluator — it can't tell you whether a specific library supports every
# operator used, or what the rule actually computes. See references/testing.md
# for what "validated" should and shouldn't be taken to mean.
#
# Usage:
#   ruby validate_skill.rb path/to/rule.json
#   echo '{">": [{"var": "age"}, 18]}' | ruby validate_skill.rb -

require "json"
require "set"

module JsonLogic
  # Walks a parsed JSON value and reports where it stops looking like
  # JsonLogic: {"operator": [args]}, nested arbitrarily deep.
  class ShapeValidator
    CORE_OPERATORS = %w[
      var missing missing_some
      if == === != !== ! !! and or
      > >= < <= max min + - * / %
      map filter reduce all some none merge in
      cat substr log
    ].freeze

    # Documented community extensions — not part of the core jsonlogic.com
    # spec (see references/operations.md), but not typos either.
    COMMUNITY_OPERATORS = %w[?? try throw preserve ?:].freeze

    KNOWN_OPERATORS = Set.new(CORE_OPERATORS + COMMUNITY_OPERATORS).freeze

    Issue = Struct.new(:path, :message) do
      def to_s = "#{path}: #{message}"
    end

    def self.check(rule) = new.visit(rule)

    def visit(node, path = "$")
      case node
      when Hash  then visit_operator(node, path)
      when Array then node.each_with_index.flat_map { |child, i| visit(child, "#{path}[#{i}]") }
      else []
      end
    end

    private

    def visit_operator(node, path)
      unless node.one?
        return [Issue.new(path, "operator object must have exactly one key, got #{node.keys}")]
      end

      operator, raw_arguments = node.first
      issues = known?(operator) ? [] : [Issue.new(path, unknown_operator(operator))]
      arguments(raw_arguments).each_with_index do |argument, index|
        issues.concat(visit(argument, "#{path}.#{operator}[#{index}]"))
      end
      issues
    end

    def arguments(value) = value.is_a?(Array) ? value : [value]

    def known?(operator) = KNOWN_OPERATORS.include?(operator)

    def unknown_operator(operator)
      "'#{operator}' is not a core jsonlogic.com operator — confirm it's a documented " \
        "extension your target library supports (see references/operations.md)"
    end
  end
end

USAGE = <<~USAGE
  Usage:
    ruby validate_skill.rb path/to/rule.json
    echo '{">": [{"var": "age"}, 18]}' | ruby validate_skill.rb -
USAGE

def read_rule(source)
  raw = source == "-" ? $stdin.read : File.read(source)
  JSON.parse(raw)
rescue JSON::ParserError => e
  abort "Invalid JSON: #{e.message}"
end

def main
  abort USAGE if ARGV.length != 1

  issues = JsonLogic::ShapeValidator.check(read_rule(ARGV.first))
  if issues.empty?
    puts "Structurally valid JsonLogic shape. (Not executed — this checks shape only.)"
  else
    issues.each { |issue| puts issue }
    exit 1
  end
end

main if __FILE__ == $PROGRAM_NAME
