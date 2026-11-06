#!/usr/bin/env nu

# AI-friendly Microsoft PowerPoint slide snapshot tool for macOS.
#
# Behavior:
# 1. For PDF rendering, stage the PPTX inside PowerPoint's sandbox container
# 2. For window capture, create a byte-identical tool-owned copy in the system temp directory
# 3. Switch to the requested slide
# 4. Default to exporting PDF inside PowerPoint's sandbox container and rendering the slide with PDFium
# 5. If `--method auto` is used, fall back to a candidate-bound window screenshot with `screencapture`
#
# Examples:
#   nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu demos/06-couple.pptx 3
#   nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu demos/06-couple.pptx --slide 3 --out demos/snapshot-3.png
#   nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu demos/06-couple.pptx --slides 3-8 --out demos/snapshot-%d.png
#   nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu demos/06-couple.pptx --slides 3,5,8-10 --out demos/snapshot-%d.png
#   nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu demos/06-couple.pptx 3 --method auto --json
#
# Notes:
# - `window` mode needs macOS Screen Recording permission for the current terminal/host app
# - `window` mode also needs macOS Accessibility permission to query the slide-show canvas rect
# - `window` mode captures the slide-show canvas instead of the full editing window
# - `pdf-render` mode requires xdoc with PDFium support and Node.js
# - PDF page identity follows presentation order and verified hidden-slide omissions
# - `pdf-render` mode also requires App Data access to PowerPoint's sandbox container; use `auto` or
#   `window` when the terminal/host app does not have that macOS privacy permission

const SLIDE_VISIBILITY_TOOL = path self | path dirname | path join 'slide-visibility.mjs'

def command-exists [name: string]: nothing -> bool {
  not (which $name | is-empty)
}

def file-sha256 [file_path: string]: nothing -> string {
  open --raw $file_path | hash sha256
}

def default-output-path [pptx_path: string, slide_number: int]: nothing -> string {
  $pptx_path | path dirname | path join $"snapshot-($slide_number).png"
}

def default-output-pattern [pptx_path: string]: nothing -> string {
  $pptx_path | path dirname | path join 'snapshot-%d.png'
}

def ensure-output-parent [output_path: string] {
  let parent_dir = ($output_path | path dirname)
  if not ($parent_dir | path exists) {
    mkdir $parent_dir
  }
}

def parse-slide-spec [slide_spec: string]: nothing -> record {
  let normalized = ($slide_spec | str trim)
  if ($normalized | is-empty) {
    return {
      ok: false
      message: 'Slide range must not be empty'
      details: {slides: $slide_spec}
    }
  }

  mut slides = []
  for raw_part in ($normalized | split row ',') {
    let part = ($raw_part | str trim)
    if ($part | is-empty) {
      return {
        ok: false
        message: 'Slide range contains an empty segment'
        details: {slides: $slide_spec}
      }
    }

    if ($part =~ '^\d+$') {
      let slide = ($part | into int)
      if $slide <= 0 {
        return {
          ok: false
          message: 'Slide numbers must be >= 1'
          details: {slides: $slide_spec segment: $part}
        }
      }
      $slides = ($slides | append $slide)
    } else if ($part =~ '^\d+-\d+$') {
      let bounds = ($part | split row '-')
      let start = ($bounds | get 0 | into int)
      let end = ($bounds | get 1 | into int)
      if ($start <= 0 or $end <= 0) {
        return {
          ok: false
          message: 'Slide numbers must be >= 1'
          details: {slides: $slide_spec segment: $part}
        }
      }
      if $start > $end {
        return {
          ok: false
          message: 'Slide range start must be <= range end'
          details: {slides: $slide_spec segment: $part start: $start end: $end}
        }
      }
      $slides = ($slides | append ($start..$end))
    } else {
      return {
        ok: false
        message: 'Unsupported slide range syntax'
        details: {
          slides: $slide_spec
          segment: $part
          expected: 'Use comma-separated positive slide numbers and ranges, e.g. 3,5,8-10'
        }
      }
    }
  }

  {
    ok: true
    spec: $normalized
    slides: ($slides | flatten)
  }
}

def output-path-for-slide [output_pattern: string, slide_number: int]: nothing -> string {
  $output_pattern | str replace '%d' ($slide_number | into string)
}

def output-info-for-slides [
  output_pattern: string
  slides: list<int>
]: nothing -> list<record> {
  $slides | each {|slide|
    let output_path = (output-path-for-slide $output_pattern $slide)
    {
      slide: $slide
      output_path: $output_path
      image: (
        if ($output_path | path exists) {
          image-info $output_path
        } else {
          {}
        }
      )
    }
  }
}

def require-pdf-renderer []: nothing -> record {
  if (command-exists 'xdoc') {
    return {ok: true}
  }

  {
    ok: false
    message: '`xdoc` with PDFium support is required for pdf-render mode'
    details: {
      hint: 'Install xdoc with PDFium support or use --method window for single-slide capture'
    }
  }
}

# Bind each PNG to PDFium, the exact executable and the unchanged Office PDF.
def render-pdf-page [pdf: path, page: int, dpi: int, output: path]: nothing -> record {
  if $page < 1 or $dpi < 1 { error make {msg: 'PDF page and DPI must be positive.'} }
  let pdf = ($pdf | path expand --strict)
  let output = ($output | path expand)
  let executable = (which xdoc | where type == external | first | get path | path expand --strict)
  let binary_sha = (open --raw $executable | hash sha256)
  let pdf_sha = (open --raw $pdf | hash sha256)
  let version = (^$executable --version | complete)
  if $version.exit_code != 0 { error make {msg: 'Cannot observe PDF rasterizer version.'} }
  let run = (mktemp --directory --tmpdir-path ($output | path dirname) 'pdf-raster.XXXXXX' | path expand)
  try {
    let rendered_dir = ($run | path join rendered)
    let result = (^$executable pdf render $pdf --pages ($page | into string) --dpi $dpi --output $rendered_dir | complete)
    if $result.exit_code != 0 { error make {msg: $'PDFium rasterization failed: ($result.stderr) ($result.stdout)'} }
    let manifest = (open ($rendered_dir | path join manifest.json))
    let files = $manifest.outputs.png
    if $manifest.input != $pdf or $manifest.pagesSelected != [$page] or ($files | length) != 1 {
      error make {msg: 'PDF rasterizer manifest does not match the requested input/page.'}
    }
    let name = $files.0
    if $name in ['' '.' '..'] or ($name | path basename) != $name {
      error make {msg: 'PDF rasterizer returned an invalid image filename.'}
    }
    let image = ($rendered_dir | path join $name)
    if ($image | path type) != file { error make {msg: 'PDF rasterizer did not create an image file.'} }
    if (open --raw $pdf | hash sha256) != $pdf_sha or (open --raw $executable | hash sha256) != $binary_sha {
      error make {msg: 'PDF input or rasterizer changed during capture.'}
    }
    cp --force $image $output
    {engine: pdfium, executable: $executable, version: ($version.stdout | str trim), binarySha256: $binary_sha, pdfSha256: $pdf_sha}
  } finally {
    rm --recursive $run
  }
}

def powerpoint-container-tmp-root []: nothing -> string {
  $env.HOME | path join 'Library' 'Containers' 'com.microsoft.Powerpoint' 'Data' 'tmp'
}

