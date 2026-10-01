#!/usr/bin/env ruby
# frozen_string_literal: true

# Executes a JsonLogic rule against data using json-logic-rb.
#
# Installs the json-logic-rb gem automatically if it's missing.
#
# Usage:
#   ruby jsonlogic.rb rule.json [data.json]
#   echo '{">=": [{"var": "age"}, 18]}' | ruby jsonlogic.rb - data.json

require "json"

begin
  require "json_logic"
rescue LoadError
  warn "json-logic-rb isn't installed — installing it now (gem install json-logic-rb)..."
  installed = system("gem", "install", "json-logic-rb")
  unless installed
    # A single retry: the resolver step that usually fails here is a network call to
    # the configured gem source, and that kind of failure is often transient.
    warn "First install attempt failed — retrying once..."
    installed = system("gem", "install", "json-logic-rb")
  end
  abort "Couldn't auto-install json-logic-rb after two attempts (see the gem output " \
        "above for why — often a network or RubyGems source issue). Install it " \
        "manually and retry: gem install json-logic-rb" unless installed
  Gem.clear_paths # forget the gem list cached at startup so the new install is visible
  begin
    require "json_logic"
  rescue LoadError
    abort "json-logic-rb installed but still won't load. Run manually: gem install json-logic-rb"
  end
end

USAGE = <<~USAGE
  Usage:
    ruby jsonlogic.rb rule.json [data.json]
    echo '{"rule": "json"}' | ruby jsonlogic.rb - [data.json]
USAGE

def read_json(source)
  raw = source == "-" ? $stdin.read : File.read(source)
  JSON.parse(raw)
rescue JSON::ParserError => e
  abort "Invalid JSON in #{source}: #{e.message}"
end

def main
  abort USAGE if ARGV.empty? || ARGV.length > 2

  rule = read_json(ARGV[0])
  data = ARGV[1] ? read_json(ARGV[1]) : {}

  puts JsonLogic.apply(rule, data).inspect
end

main if __FILE__ == $PROGRAM_NAME
