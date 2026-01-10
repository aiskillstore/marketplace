#!/bin/bash
# Extract code blocks from documentation text
# Uses awk for maximum efficiency (0 LLM tokens!)

set -euo pipefail

MAX_BLOCKS="${1:-5}"

# Use awk to extract code blocks between ``` markers
awk -v max="$MAX_BLOCKS" '
  BEGIN {
    count = 0
    in_block = 0
    block = ""
    lang = ""
  }

  /^```/ {
    if (in_block) {
      # End of code block
      if (count < max && length(block) > 20) {
        count++
        print "### Example " count
        if (lang != "") {
          print "```" lang
        } else {
          print "```"
        }
        print block
        print "```\n"
      }
      block = ""
      lang = ""
      in_block = 0
    } else {
      # Start of code block - extract language
      in_block = 1
      lang = substr($0, 4)  # Get language after ```
    }
    next
  }

  in_block {
    if (block != "") {
      block = block "\n" $0
    } else {
      block = $0
    }
  }

  END {
    if (count == 0) {
      print "# No code blocks found"
    }
  }
'