def cleanup-owned-temp-dir [
  tmp_root: string
  tmp_dir: string
]: nothing -> record {
  let root = ($tmp_root | path expand)
  let target = ($tmp_dir | path expand)
  let basename = ($target | path basename)
  let relative = (
    try {
      $target | path relative-to $root
    } catch {
      null
    }
  )
  let is_owned_child = (
    $relative != null and
    $relative == $basename and
    ($basename =~ '^pptx-snapshot\.[A-Za-z0-9]+$') and
    $target != '/' and
    $target != $nu.home-dir and
    $target != $root
  )

  if not $is_owned_child {
    return {
      removed: []
      failed: [{
        path: $target
        message: 'Refusing to remove a temporary directory not owned by pptx-snapshot'
      }]
    }
  }

  if not ($target | path exists) {
    return {removed: [] failed: []}
  }

  try {
    rm --recursive --force -- $target
    {removed: [$target] failed: []}
  } catch {|err|
    {
      removed: []
      failed: [{
        path: $target
        message: ($err.msg? | default 'Failed to remove the owned temporary directory')
      }]
    }
  }
}

def make-temp-dir-with-timeout [template: string]: nothing -> record {
  let tag = (random int 1..2147483647)
  let job_id = (job spawn --description 'pptx-snapshot mktemp' {
    let result = (^mktemp -d $template | complete)
    $result | job send 0 --tag $tag
  })
  let result = (
    try {
      job recv --tag $tag --timeout 3sec
    } catch {
      null
    }
  )

  if $result == null {
    do -i { job kill $job_id } | ignore
    return {
      exit_code: 124
      stdout: ''
      stderr: 'Timed out while creating a temporary directory'
      timed_out: true
    }
  }

  $result | merge {timed_out: false}
}

def make-window-staging-dir []: nothing -> record {
  let candidate_roots = [($env.TMPDIR? | default '/tmp') '/tmp'] | uniq
  for root in $candidate_roots {
    if not ($root | path exists) {
      continue
    }
    let template = ($root | path join 'pptx-snapshot.XXXXXX')
    let result = (make-temp-dir-with-timeout $template)
    if $result.exit_code == 0 {
      return {
        ok: true
        tmp_dir: ($result.stdout | str trim)
        root: $root
        uses_powerpoint_container: false
      }
    }
  }

  {
    ok: false
    message: 'Failed to create a temporary directory for window capture'
    details: {
      candidates: $candidate_roots
      hint: 'Ensure the system temporary directory is writable'
    }
  }
}

def make-temp-export-dir []: nothing -> record {
  let root = (powerpoint-container-tmp-root)
  if not ($root | path exists) {
    return {
      ok: false
      message: 'The PowerPoint sandbox temporary directory is unavailable'
      details: {
        root: $root
        hint: 'Launch PowerPoint once, or use --method window when sandbox staging is unavailable'
      }
    }
  }

  let template = ($root | path join 'pptx-snapshot.XXXXXX')
  let result = (make-temp-dir-with-timeout $template)
  if $result.exit_code == 0 {
    return {
      ok: true
      tmp_dir: ($result.stdout | str trim)
      root: $root
      uses_powerpoint_container: true
    }
  }

  {
    ok: false
    message: 'Failed to create a PowerPoint sandbox temporary directory'
    details: {
      root: $root
      timed_out: $result.timed_out
      stderr: ($result.stderr | str trim)
      hint: 'Grant App Data access to the terminal/host app, or use --method auto/window'
    }
  }
}

def stage-pptx-for-powerpoint [
  pptx_path: string
]: nothing -> record {
  let tmp_dir_result = (make-temp-export-dir)
  if not $tmp_dir_result.ok {
    return {
      ok: false
      message: $tmp_dir_result.message
      details: $tmp_dir_result.details
    }
  }

  if not $tmp_dir_result.uses_powerpoint_container {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir | ignore
    return {
      ok: false
      message: 'Failed to stage the PPTX inside the PowerPoint sandbox container'
      details: {
        tmp_dir: $tmp_dir_result.tmp_dir
        root: $tmp_dir_result.root
        hint: 'The PowerPoint container tmp directory is required to avoid the macOS Grant File Access prompt'
      }
    }
  }

  let source_name = ($pptx_path | path basename)
  let staged_name = (
    if ($source_name | str ends-with '.pptx') {
      $source_name
    } else {
      'deck.pptx'
    }
  )
  let staged_path = ($tmp_dir_result.tmp_dir | path join $staged_name)
  let source_sha256 = (file-sha256 $pptx_path)
  let copy_result = (^cp $pptx_path $staged_path | complete)

  if ($copy_result.exit_code != 0 or not ($staged_path | path exists)) {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir | ignore
    return {
      ok: false
      message: 'Failed to stage the PPTX inside the PowerPoint container'
      details: {
        tmp_dir: $tmp_dir_result.tmp_dir
        stderr: ($copy_result.stderr | str trim)
        stdout: ($copy_result.stdout | str trim)
      }
    }
  }

  let staged_sha256 = (file-sha256 $staged_path)
  if $staged_sha256 != $source_sha256 {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir | ignore
    return {
      ok: false
      message: 'The staged PPTX does not match the source bytes'
      details: {
        source_sha256: $source_sha256
        staged_sha256: $staged_sha256
      }
    }
  }

  {
    ok: true
    original_path: $pptx_path
    staged_path: $staged_path
    tmp_dir: $tmp_dir_result.tmp_dir
    root: $tmp_dir_result.root
    uses_powerpoint_container: $tmp_dir_result.uses_powerpoint_container
    sha256: $source_sha256
  }
}

def image-info [image_path: string]: nothing -> record {
  let probe = (^sips -g pixelWidth -g pixelHeight $image_path | complete)
  if $probe.exit_code != 0 {
    return {}
  }

  let width_line = (
    $probe.stdout
      | lines
      | where {|line| $line | str contains 'pixelWidth:' }
  )
  let height_line = (
    $probe.stdout
      | lines
      | where {|line| $line | str contains 'pixelHeight:' }
  )
  let raw = (open --raw $image_path)

  {
    pixel_width: (
      if ($width_line | is-empty) {
        null
      } else {
        $width_line | first | split row ':' | last | str trim | into int
      }
    )
    pixel_height: (
      if ($height_line | is-empty) {
        null
      } else {
        $height_line | first | split row ':' | last | str trim | into int
      }
    )
    byte_length: ($raw | bytes length)
    sha256: ($raw | hash sha256)
  }
}

def slide-size [pptx_path: string]: nothing -> record {
  if not (command-exists 'unzip') {
    return {
      ok: false
      message: '`unzip` is required to inspect the slide size for window mode'
      details: {
        hint: 'Install or restore the macOS `unzip` command, or use --method pdf-render'
      }
    }
  }

  let extract = (^unzip -p $pptx_path 'ppt/presentation.xml' | complete)
  if $extract.exit_code != 0 {
    return {
      ok: false
      message: 'Failed to read the slide size from the presentation'
      details: {
        stderr: ($extract.stderr | str trim)
        stdout: ($extract.stdout | str trim)
      }
    }
  }

  let tag_matches = (
    $extract.stdout
      | parse --regex '(?P<tag><[^>]*sldSz[^>]*>)'
  )

  if ($tag_matches | is-empty) {
    return {
      ok: false
      message: 'The presentation slide size could not be determined'
      details: {
        hint: 'The presentation.xml file does not contain a readable <p:sldSz> element'
      }
    }
  }

  let tag = ($tag_matches | first | get tag)
  let width_match = ($tag | parse --regex 'cx="(?P<width>\d+)"')
  let height_match = ($tag | parse --regex 'cy="(?P<height>\d+)"')

  if (($width_match | is-empty) or ($height_match | is-empty)) {
    return {
      ok: false
      message: 'The presentation slide size could not be determined'
      details: {
        tag: $tag
      }
    }
  }

  {
    ok: true
    width: ($width_match | first | get width | into int)
    height: ($height_match | first | get height | into int)
  }
}

