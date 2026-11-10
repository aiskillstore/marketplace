#!/usr/bin/env nu

# PowerPoint-native Morph recognition and slide-show playback probe for macOS.
# This records semantic/playback state only; it does not capture pixels and is
# not a substitute for visual interpolation review.

const SCHEMA_VERSION = 'pptx-morph-playback/v1'
const POWERPOINT_APP = 'Microsoft PowerPoint'

def expected-entry-effect [mode: string]: nothing -> string {
  match $mode {
    by-object => 'entry effect morph by object'
    by-word => 'entry effect morph by word'
    by-char => 'entry effect morph by char'
    _ => {
      error make {
        msg: $'Unsupported Morph mode: ($mode)'
        help: 'Use by-object, by-word, or by-char.'
      }
    }
  }
}

def safe-cleanup [path: path, base: path] {
  let resolved = ($path | path expand --strict)
  let resolved_base = ($base | path expand --strict)
  $resolved | path relative-to $resolved_base | ignore
  if $resolved == $resolved_base or $resolved == '/' or $resolved == $nu.home-dir {
    error make {msg: $'Refusing to remove unsafe playback staging path: ($resolved)'}
  }
  rm --recursive $resolved
}

def close-powerpoint-presentation [staged_path: path] {
  let script = (['on run argv'
    '  set ppt_path to item 1 of argv'
    '  using terms from application "Microsoft PowerPoint"'
    '    tell application "Microsoft PowerPoint"'
    '      set pres_count to count of presentations'
    '      repeat with i from pres_count to 1 by -1'
    '        try'
    '          if ((full name of presentation i) as string) is equal to ppt_path then'
    '            try'
    '              tell slide show window of presentation i'
    '                tell slideshow view to exit slide show'
    '              end tell'
    '            end try'
    '            close presentation i saving no'
    '          end if'
    '        end try'
    '      end repeat'
    '    end tell'
    '  end using terms from'
    'end run'] | str join (char nl))
  $script | ^osascript - $staged_path | complete | ignore
}

def parse-observation [stdout: string]: nothing -> record {
  let fields = ($stdout | str trim | split row (char tab))
  if ($fields | length) != 7 {
    error make {
      msg: 'PowerPoint playback probe returned an unexpected response.'
      help: $'Expected 7 tab-separated fields, received ($fields | length).'
    }
  }
  {
    presentationName: ($fields | get 0)
    recognizedEntryEffect: ($fields | get 1 | str trim | str lowercase)
    transitionDurationMs: (($fields | get 2 | into float) * 1000 | math round | into int)
    showWithAnimation: (($fields | get 3 | str trim | str lowercase) == 'true')
    startSlideNumber: ($fields | get 4 | into int)
    endSlideNumber: ($fields | get 5 | into int)
    presentationElapsedSeconds: ($fields | get 6 | into float)
  }
}