def fit-slide-into-box [
  slide_width: int
  slide_height: int
  max_width: int
  max_height: int
]: nothing -> record {
  if ($slide_width <= 0 or $slide_height <= 0 or $max_width <= 0 or $max_height <= 0) {
    return {
      ok: false
      message: 'Window sizing requires positive slide and target dimensions'
      details: {
        slide_width: $slide_width
        slide_height: $slide_height
        max_width: $max_width
        max_height: $max_height
      }
    }
  }

  let width_limited = (($max_width * $slide_height) <= ($max_height * $slide_width))

  if $width_limited {
    {
      ok: true
      width: $max_width
      height: ((($max_width * $slide_height) / $slide_width) | into int)
    }
  } else {
    {
      ok: true
      width: ((($max_height * $slide_width) / $slide_height) | into int)
      height: $max_height
    }
  }
}

def ensure-powerpoint-presentation [
  pptx_path: string
  open_delay: float
  --locate-only
]: nothing -> record {
  let open_lines = (
    if $locate_only {
      []
    } else {
      [
        '      if target_presentation is missing value then'
        '        open POSIX file ppt_path'
        '        delay open_delay'
        '        set pres_count to count of presentations'
        '        repeat with i from 1 to pres_count'
        '          if ((full name of presentation i) as string) is equal to ppt_path then'
        '            set target_presentation to presentation i'
        '            exit repeat'
        '          end if'
        '        end repeat'
        '      end if'
      ]
    }
  )
  let applescript = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  set open_delay to (item 2 of argv) as real'
    '  with timeout of 600 seconds'
    '    tell application "Microsoft PowerPoint"'
    '      launch'
    '      set target_presentation to missing value'
    '      set pres_count to count of presentations'
    '      repeat with i from 1 to pres_count'
    '        if ((full name of presentation i) as string) is equal to ppt_path then'
    '          set target_presentation to presentation i'
    '          exit repeat'
    '        end if'
    '      end repeat'
    ...$open_lines
    '      if target_presentation is missing value then'
    '        error "PowerPoint opened no presentation matching " & ppt_path'
    '      end if'
    '      return name of target_presentation as string'
    '    end tell'
    '  end timeout'
    'end run'
  ] | str join (char nl))

  let result = (
    $applescript
      | ^osascript - $pptx_path ($open_delay | into string)
      | complete
  )

  if $result.exit_code != 0 {
    return {
      ok: false
      message: 'Failed to open the target presentation'
      details: {
        stderr: ($result.stderr | str trim)
        stdout: ($result.stdout | str trim)
      }
    }
  }

  {
    ok: true
    presentation_name: ($result.stdout | str trim)
  }
}

def open-powerpoint-via-launch-services [
  pptx_path: string
  open_delay: float
]: nothing -> record {
  let launch = (^open -a 'Microsoft PowerPoint' $pptx_path | complete)
  if $launch.exit_code != 0 {
    return {
      ok: false
      message: 'Failed to open the target presentation through LaunchServices'
      details: {
        stderr: ($launch.stderr | str trim)
        stdout: ($launch.stdout | str trim)
      }
    }
  }

  sleep ($open_delay * 1sec)
  let located = (ensure-powerpoint-presentation $pptx_path 0.0 --locate-only)
  if not $located.ok {
    return {
      ok: false
      message: 'LaunchServices did not open the target presentation in PowerPoint'
      details: $located.details
    }
  }

  $located
}

def stage-pptx-for-window-capture [
  pptx_path: string
  open_delay: float
]: nothing -> record {
  let tmp_dir_result = (make-window-staging-dir)
  if not $tmp_dir_result.ok {
    return $tmp_dir_result
  }

  let source_name = ($pptx_path | path basename)
  let staged_name = (
    if ($source_name | str ends-with '.pptx') {
      $source_name
    } else {
      'deck.pptx'
    }
  )
  let staged_path = ($tmp_dir_result.tmp_dir | path join $staged_name)
  let source_sha256 = (file-sha256 $pptx_path)
  let copy_result = (^cp $pptx_path $staged_path | complete)
  if ($copy_result.exit_code != 0 or not ($staged_path | path exists)) {
    let cleanup = (cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir)
    return {
      ok: false
      message: 'Failed to stage the PPTX for window capture'
      details: {
        stderr: ($copy_result.stderr | str trim)
        stdout: ($copy_result.stdout | str trim)
        cleanup: $cleanup
      }
    }
  }

  let staged_sha256 = (file-sha256 $staged_path)
  if $staged_sha256 != $source_sha256 {
    let cleanup = (cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir)
    return {
      ok: false
      message: 'The window-capture PPTX copy does not match the source bytes'
      details: {
        source_sha256: $source_sha256
        staged_sha256: $staged_sha256
        cleanup: $cleanup
      }
    }
  }

  let opened = (open-powerpoint-via-launch-services $staged_path $open_delay)
  if not $opened.ok {
    let close_staged = (close-powerpoint-presentation $staged_path)
    let cleanup = (cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir_result.tmp_dir)
    return {
      ok: false
      message: $opened.message
      details: ($opened.details | merge {
        close_staged: $close_staged
        cleanup: $cleanup
      })
    }
  }

  {
    ok: true
    original_path: $pptx_path
    staged_path: $staged_path
    tmp_dir: $tmp_dir_result.tmp_dir
    root: $tmp_dir_result.root
    uses_powerpoint_container: false
    sha256: $source_sha256
  }
}

def setup-slide-show-canvas [
  pptx_path: string
  slide_number: int
  window_left: int
  window_top: int
  canvas_width: int
  canvas_height: int
  open_delay: float
  focus_delay: float
]: nothing -> record {
  let applescript = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  set slide_num to (item 2 of argv) as integer'
    '  set window_left to (item 3 of argv) as integer'
    '  set window_top to (item 4 of argv) as integer'
    '  set canvas_width to (item 5 of argv) as integer'
    '  set canvas_height to (item 6 of argv) as integer'
    '  set open_delay to (item 7 of argv) as real'
    '  set focus_delay to (item 8 of argv) as real'
    '  set tab_char to ASCII character 9'
    '  with timeout of 600 seconds'
    '    tell application "Microsoft PowerPoint"'
    '      set target_presentation to missing value'
    '      set pres_count to count of presentations'
    '      repeat with i from 1 to pres_count'
    '        if ((full name of presentation i) as string) is equal to ppt_path then'
    '          set target_presentation to presentation i'
    '          exit repeat'
    '        end if'
    '      end repeat'
    '      activate'
    '      if target_presentation is missing value then'
    '        open POSIX file ppt_path'
    '        delay open_delay'
    '        set pres_count to count of presentations'
    '        repeat with i from 1 to pres_count'
    '          if ((full name of presentation i) as string) is equal to ppt_path then'
    '            set target_presentation to presentation i'
    '            exit repeat'
    '          end if'
    '        end repeat'
    '      end if'
    '      if target_presentation is missing value then'
    '        error "PowerPoint opened no presentation matching " & ppt_path'
    '      end if'
    '      try'
    '        tell slide show window of target_presentation'
    '          tell slideshow view to exit slide show'
    '        end tell'
    '        delay 0.2'
    '      end try'
    '      tell slide show settings of target_presentation'
    '        set starting slide to slide_num'
    '        set ending slide to slide_num'
    '        set range type to slide show range'
    '        set show type to slide show type window'
    '      end tell'
    '      set slide_show_window to run slide show (slide show settings of target_presentation)'
    '      delay focus_delay'
    '      set presentation_name to (name of target_presentation as string)'
    '    end tell'
    '  end timeout'
    '  tell application "System Events"'
    '    tell process "Microsoft PowerPoint"'
    '      set frontmost to true'
    '      set target_window to window 1'
    '      set position of target_window to {window_left, window_top}'
    '      delay focus_delay'
    '      set layout_area to UI element 1 of target_window'
    '      set window_pos to position of target_window'
    '      set window_size to size of target_window'
    '      set layout_pos to position of layout_area'
    '      set layout_size to size of layout_area'
    '      set horizontal_chrome to (item 1 of window_size) - (item 1 of layout_size)'
    '      set titlebar_height to (item 2 of layout_pos) - (item 2 of window_pos)'
    '      set vertical_chrome to (item 2 of window_size) - titlebar_height - (item 2 of layout_size)'
    '      set size of target_window to {canvas_width + horizontal_chrome, canvas_height + titlebar_height + vertical_chrome}'
    '      delay focus_delay'
    '      set layout_area to UI element 1 of target_window'
    '      set layout_pos to position of layout_area'
    '      set layout_size to size of layout_area'
    '    end tell'
    '  end tell'
    '  tell application "Microsoft PowerPoint"'
    '    set current_slide to slide index of slide of slideshow view of slide_show_window'
    '  end tell'
    '  return presentation_name & tab_char & (current_slide as string) & tab_char & ¬'
    '    (item 1 of layout_pos as string) & tab_char & (item 2 of layout_pos as string) & tab_char & ¬'
    '    (item 1 of layout_size as string) & tab_char & (item 2 of layout_size as string)'
    'end run'
  ] | str join (char nl))

  let result = (
    $applescript
      | ^osascript - $pptx_path ($slide_number | into string) ($window_left | into string) ($window_top | into string) ($canvas_width | into string) ($canvas_height | into string) ($open_delay | into string) ($focus_delay | into string)
      | complete
  )

  if $result.exit_code != 0 {
    return {
      ok: false
      message: 'Failed to open a slide-show window for canvas capture'
      details: {
        stderr: ($result.stderr | str trim)
        stdout: ($result.stdout | str trim)
        hint: 'Grant Accessibility permission to the terminal/host app, or use --method pdf-render'
      }
    }
  }

  let fields = ($result.stdout | str trim | split row (char tab))
  if (($fields | length) != 6) {
    return {
      ok: false
      message: 'Slide-show setup returned an unexpected response'
      details: {
        stdout: ($result.stdout | str trim)
      }
    }
  }

  let left = ($fields | get 2 | into int)
  let top = ($fields | get 3 | into int)
  let width = ($fields | get 4 | into int)
  let height = ($fields | get 5 | into int)

  {
    ok: true
    presentation_name: ($fields | get 0)
    slide: ($fields | get 1 | into int)
    canvas: {
      left: $left
      top: $top
      width: $width
      height: $height
      right: ($left + $width)
      bottom: ($top + $height)
    }
  }
}

def inspect-slide-show-capture-state [
  pptx_path: string
]: nothing -> record {
  let applescript = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  set tab_char to ASCII character 9'
    '  with timeout of 600 seconds'
    '    tell application "Microsoft PowerPoint"'
    '      set target_presentation to missing value'
    '      set pres_count to count of presentations'
    '      repeat with i from 1 to pres_count'
    '        if ((full name of presentation i) as string) is equal to ppt_path then'
    '          set target_presentation to presentation i'
    '          exit repeat'
    '        end if'
    '      end repeat'
    '      if target_presentation is missing value then'
    '        error "PowerPoint has no open presentation matching " & ppt_path'
    '      end if'
    '      set presentation_name to (name of target_presentation as string)'
    '      set presentation_path to ((full name of target_presentation) as string)'
    '      set slide_show_window to slide show window of target_presentation'
    '      set current_slide to slide index of slide of slideshow view of slide_show_window'
    '    end tell'
    '  end timeout'
    '  tell application "System Events"'
    '    set front_process to first application process whose frontmost is true'
    '    set front_process_name to name of front_process as string'
    '    tell process "Microsoft PowerPoint"'
    '      set target_window to window 1'
    '      set window_title to name of target_window as string'
    '      set layout_area to UI element 1 of target_window'
    '      set layout_pos to position of layout_area'
    '      set layout_size to size of layout_area'
    '    end tell'
    '  end tell'
    '  return front_process_name & tab_char & window_title & tab_char & presentation_name & tab_char & presentation_path & tab_char & ¬'
    '    (current_slide as string) & tab_char & (item 1 of layout_pos as string) & tab_char & (item 2 of layout_pos as string) & tab_char & ¬'
    '    (item 1 of layout_size as string) & tab_char & (item 2 of layout_size as string)'
    'end run'
  ] | str join (char nl))

  let result = ($applescript | ^osascript - $pptx_path | complete)
  if $result.exit_code != 0 {
    return {
      ok: false
      message: 'Failed to inspect the live PowerPoint slide-show capture state'
      details: {
        stderr: ($result.stderr | str trim)
        stdout: ($result.stdout | str trim)
      }
    }
  }

  let fields = ($result.stdout | str trim | split row (char tab))
  if (($fields | length) != 9) {
    return {
      ok: false
      message: 'PowerPoint capture-state inspection returned an unexpected response'
      details: {stdout: ($result.stdout | str trim)}
    }
  }

  let left = ($fields | get 5 | into int)
  let top = ($fields | get 6 | into int)
  let width = ($fields | get 7 | into int)
  let height = ($fields | get 8 | into int)
  {
    ok: true
    frontmost_process: ($fields | get 0)
    window_title: ($fields | get 1)
    presentation_name: ($fields | get 2)
    presentation_path: ($fields | get 3)
    slide: ($fields | get 4 | into int)
    canvas: {
      left: $left
      top: $top
      width: $width
      height: $height
      right: ($left + $width)
      bottom: ($top + $height)
    }
  }
}

def number-near [actual: int, expected: int, tolerance: int = 2]: nothing -> bool {
  (($actual - $expected) | math abs) <= $tolerance
}

def canvas-matches [actual: record, expected: record]: nothing -> bool {
  (
    (number-near $actual.left $expected.left) and
    (number-near $actual.top $expected.top) and
    (number-near $actual.width $expected.width) and
    (number-near $actual.height $expected.height)
  )
}