def run-powerpoint-probe [
  staged_path: path
  from_slide_number: int
  to_slide_number: int
  timeout_seconds: int
  staged_resave_path: string
  navigation_timeout_seconds: int
]: nothing -> record {
  # A selected range starts its show position at 1; read the slide's own index.
  # Only the staged copy's range changes, and restore it before an optional save.
  let script = (['on run argv'
    '  set ppt_path to item 1 of argv'
    '  set from_slide_number to (item 2 of argv) as integer'
    '  set to_slide_number to (item 3 of argv) as integer'
    '  set timeout_seconds to (item 4 of argv) as integer'
    '  set resave_path to item 5 of argv'
    '  set navigation_timeout_seconds to (item 6 of argv) as integer'
    '  set tab_char to ASCII character 9'
    '  with timeout of 600 seconds'
    '    tell application "Microsoft PowerPoint"'
    '      activate'
    '      set target_presentation to missing value'
    '      set pres_count to count of presentations'
    '      repeat with i from 1 to pres_count'
    '        if ((full name of presentation i) as string) is equal to ppt_path then'
    '          set target_presentation to presentation i'
    '          exit repeat'
    '        end if'
    '      end repeat'
    '      if target_presentation is missing value then'
    '        try'
    '          with timeout of navigation_timeout_seconds seconds'
    '        open POSIX file ppt_path'
    '        delay 1'
    '        set pres_count to count of presentations'
    '        repeat with i from 1 to pres_count'
    '          if ((full name of presentation i) as string) is equal to ppt_path then'
    '            set target_presentation to presentation i'
    '            exit repeat'
    '          end if'
    '        end repeat'
    '          end timeout'
    '        on error err_msg number err_num'
    '          error "open-presentation: " & err_msg number err_num'
    '        end try'
    '      end if'
    '      if target_presentation is missing value then error "PowerPoint opened no matching presentation"'
    '      try'
    '        set destination_transition to slide show transition of slide to_slide_number of target_presentation'
    '        set recognized_effect to entry effect of destination_transition as string'
    '        set recognized_duration to transition duration of destination_transition'
    '      on error err_msg number err_num'
    '        error "read-transition: " & err_msg number err_num'
    '      end try'
    '      set animations_enabled to show with animation of slide show settings of target_presentation'
    '      try'
    '        with timeout of navigation_timeout_seconds seconds'
    '          set show_settings to slide show settings of target_presentation'
    '          set original_range to range type of show_settings'
    '          set original_start to starting slide of show_settings'
    '          set original_end to ending slide of show_settings'
    '          set range type of show_settings to slide show range'
    '          set starting slide of show_settings to from_slide_number'
    '          set ending slide of show_settings to count of slides of target_presentation'
    '          set show_window to run slide show show_settings'
    '        set show_view to slideshow view of show_window'
    '        end timeout'
    '      on error err_msg number err_num'
    '        error "start-slideshow: " & err_msg number err_num'
    '      end try'
    '      delay 0.5'
    '      set deadline to (current date) + navigation_timeout_seconds'
    '      repeat while (slide index of slide of show_view) is not from_slide_number'
    '        if (current date) is greater than deadline then error "navigate-source: timed out starting at source slide; observed " & (slide index of slide of show_view as string)'
    '        delay 0.1'
    '      end repeat'
    '      set start_position to slide index of slide of show_view'
    '      try'
    '        with timeout of timeout_seconds seconds'
    '          go to next slide show_view'
    '        end timeout'
    '      on error err_msg number err_num'
    '        error "advance-slideshow: " & err_msg number err_num'
    '      end try'
    '      set deadline to (current date) + timeout_seconds'
    '      repeat while (slide index of slide of show_view) is not to_slide_number'
    '        if (current date) is greater than deadline then error "wait-destination: timed out waiting for destination slide"'
    '        delay 0.05'
    '      end repeat'
    '      if recognized_duration > timeout_seconds then error "wait-transition: duration exceeds playback timeout"'
    '      delay (recognized_duration + 0.25)'
    '      set end_position to slide index of slide of show_view'
    '      try'
    '        set elapsed_seconds to presentation elapsed time of show_view'
    '      on error err_msg number err_num'
    '        error "read-playback-state: " & err_msg number err_num'
    '      end try'
    '      set presentation_name to name of target_presentation as string'
    '      exit slide show show_view'
    '      set starting slide of show_settings to original_start'
    '      set ending slide of show_settings to original_end'
    '      set range type of show_settings to original_range'
    '      if resave_path is not "" then'
    '        try'
    '          with timeout of timeout_seconds seconds'
    '        save target_presentation in POSIX file resave_path as save as Open XML presentation'
    '          end timeout'
    '        on error err_msg number err_num'
    '          error "resave: " & err_msg number err_num'
    '        end try'
    '      end if'
    '      close target_presentation saving no'
    '      return presentation_name & tab_char & recognized_effect & tab_char & ¬'
    '        (recognized_duration as string) & tab_char & (animations_enabled as string) & tab_char & ¬'
    '        (start_position as string) & tab_char & (end_position as string) & tab_char & (elapsed_seconds as string)'
    '    end tell'
    '  end timeout'
    'end run'] | str join (char nl))
  let result = (
    $script
    | ^osascript - $staged_path ($from_slide_number | into string) ($to_slide_number | into string) ($timeout_seconds | into string) $staged_resave_path ($navigation_timeout_seconds | into string)
    | complete
  )
  if $result.exit_code != 0 {
    error make {
      msg: 'PowerPoint Morph playback probe failed.'
      help: ($result.stderr | str trim)
    }
  }
  parse-observation $result.stdout
}