def validate-window-observation [
  observation: record
  expected_pptx_path: string
  expected_slide: int
  expected_canvas: record
  phase: string
]: nothing -> list<record> {
  mut issues = []
  if not $observation.ok {
    return [{
      code: 'capture-state-unavailable'
      phase: $phase
      message: ($observation.message? | default 'Capture state is unavailable')
      details: ($observation.details? | default {})
    }]
  }

  let expected_name = ($expected_pptx_path | path basename)
  let expected_title_token = ($expected_pptx_path | path parse | get stem | str lowercase)
  let actual_title = ($observation.window_title | str lowercase)
  if $observation.frontmost_process != 'Microsoft PowerPoint' {
    $issues = ($issues | append {
      code: 'frontmost-process-mismatch'
      phase: $phase
      expected: 'Microsoft PowerPoint'
      actual: $observation.frontmost_process
    })
  }
  if $observation.presentation_path != $expected_pptx_path {
    $issues = ($issues | append {
      code: 'presentation-path-mismatch'
      phase: $phase
      expected: $expected_pptx_path
      actual: $observation.presentation_path
    })
  }
  if $observation.presentation_name != $expected_name {
    $issues = ($issues | append {
      code: 'presentation-name-mismatch'
      phase: $phase
      expected: $expected_name
      actual: $observation.presentation_name
    })
  }
  if not ($actual_title | str contains $expected_title_token) {
    $issues = ($issues | append {
      code: 'window-title-mismatch'
      phase: $phase
      expected_contains: $expected_title_token
      actual: $observation.window_title
    })
  }
  if $observation.slide != $expected_slide {
    $issues = ($issues | append {
      code: 'slide-mismatch'
      phase: $phase
      expected: $expected_slide
      actual: $observation.slide
    })
  }
  if ($observation.canvas.width <= 0 or $observation.canvas.height <= 0) {
    $issues = ($issues | append {
      code: 'canvas-invalid'
      phase: $phase
      actual: $observation.canvas
    })
  } else if not (canvas-matches $observation.canvas $expected_canvas) {
    $issues = ($issues | append {
      code: 'canvas-mismatch'
      phase: $phase
      expected: $expected_canvas
      actual: $observation.canvas
    })
  }
  $issues
}

def validate-window-capture-state [
  expected_pptx_path: string
  expected_slide: int
  expected_canvas: record
  before: record
  after: record
  image: record
]: nothing -> record {
  mut issues = (
    (validate-window-observation $before $expected_pptx_path $expected_slide $expected_canvas 'before')
      | append (validate-window-observation $after $expected_pptx_path $expected_slide $expected_canvas 'after')
  )

  if ($before.ok and $after.ok and not (canvas-matches $after.canvas $before.canvas)) {
    $issues = ($issues | append {
      code: 'canvas-changed-during-capture'
      before: $before.canvas
      after: $after.canvas
    })
  }

  let pixel_width = ($image.pixel_width? | default 0)
  let pixel_height = ($image.pixel_height? | default 0)
  mut scale = 0.0
  mut scale_available = false
  if ($pixel_width <= 0 or $pixel_height <= 0) {
    $issues = ($issues | append {code: 'image-dimensions-missing' image: $image})
  } else {
    let scale_x = ($pixel_width / $expected_canvas.width)
    let scale_y = ($pixel_height / $expected_canvas.height)
    $scale = $scale_x
    $scale_available = true
    let ratios_match = ((($scale_x - $scale_y) | math abs) <= 0.02)
    let scale_valid = ($scale_x >= 1.0 and $scale_x <= 4.0)
    let width_matches = (((($expected_canvas.width * $scale_x) - $pixel_width) | math abs) <= 2.0)
    let height_matches = (((($expected_canvas.height * $scale_x) - $pixel_height) | math abs) <= 2.0)
    if not ($ratios_match and $scale_valid and $width_matches and $height_matches) {
      $issues = ($issues | append {
        code: 'image-canvas-scale-mismatch'
        canvas: $expected_canvas
        image: {pixel_width: $pixel_width pixel_height: $pixel_height}
        scale_x: $scale_x
        scale_y: $scale_y
      })
    }
  }

  {
    ok: ($issues | is-empty)
    issues: $issues
    scale: (if $scale_available { $scale } else { null })
  }
}

def close-slide-show-window [pptx_path: string]: nothing -> record {
  let applescript = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  tell application "Microsoft PowerPoint"'
    '    set pres_count to count of presentations'
    '    repeat with i from 1 to pres_count'
    '      if ((full name of presentation i) as string) is equal to ppt_path then'
    '        try'
    '          tell slide show window of presentation i'
    '            tell slideshow view to exit slide show'
    '          end tell'
    '        end try'
    '        exit repeat'
    '      end if'
    '    end repeat'
    '  end tell'
    'end run'
  ] | str join (char nl))

  let result = ($applescript | ^osascript - $pptx_path | complete)
  {
    ok: ($result.exit_code == 0)
    stderr: ($result.stderr | str trim)
    stdout: ($result.stdout | str trim)
  }
}

def close-powerpoint-presentation [pptx_path: string]: nothing -> record {
  let applescript = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  tell application "Microsoft PowerPoint"'
    '    set pres_count to count of presentations'
    '    repeat with i from pres_count to 1 by -1'
    '      if ((full name of presentation i) as string) is equal to ppt_path then'
    '        close presentation i saving no'
    '      end if'
    '    end repeat'
    '  end tell'
    'end run'
  ] | str join (char nl))

  let result = ($applescript | ^osascript - $pptx_path | complete)
  {
    ok: ($result.exit_code == 0)
    stderr: ($result.stderr | str trim)
    stdout: ($result.stdout | str trim)
  }
}

def export-presentation-to-pdf [
  pptx_path: string
  pdf_path: string
  tmp_dir_result: record
]: nothing -> record {
  let export_script = ([
    'on run argv'
    '  set ppt_path to item 1 of argv'
    '  set pdf_path to item 2 of argv'
    '  with timeout of 600 seconds'
    '    tell application "Microsoft PowerPoint"'
    '      set target_presentation to missing value'
    '      set pres_count to count of presentations'
    '      repeat with i from 1 to pres_count'
    '        if ((full name of presentation i) as string) is equal to ppt_path then'
    '          set target_presentation to presentation i'
    '          exit repeat'
    '        end if'
    '      end repeat'
    '      if target_presentation is missing value then'
    '        error "PowerPoint has no open presentation matching " & ppt_path'
    '      end if'
    '      save target_presentation in POSIX file pdf_path as save as PDF'
    '      return pdf_path'
    '    end tell'
    '  end timeout'
    'end run'
  ] | str join (char nl))

  let export_result = ($export_script | ^osascript - $pptx_path $pdf_path | complete)
  if ($export_result.exit_code != 0 or not ($pdf_path | path exists)) {
    return {
      ok: false
      message: 'Failed to export the presentation to PDF'
      details: {
        export_root: $tmp_dir_result.root
        uses_powerpoint_container: $tmp_dir_result.uses_powerpoint_container
        stderr: ($export_result.stderr | str trim)
        stdout: ($export_result.stdout | str trim)
      }
    }
  }

  {
    ok: true
    pdf_path: $pdf_path
  }
}

def capture-window-screenshot [
  pptx_path: string
  slide_number: int
  output_path: string
  window_left: int
  window_top: int
  window_width: int
  window_height: int
  open_delay: float
  focus_delay: float
]: nothing -> record {
  let slide_size = (slide-size $pptx_path)
  if not $slide_size.ok {
    return $slide_size
  }

  let canvas_size = (fit-slide-into-box $slide_size.width $slide_size.height $window_width $window_height)
  if not $canvas_size.ok {
    return $canvas_size
  }

  let slide_show = (
    setup-slide-show-canvas $pptx_path $slide_number $window_left $window_top $canvas_size.width $canvas_size.height $open_delay $focus_delay
  )
  if not $slide_show.ok {
    return $slide_show
  }

  let before = (inspect-slide-show-capture-state $pptx_path)
  let before_issues = (
    validate-window-observation $before $pptx_path $slide_number $slide_show.canvas 'before'
  )
  if not ($before_issues | is-empty) {
    let cleanup = (close-slide-show-window $pptx_path)
    return {
      ok: false
      message: 'PowerPoint window capture preconditions are not trustworthy'
      details: {
        issues: $before_issues
        observation: $before
        cleanup_ok: $cleanup.ok
        cleanup_stderr: $cleanup.stderr
      }
    }
  }

  if ($output_path | path exists) {
    rm --force $output_path
  }

  let rect = $"($slide_show.canvas.left),($slide_show.canvas.top),($slide_show.canvas.width),($slide_show.canvas.height)"
  let result = (^screencapture -x -R $rect $output_path | complete)
  let after = (inspect-slide-show-capture-state $pptx_path)
  let image = (
    if ($output_path | path exists) {
      image-info $output_path
    } else {
      {}
    }
  )
  let validation = (
    validate-window-capture-state $pptx_path $slide_number $slide_show.canvas $before $after $image
  )
  let cleanup = (close-slide-show-window $pptx_path)

  if ($result.exit_code != 0 or not ($output_path | path exists)) {
    return {
      ok: false
      message: 'Slide-show canvas screenshot failed'
      details: {
        rect: $rect
        stderr: ($result.stderr | str trim)
        stdout: ($result.stdout | str trim)
        cleanup_ok: $cleanup.ok
        cleanup_stderr: $cleanup.stderr
        hint: 'Grant Screen Recording permission to the terminal/host app, or use --method pdf-render'
      }
    }
  }

  if not $validation.ok {
    rm --force $output_path
    return {
      ok: false
      message: 'PowerPoint window capture identity changed or could not be verified'
      details: {
        rect: $rect
        issues: $validation.issues
        before: $before
        after: $after
        image: $image
        cleanup_ok: $cleanup.ok
        cleanup_stderr: $cleanup.stderr
        hint: 'Use --method pdf-render for candidate-bound PowerPoint rendering evidence'
      }
    }
  }

  {
    ok: true
    method: 'window'
    rect: $rect
    presentation_name: $slide_show.presentation_name
    slide: $slide_show.slide
    canvas_width: $slide_show.canvas.width
    canvas_height: $slide_show.canvas.height
    window: {
      title: $after.window_title
      frontmost_process: $after.frontmost_process
      presentation_path: $after.presentation_path
      canvas: $after.canvas
      scale: $validation.scale
    }
    cleanup_ok: $cleanup.ok
  }
}

# PowerPoint may include or omit hidden slides in its PDF export. Verify which
# sequence was exported before interpreting the user's logical slide numbers.
def resolve-pdf-slide-pages [
  slides: list<record>
  pdf_page_count: int
  requested: list<int>
]: nothing -> list<record> {
  let visible = $slides | where {|slide| not $slide.hidden}
  let exported = if $pdf_page_count == ($slides | length) {
    $slides
  } else if $pdf_page_count == ($visible | length) {
    $visible
  } else {
    error make {msg: 'Exported PDF page count does not match all or visible slides'}
  }
  let mapping = $exported | enumerate | each {|entry| $entry.item | insert pdf_page ($entry.index + 1)}
  $requested | each {|slide|
    let found = $mapping | where slide == $slide
    if ($found | length) != 1 {
      error make {msg: $'Slide ($slide) is absent from the exported PDF; it may be hidden'}
    }
    $found | first
  }
}

def render-via-pdf [
  pptx_path: string
  output_target: string
  slide_selection: record
  dpi: int
  open_delay: float
]: nothing -> record {
  let renderer_check = (require-pdf-renderer)
  if not $renderer_check.ok {
    return $renderer_check
  }

  if ($slide_selection.multi and not ($output_target | str contains '%d')) {
    return {
      ok: false
      message: 'Multi-slide output requires `%d` in the output path'
      details: {
        output_path: $output_target
        hint: 'Use a pattern such as .tmp/snapshot-%d.png'
      }
    }
  }

  let tmp_dir_result = (make-temp-export-dir)
  if not $tmp_dir_result.ok {
    return {
      ok: false
      message: $tmp_dir_result.message
      details: $tmp_dir_result.details
    }
  }

  let tmp_dir = $tmp_dir_result.tmp_dir
  let tmp_pdf = ($tmp_dir | path join 'slides.pdf')
  let open_result = (ensure-powerpoint-presentation $pptx_path $open_delay)

  if not $open_result.ok {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir | ignore
    return $open_result
  }

  let export_result = (export-presentation-to-pdf $pptx_path $tmp_pdf $tmp_dir_result)
  if not $export_result.ok {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir | ignore
    return $export_result
  }

  let requested = if $slide_selection.multi { $slide_selection.slides } else { [$slide_selection.slide] }
  let identity = try {
    let source = ^node $SLIDE_VISIBILITY_TOOL $pptx_path | complete
    if $source.exit_code != 0 { error make {msg: $source.stderr} }
    let count = ^xdoc pdf inspect $tmp_pdf --json | complete
    if $count.exit_code != 0 { error make {msg: $count.stderr} }
    let pdf_page_count = $count.stdout | from json | get pageCount | into int
    let pages = resolve-pdf-slide-pages ($source.stdout | from json) $pdf_page_count $requested
    {ok: true pages: $pages pdf_page_count: $pdf_page_count}
  } catch {|err|
    {ok: false message: 'Cannot establish logical slide identity in the exported PDF' details: {reason: $err.msg}}
  }
  if not $identity.ok {
    cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir | ignore
    return $identity
  }

  let target_outputs = (
    if $slide_selection.multi {
      $slide_selection.slides | each {|slide| output-path-for-slide $output_target $slide }
    } else {
      [$output_target]
    }
  )
  # Stage every requested PDF page before publishing logical slide filenames.
  # PDFium avoids MuPDF dropping or enlarging valid rotated glyphs.
  let staged_pattern = $tmp_dir | path join 'page-%d.png'
  let draw_result = try {
    mut rasterizers: list<record> = []
    for page in ($identity.pages.pdf_page | uniq) {
      let current = (render-pdf-page $tmp_pdf $page $dpi (output-path-for-slide $staged_pattern $page))
      if not ($rasterizers | is-empty) and $rasterizers.0 != $current {
        error make {msg: 'PDF rasterizer identity changed during capture.'}
      }
      $rasterizers = ($rasterizers | append $current)
    }
    {exit_code: 0 stdout: '' stderr: '' rasterizer: $rasterizers.0}
  } catch {|err|
    {exit_code: 1 stdout: '' stderr: $err.msg rasterizer: null}
  }
  let staged = $identity.pages | each {|page| output-path-for-slide $staged_pattern $page.pdf_page}
  let all_rendered = $staged | all {|path| $path | path exists}
  if $draw_result.exit_code == 0 and $all_rendered {
    for pair in ($staged | zip $target_outputs) {
      cp --force $pair.0 $pair.1
    }
  }
  cleanup-owned-temp-dir $tmp_dir_result.root $tmp_dir | ignore

  let outputs = (
    if $slide_selection.multi {
      output-info-for-slides $output_target $slide_selection.slides
    } else {
      [{
        slide: $slide_selection.slide
        output_path: $output_target
        image: (
          if ($output_target | path exists) {
            image-info $output_target
          } else {
            {}
          }
        )
      }]
    }
  )
  let missing_outputs = (
    $outputs | where {|item| not ($item.output_path | path exists) }
  )
  if ($draw_result.exit_code != 0 or not $all_rendered or not ($missing_outputs | is-empty)) {
    return {
      ok: false
      message: (
        if $slide_selection.multi {
          'Failed to render one or more slides from the exported PDF'
        } else {
          'Failed to render the slide from the exported PDF'
        }
      )
      details: {
        export_root: $tmp_dir_result.root
        uses_powerpoint_container: $tmp_dir_result.uses_powerpoint_container
        missing_outputs: $missing_outputs
        stderr: ($draw_result.stderr | str trim)
        stdout: ($draw_result.stdout | str trim)
      }
    }
  }

  {
    ok: true
    method: 'pdf-render'
    pdf_page_count: $identity.pdf_page_count
    pdf_pages: $identity.pages
    rasterizer: $draw_result.rasterizer
    presentation_name: $open_result.presentation_name
    slide: (
      if $slide_selection.multi {
        null
      } else {
        $slide_selection.slide
      }
    )
    slide_spec: (
      if $slide_selection.multi {
        $slide_selection.spec
      } else {
        null
      }
    )
    slides: (
      if $slide_selection.multi {
        $slide_selection.slides
      } else {
        null
      }
    )
    dpi: $dpi
    outputs: (
      if $slide_selection.multi {
        $outputs
      } else {
        null
      }
    )
    export_root: $tmp_dir_result.root
    uses_powerpoint_container: $tmp_dir_result.uses_powerpoint_container
  }
}