def main [
  pptx_file: path                 # Candidate PPTX file.
  --from-slide: int = 1           # 1-based source slide number.
  --to-slide: int = 2             # 1-based adjacent destination slide number.
  --mode: string = 'by-object'    # Expected Morph mode.
  --duration-ms: int              # Required expected duration with 50 ms tolerance.
  --timeout-seconds: int = 10     # Destination playback/resave timeout, 1..600 seconds.
  --navigation-timeout-seconds: int = 60 # Source startup/navigation timeout, 1..600 seconds.
  --output: path                  # Optional JSON report path.
  --resave-output: path           # Optional PowerPoint-resaved PPTX path.
  --overwrite                     # Replace an existing report or resaved PPTX.
  --json                          # Print the complete report as JSON.
] {
  if $from_slide < 1 or $to_slide != ($from_slide + 1) {
    error make {msg: 'Morph playback requires one adjacent 1-based slide pair.'}
  }
  if $timeout_seconds < 1 or $timeout_seconds > 600 or $navigation_timeout_seconds < 1 or $navigation_timeout_seconds > 600 {
    error make {msg: 'Playback and navigation timeouts must be between 1 and 600 seconds.'}
  }
  if $duration_ms == null {
    error make {
      msg: 'Expected Morph duration is required for a passing playback gate.'
      help: 'Pass --duration-ms from the authored patch or inspect report.'
    }
  }
  if $duration_ms < 0 {
    error make {msg: 'Expected transition duration must be non-negative.'}
  }
  let input_path = ($pptx_file | path expand --strict)
  let expected_effect = (expected-entry-effect $mode)
  let output_path = if $output == null { null } else { $output | path expand }
  let resave_output_path = if $resave_output == null {
    null
  } else {
    $resave_output | path expand
  }
  if $output_path == $input_path or $resave_output_path == $input_path {
    error make {msg: 'Playback evidence outputs must not overwrite the input PPTX.'}
  }
  if $output_path != null and $output_path == $resave_output_path {
    error make {msg: 'JSON report and resaved PPTX outputs must use different paths.'}
  }
  for candidate in [$output_path $resave_output_path] {
    if $candidate != null and ($candidate | path exists) and not $overwrite {
      error make {msg: $'Playback output already exists: ($candidate)'}
    }
  }
  let unavailability = if (sys host | get name) != 'Darwin' {
    {
      reason: 'unsupported-platform'
      detail: 'PowerPoint Morph playback probing currently requires macOS.'
    }
  } else if (which osascript | is-empty) {
    {
      reason: 'osascript-unavailable'
      detail: 'The osascript command is unavailable.'
    }
  } else {
    let app_check = (^osascript -e $'id of application "($POWERPOINT_APP)"' | complete)
    if $app_check.exit_code == 0 {
      null
    } else {
      {
        reason: 'powerpoint-unavailable'
        detail: ($app_check.stderr | str trim)
      }
    }
  }
  if $unavailability != null {
    let report = {
      schemaVersion: $SCHEMA_VERSION
      status: 'skipped'
      gate: {
        passed: false
        reason: $unavailability.reason
      }
      input: {
        path: $input_path
        byteLength: (ls $input_path | get size.0 | into int)
        sha256: (open --raw $input_path | hash sha256)
      }
      request: {
        fromSlideIndex: ($from_slide - 1)
        toSlideIndex: ($to_slide - 1)
        morphMode: $mode
        durationMs: $duration_ms
        navigationTimeoutSeconds: $navigation_timeout_seconds
        transitionTimeoutSeconds: $timeout_seconds
      }
      availability: $unavailability
      observations: null
      checks: null
      resave: null
      limits: [
        'PowerPoint playback was not executed, so Morph recognition and playback remain unverified.'
        'This probe does not provide Windows PowerPoint compatibility evidence.'
      ]
    }
    let encoded = ($report | to json --indent 2)
    if $output_path != null {
      $encoded | save --force $output_path
    }
    if $json {
      print $encoded
    } else {
      print $'PowerPoint Morph playback: ($report.status) - ($unavailability.reason)'
    }
    return
  }
  let powerpoint_tmp = (
    $nu.home-dir
    | path join Library Containers com.microsoft.Powerpoint Data tmp
    | path expand --strict
  )
  let staging_dir = (
    mktemp --directory --tmpdir-path $powerpoint_tmp 'pptx-morph-playback.XXXXXXXX'
  )
  let staged_path = ($staging_dir | path join ($input_path | path basename))
  let staged_resave_path = if $resave_output_path == null {
    ''
  } else {
    $staging_dir | path join powerpoint-resaved.pptx
  }
  try {
    cp $input_path $staged_path
    let observation = (
      run-powerpoint-probe
        $staged_path
        $from_slide
        $to_slide
        $timeout_seconds
        $staged_resave_path
        $navigation_timeout_seconds
    )
    let resave_evidence = if $resave_output_path == null {
      null
    } else {
      if not ($staged_resave_path | path exists) {
        error make {msg: 'PowerPoint did not create the requested resaved PPTX.'}
      }
      let saved_zip = (^unzip -t $staged_resave_path | complete)
      if $saved_zip.exit_code != 0 {
        error make {msg: 'PowerPoint resave is not a complete PPTX ZIP package.'}
      }
      cp $staged_resave_path $resave_output_path
      {
        path: $resave_output_path
        byteLength: (ls $resave_output_path | get size.0 | into int)
        sha256: (open --raw $resave_output_path | hash sha256)
      }
    }
    let duration_matches = (
      (($observation.transitionDurationMs - $duration_ms) | math abs) <= 50
    )
    let checks = {
      morphModeRecognized: ($observation.recognizedEntryEffect == $expected_effect)
      slideShowAnimationsEnabled: $observation.showWithAnimation
      startedOnSource: ($observation.startSlideNumber == $from_slide)
      advancedToDestination: ($observation.endSlideNumber == $to_slide)
      durationMatched: $duration_matches
    }
    let passed = ($checks | values | all {|value| $value })
    let report = {
      schemaVersion: $SCHEMA_VERSION
      status: (if $passed { 'pass' } else { 'fail' })
      gate: {
        passed: $passed
        reason: (if $passed { 'powerpoint-recognized-and-played-morph' } else { 'powerpoint-playback-check-failed' })
      }
      input: {
        path: $input_path
        byteLength: (ls $input_path | get size.0 | into int)
        sha256: (open --raw $input_path | hash sha256)
      }
      request: {
        fromSlideIndex: ($from_slide - 1)
        toSlideIndex: ($to_slide - 1)
        morphMode: $mode
        durationMs: $duration_ms
        navigationTimeoutSeconds: $navigation_timeout_seconds
        transitionTimeoutSeconds: $timeout_seconds
      }
      observations: $observation
      checks: $checks
      resave: $resave_evidence
      limits: [
        'This probe verifies PowerPoint recognition, animation-enabled slide-show execution, and navigation to the destination slide.'
        'It does not capture or score the visual interpolation frames and does not establish rendering parity.'
      ]
    }
    let encoded = ($report | to json --indent 2)
    if $output_path != null {
      $encoded | save --force $output_path
    }
    if $json {
      print $encoded
    } else {
      print $'PowerPoint Morph playback: ($report.status)'
      print $'Effect: ($observation.recognizedEntryEffect); slides: ($observation.startSlideNumber) -> ($observation.endSlideNumber)'
    }
    if not $passed { exit 1 }
  } finally {
    close-powerpoint-presentation $staged_path
    safe-cleanup $staging_dir $powerpoint_tmp
  }
}