def emit-success [payload: record, --json] {
  if $json {
    print ($payload | to json --raw)
    return
  }

  if ($payload.slides? != null) {
    print $'Saved slides ($payload.slide_spec) snapshots to ($payload.output_pattern)'
  } else {
    print $'Saved slide ($payload.slide) snapshot to ($payload.output_path)'
  }
  print $'Method: ($payload.method)'
  if ($payload.fallback? != null) {
    print $'Fallback: ($payload.fallback.from) -> ($payload.fallback.to)'
  }
  if ($payload.image? != null and $payload.image.pixel_width? != null and $payload.image.pixel_height? != null) {
    print $'Image: ($payload.image.pixel_width)x($payload.image.pixel_height)'
  }
}

def emit-error [message: string, details: record, --json] {
  let payload = {
    status: 'error'
    message: $message
    details: $details
  }

  if $json {
    print ($payload | to json --raw)
  } else {
    print $'Error: ($message)'
    if (($details | columns | length) > 0) {
      print ($details | to json --raw)
    }
  }

  exit 1
}

def failure [message: string, details: record = {}]: nothing -> record {
  {
    status: 'error'
    message: $message
    details: $details
  }
}

def acquire-lock [lock_dir: string]: nothing -> record {
  let result = (^mkdir $lock_dir | complete)
  if $result.exit_code != 0 {
    return {
      ok: false
      message: 'Another pptx-snapshot invocation is already running'
      details: {
        lock_dir: $lock_dir
        stderr: ($result.stderr | str trim)
        hint: 'Run the script serially, or remove the stale lock directory if no snapshot job is active'
      }
    }
  }

  {
    ok: true
    lock_dir: $lock_dir
  }
}

def release-lock [lock_dir: string] {
  if ($lock_dir | path exists) {
    rm --recursive --force $lock_dir
  }
}

def resolve-slide-selection [
  positional_slide: any
  flag_slide: any
  slide_spec: any
  --json
]: nothing -> record {
  if $slide_spec != null {
    if ($flag_slide != null or $positional_slide != null) {
      emit-error 'Conflicting slide arguments were provided' {
        slides: $slide_spec
        flag_slide: $flag_slide
        positional_slide: $positional_slide
        hint: 'Use either --slides for multi-slide capture or --slide/positional slide_number for single-slide capture'
      } --json=$json
    }

    let parsed_slides = (parse-slide-spec $slide_spec)
    if not $parsed_slides.ok {
      emit-error $parsed_slides.message $parsed_slides.details --json=$json
    }

    return ($parsed_slides | merge {
      multi: true
      slide: null
    })
  }

  let chosen_slide = (
    if ($flag_slide != null and $positional_slide != null and $flag_slide != $positional_slide) {
      emit-error 'Conflicting slide numbers were provided' {
        flag_slide: $flag_slide
        positional_slide: $positional_slide
      } --json=$json
    } else if $flag_slide != null {
      $flag_slide
    } else if $positional_slide != null {
      $positional_slide
    } else {
      1
    }
  )

  if $chosen_slide <= 0 {
    emit-error 'Slide number must be >= 1' {slide: $chosen_slide} --json=$json
  }

  {
    ok: true
    multi: false
    spec: ($chosen_slide | into string)
    slide: $chosen_slide
    slides: [$chosen_slide]
  }
}

def resolve-output-target [
  pptx_path: string
  output_path: any
  slide_selection: record
  --json
]: nothing -> string {
  let output_target = (
    if $slide_selection.multi {
      ($output_path | default (default-output-pattern $pptx_path)) | path expand
    } else {
      ($output_path | default (default-output-path $pptx_path $slide_selection.slide)) | path expand
    }
  )

  if ($slide_selection.multi and not ($output_target | str contains '%d')) {
    emit-error 'Multi-slide output requires `%d` in the output path' {
      output_path: $output_target
      hint: 'Use a pattern such as .tmp/snapshot-%d.png'
    } --json=$json
  }

  ensure-output-parent $output_target
  $output_target
}

def capture-as-failure [
  capture: record
  method_name: string
]: nothing -> record {
  if $capture.ok {
    $capture
  } else {
    failure $capture.message ($capture.details | merge {method: $method_name})
  }
}

def capture-by-method [
  method_name: string
  pptx_path: string
  output_target: string
  slide_selection: record
  window_left: int
  window_top: int
  window_width: int
  window_height: int
  open_delay: float
  focus_delay: float
  dpi: int
]: nothing -> record {
  if $slide_selection.multi {
    return (
      capture-as-failure
        (render-via-pdf $pptx_path $output_target $slide_selection $dpi $open_delay)
        'pdf-render'
    )
  }

  match $method_name {
    window => {
      capture-as-failure (
        capture-window-screenshot
          $pptx_path
          $slide_selection.slide
          $output_target
          $window_left
          $window_top
          $window_width
          $window_height
          $open_delay
          $focus_delay
      ) 'window'
    }
    pdf-render => {
      capture-as-failure (
        render-via-pdf $pptx_path $output_target $slide_selection $dpi $open_delay
      ) 'pdf-render'
    }
    auto => {
      let pdf_capture = (
        render-via-pdf $pptx_path $output_target $slide_selection $dpi $open_delay
      )
      if $pdf_capture.ok {
        $pdf_capture
      } else {
        let window_capture = (
          capture-window-screenshot
            $pptx_path
            $slide_selection.slide
            $output_target
            $window_left
            $window_top
            $window_width
            $window_height
            $open_delay
            $focus_delay
        )
        if not $window_capture.ok {
          failure 'Both snapshot methods failed' {
            pdf_error: $pdf_capture.details
            window_error: $window_capture.details
          }
        } else {
          $window_capture | merge {
            fallback: {
              from: 'pdf-render'
              to: 'window'
              reason: $pdf_capture.message
              details: $pdf_capture.details
            }
          }
        }
      }
    }
    _ => {
      failure 'Unsupported method' {method: $method_name allowed: [auto window pdf-render]}
    }
  }
}

def snapshot-result [
  pptx_path: string
  pptx_sha256: string
  output_target: string
  slide_selection: record
  capture: record
]: nothing -> record {
  if ($capture.status? | default null) == 'error' {
    return $capture
  }

  {
    schema_version: 'pptx-snapshot/v1'
    status: 'ok'
    method: $capture.method
    pptx_path: $pptx_path
    pptx_sha256: $pptx_sha256
    presentation_name: ($capture.presentation_name? | default null)
    slide: ($capture.slide? | default null)
    slide_spec: ($capture.slide_spec? | default null)
    slides: ($capture.slides? | default null)
    output_path: (
      if $slide_selection.multi {
        null
      } else {
        $output_target
      }
    )
    output_pattern: (
      if $slide_selection.multi {
        $output_target
      } else {
        null
      }
    )
    outputs: ($capture.outputs? | default null)
    pdf_page_count: ($capture.pdf_page_count? | default null)
    pdf_pages: ($capture.pdf_pages? | default null)
    rasterizer: ($capture.rasterizer? | default null)
    window: ($capture.window? | default null)
    image: (
      if $slide_selection.multi {
        null
      } else {
        image-info $output_target
      }
    )
    fallback: ($capture.fallback? | default null)
  }
}

def main [
  pptx_file: string                # Path to the .pptx file
  slide_number?: int               # 1-based slide number
  --slide (-s): int                # 1-based slide number (preferred for agents)
  --slides: string                 # Comma-separated slide numbers and ranges, e.g. 3,5,8-10
  --out (-o): string               # Output png path
  --method (-m): string = 'pdf-render' # pdf-render | auto | window
  --window-left: int = 80          # PowerPoint window left position
  --window-top: int = 60           # PowerPoint window top position
  --window-width: int = 1440       # PowerPoint window width
  --window-height: int = 900       # PowerPoint window height
  --open-delay: float = 2.0        # Delay after opening the file
  --focus-delay: float = 1.0       # Delay after switching slides
  --dpi: int = 200                 # Render DPI for pdf-render
  --json                           # Emit machine-readable JSON
] {
  if (sys host | get name) != 'Darwin' {
    emit-error 'This script only supports macOS' {} --json=$json
  }

  if not (command-exists 'osascript') {
    emit-error '`osascript` is required but not available' {} --json=$json
  }

  let slide_selection = (resolve-slide-selection $slide_number $slide $slides --json=$json)

  let normalized_method = ($method | str lowercase)
  if ($normalized_method not-in ['auto' 'window' 'pdf-render']) {
    emit-error 'Unsupported method' {method: $method allowed: ['auto' 'window' 'pdf-render']} --json=$json
  }

  if ($slide_selection.multi and $normalized_method == 'window') {
    emit-error 'Window capture mode only supports a single slide' {
      method: $method
      slides: $slide_selection.spec
      hint: 'Use --method pdf-render or --method auto for multi-slide capture'
    } --json=$json
  }

  let pptx_path = ($pptx_file | path expand --no-symlink)
  if not ($pptx_path | path exists) {
    emit-error 'PPTX file not found' {pptx_path: $pptx_path} --json=$json
  }

  let output_target = (resolve-output-target $pptx_path $out $slide_selection --json=$json)

  let powerpoint_check = (^osascript -e 'id of application "Microsoft PowerPoint"' | complete)
  if $powerpoint_check.exit_code != 0 {
    emit-error 'Microsoft PowerPoint is not installed or not scriptable' {
      stderr: ($powerpoint_check.stderr | str trim)
      stdout: ($powerpoint_check.stdout | str trim)
    } --json=$json
  }

  let lock_dir = '/tmp/pptx-snapshot.lock'
  let lock = (acquire-lock $lock_dir)
  if not $lock.ok {
    emit-error $lock.message $lock.details --json=$json
  }

  let prepared = (
    if $normalized_method == 'window' {
      let staged = (stage-pptx-for-window-capture $pptx_path $open_delay)
      if not $staged.ok {
        $staged
      } else {
        $staged | merge {
          capture_method: 'window'
          preparation_fallback: null
        }
      }
    } else {
      let staged = (stage-pptx-for-powerpoint $pptx_path)
      if $staged.ok {
        $staged | merge {
          capture_method: $normalized_method
          preparation_fallback: null
        }
      } else if ($normalized_method == 'auto' and not $slide_selection.multi) {
        let window_staged = (stage-pptx-for-window-capture $pptx_path $open_delay)
        if not $window_staged.ok {
          $staged
        } else {
          $window_staged | merge {
            capture_method: 'window'
            preparation_fallback: {
              from: 'pdf-render'
              to: 'window'
              reason: $staged.message
              details: $staged.details
            }
          }
        }
      } else {
        $staged
      }
    }
  )
  if not $prepared.ok {
    release-lock $lock_dir
    emit-error $prepared.message $prepared.details --json=$json
  }

  let result = (do {
    let powerpoint_pptx_path = $prepared.staged_path
    let capture = (
      capture-by-method
        $prepared.capture_method
        $powerpoint_pptx_path
        $output_target
        $slide_selection
        $window_left
        $window_top
        $window_width
        $window_height
        $open_delay
        $focus_delay
        $dpi
    )
    let capture_with_fallback = (
      if (
        $prepared.preparation_fallback != null and
        ($capture.status? | default null) != 'error'
      ) {
        $capture | merge {fallback: $prepared.preparation_fallback}
      } else {
        $capture
      }
    )

    snapshot-result $pptx_path $prepared.sha256 $output_target $slide_selection $capture_with_fallback
  })
  let close_staged = (close-powerpoint-presentation $prepared.staged_path)
  let staged_tmp_cleanup = (
    if $prepared.tmp_dir == null {
      {removed: [] failed: []}
    } else {
      cleanup-owned-temp-dir $prepared.root $prepared.tmp_dir
    }
  )

  release-lock $lock_dir

  if $result.status == 'ok' {
    emit-success ($result | merge {
      staged_tmp_cleanup: $staged_tmp_cleanup
      close_staged: $close_staged
    }) --json=$json
  } else {
    emit-error $result.message ($result.details | merge {
      staged_tmp_cleanup: $staged_tmp_cleanup
      close_staged: $close_staged
    }) --json=$json
  }
}
