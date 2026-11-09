#Requires -Version 7.0
<# UIA worker. run_uia.py supplies a hard deadline and a durable per-run journal. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][int]$TargetPid,
    [Parameter(Mandatory)][string]$Executable,
    [string]$WindowName,
    [switch]$Inspect,
    [switch]$Probe,
    [string]$StepsFile,
    [ValidateRange(0.05, 60)][double]$WaitSeconds = 5,
    [ValidateRange(1, 10000)][int]$MaxNodes = 400,
    [ValidateRange(0, 100)][int]$InspectDepth = 0,
    [string]$JournalPath,
    [string]$RunId
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$timer = [Diagnostics.Stopwatch]::StartNew()
$completedSteps = [Collections.Generic.List[object]]::new()
$diagnostics = @{ selector_queries = 0; elements_returned = 0 }
$report = [ordered]@{ ok = $false; status = 'failed'; steps = $completedSteps; diagnostics = $diagnostics }
$journalWriter = $null

function Write-RouterEvent([string]$Event, $Fields) {
    if (-not $journalWriter) { return }
    $item = [ordered]@{ run_id = $RunId; event = $Event; time = [DateTimeOffset]::UtcNow.ToString('o') }
    foreach ($key in $Fields.Keys) { $item[$key] = $Fields[$key] }
    $journalWriter.WriteLine(($item | ConvertTo-Json -Depth 14 -Compress))
    $journalWriter.Flush()
    $journalWriter.BaseStream.Flush($true)
}

try {
    if ($JournalPath) {
        $journalWriter = [IO.StreamWriter]::new($JournalPath, $true, [Text.UTF8Encoding]::new($false))
    }
    Add-Type -AssemblyName UIAutomationClient
    Add-Type -AssemblyName UIAutomationTypes
    . (Join-Path $PSScriptRoot 'uia_windows.ps1')
    $expectedPath = (Resolve-Path -LiteralPath $Executable).Path
    $initialProcess = Get-Process -Id $TargetPid
    $processBirth = $initialProcess.StartTime.Ticks

    function Assert-Target {
        $currentProcess = Get-Process -Id $TargetPid
        if (-not [string]::Equals($currentProcess.Path, $expectedPath, [StringComparison]::OrdinalIgnoreCase) -or
            $currentProcess.StartTime.Ticks -ne $processBirth) {
            throw 'TARGET_MISMATCH: PID, process start time and executable must identify the same target.'
        }
    }

    function Get-Window([string]$ExactName) {
        Assert-Target
        $windows = Get-RouterWindows @($TargetPid) $ExactName
        if ($windows.Count -gt 1) { throw 'AMBIGUOUS_WINDOW: pass an exact --window or per-step window name.' }
        if ($windows.Count -eq 1) { return $windows[0].element }
        return $null
    }

    function Get-Elements($Root) {
        $queue = [Collections.Generic.Queue[object]]::new()
        $items = [Collections.Generic.List[object]]::new()
        $queue.Enqueue(@{ element = $Root; depth = 0 })
        $report.depth_limited = $false
        while ($queue.Count -gt 0) {
            $entry = $queue.Dequeue()
            if ($items.Count -ge $MaxNodes) { throw 'NODE_LIMIT: narrow inspection with --inspect-depth or increase --max-nodes.' }
            if ($entry.element.Current.ProcessId -ne $TargetPid) { continue }
            $items.Add($entry)
            if ($InspectDepth -gt 0 -and $entry.depth -ge $InspectDepth) { $report.depth_limited = $true; continue }
            $children = $entry.element.FindAll([System.Windows.Automation.TreeScope]::Children,
                [System.Windows.Automation.Condition]::TrueCondition)
            foreach ($child in $children) { $queue.Enqueue(@{ element = $child; depth = $entry.depth + 1 }) }
        }
        return ,$items
    }

    function Get-Field($Element, [string]$Property) {
        switch ($Property) {
            'name' { return $Element.Current.Name }
            'enabled' { return $Element.Current.IsEnabled }
            'value' {
                $pattern = $null
                if (-not $Element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) {
                    throw 'UNSUPPORTED_PATTERN: ValuePattern is unavailable.'
                }
                if ($Element.Current.IsPassword) { throw 'PASSWORD_FIELD: values are not read or reported.' }
                return $pattern.Current.Value
            }
            default { throw "INVALID_PLAN: unsupported property $Property; use name, value or enabled." }
        }
    }

    function Assert-Selector($Selector) {
        if ($Selector -isnot [Collections.IDictionary] -or $Selector.Count -eq 0) { throw 'INVALID_PLAN: an explicit selector object is required.' }
        foreach ($key in $Selector.Keys) {
            if ($key -notin @('name', 'automation_id', 'control_type', 'class_name') -or
                $Selector[$key] -isnot [string] -or [string]::IsNullOrEmpty($Selector[$key])) {
                throw "INVALID_PLAN: selector field $key must be a known key with a nonempty string value."
            }
        }
        if ($Selector.Contains('control_type')) {
            $field = [System.Windows.Automation.ControlType].GetField($Selector.control_type)
            if (-not $field -or $field.FieldType -ne [System.Windows.Automation.ControlType]) { throw 'INVALID_PLAN: unknown control_type.' }
        }
    }

    function Find-Selector($Root, $Selector) {
        $properties = @{
            name = [System.Windows.Automation.AutomationElement]::NameProperty
            automation_id = [System.Windows.Automation.AutomationElement]::AutomationIdProperty
            control_type = [System.Windows.Automation.AutomationElement]::ControlTypeProperty
            class_name = [System.Windows.Automation.AutomationElement]::ClassNameProperty
        }
        $conditions = [Collections.Generic.List[System.Windows.Automation.Condition]]::new()
        $conditions.Add([System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $TargetPid))
        $conditions.Add([System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::IsOffscreenProperty, $false))
        foreach ($key in $Selector.Keys) {
            $value = $Selector[$key]
            if ($key -eq 'control_type') { $value = [System.Windows.Automation.ControlType].GetField($value).GetValue($null) }
            $conditions.Add([System.Windows.Automation.PropertyCondition]::new($properties[$key], $value))
        }
        $condition = [System.Windows.Automation.AndCondition]::new($conditions.ToArray())
        $matches = $Root.FindAll([System.Windows.Automation.TreeScope]::Subtree, $condition)
        $diagnostics.selector_queries++
        $diagnostics.elements_returned += $matches.Count
        if ($matches.Count -gt 1) { throw "AMBIGUOUS_SELECTOR: matched $($matches.Count) controls; refine selector or within scope." }
        if ($matches.Count -eq 1) { return $matches[0] }
        return $null
    }

    function Wait-ForTarget($Step) {
        $clock = [Diagnostics.Stopwatch]::StartNew()
        $lastObserved = $null
        $title = $WindowName
        if ($Step -and $Step.ContainsKey('window')) { $title = $Step.window }
        do {
            try {
                $window = Get-Window $title
                if ($window) {
                    if ($null -eq $Step) { return @{ element = $window } }
                    $scope = $window
                    foreach ($ancestor in $Step.within) {
                        $scope = Find-Selector $scope $ancestor
                        if (-not $scope) { break }
                    }
                    if ($scope) {
                        $element = Find-Selector $scope $Step.selector
                        if ($element) {
                            if ($Step.action -eq 'wait') {
                                $lastObserved = Get-Field $element $Step.property
                                if ($lastObserved -ceq $Step.equals) {
                                    return @{ element = $element; observed = $lastObserved; observed_at = [DateTimeOffset]::UtcNow.ToString('o') }
                                }
                            } elseif ($element.Current.IsEnabled) { return @{ element = $element } }
                        }
                    }
                }
            } catch [System.Windows.Automation.ElementNotAvailableException] {
                # Only discovery/reads are retried; actions are dispatched once.
            }
            Start-Sleep -Milliseconds 50
        } while ($clock.Elapsed.TotalSeconds -lt $WaitSeconds)
        throw "TIMEOUT: no unique ready target or expected state within $WaitSeconds seconds; last observed: $lastObserved"
    }

    Assert-Target
    if ($Probe) {
        $probeResult = Find-RouterWindowOwner $TargetPid $WindowName $WaitSeconds
        foreach ($key in $probeResult.Keys) { $report[$key] = $probeResult[$key] }
    } elseif ($Inspect) {
        $found = Wait-ForTarget $null
        $records = [Collections.Generic.List[object]]::new()
        foreach ($entry in (Get-Elements $found.element)) {
            $info = $entry.element.Current
            $records.Add([ordered]@{
                name = $info.Name; automation_id = $info.AutomationId; depth = $entry.depth
                control_type = $info.ControlType.ProgrammaticName.Replace('ControlType.', '')
                class_name = $info.ClassName; enabled = $info.IsEnabled; offscreen = $info.IsOffscreen
                password = $info.IsPassword
                patterns = @($entry.element.GetSupportedPatterns() | ForEach-Object { $_.ProgrammaticName })
            })
        }
        $report.elements = $records
    } else {
        if (-not $StepsFile) { throw 'INVALID_PLAN: supply --steps, --inspect or --probe.' }
        $plan = Get-Content -LiteralPath $StepsFile -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable
        if ($plan.steps -isnot [array] -or $plan.steps.Count -eq 0) { throw 'INVALID_PLAN: steps must be a nonempty array.' }
        # Validate the whole plan before the first action, including all nested scopes.
        foreach ($step in $plan.steps) {
            if ($step -isnot [Collections.IDictionary] -or $step.action -notin @('set', 'invoke', 'wait')) { throw 'INVALID_PLAN: action must be set, invoke or wait.' }
            Assert-Selector $step.selector
            if ($step.ContainsKey('window') -and ($step.window -isnot [string] -or [string]::IsNullOrEmpty($step.window))) { throw 'INVALID_PLAN: window must be a nonempty string.' }
            if ($step.ContainsKey('within')) {
                if ($step.within -is [Collections.IDictionary]) { $step.within = @($step.within) }
                if ($step.within -isnot [array] -or $step.within.Count -eq 0) { throw 'INVALID_PLAN: within must be a selector or nonempty selector array.' }
                foreach ($scope in $step.within) { Assert-Selector $scope }
            } else { $step.within = @() }
            if ($step.action -eq 'set' -and (-not $step.ContainsKey('value') -or $step.value -isnot [string])) { throw 'INVALID_PLAN: set needs a string value.' }
            if ($step.action -eq 'wait') {
                if ($step.property -notin @('name', 'value', 'enabled') -or -not $step.ContainsKey('equals')) { throw 'INVALID_PLAN: wait needs a property and equals.' }
                if ($step.property -eq 'enabled' -and $step.equals -isnot [bool]) { throw 'INVALID_PLAN: enabled requires a JSON boolean equals value.' }
                if ($step.property -in @('name', 'value') -and $step.equals -isnot [string]) { throw 'INVALID_PLAN: name and value require a string equals value.' }
            }
        }
        for ($index = 0; $index -lt $plan.steps.Count; $index++) {
            $step = $plan.steps[$index]
            Write-RouterEvent 'step_started' @{ index = $index; action = $step.action; selector = $step.selector }
            $stepClock = [Diagnostics.Stopwatch]::StartNew()
            $found = Wait-ForTarget $step
            $element = $found.element
            Assert-Target
            $record = [ordered]@{ action = $step.action; selector = $step.selector; status = 'dispatched' }
            if ($step.within.Count) { $record.within = $step.within }
            if ($step.ContainsKey('window')) { $record.window = $step.window }
            switch ($step.action) {
                'set' {
                    $pattern = $null
                    if ($element.Current.IsPassword) { throw 'PASSWORD_FIELD: this helper does not write password fields.' }
                    if (-not $element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) { throw 'UNSUPPORTED_PATTERN: ValuePattern is unavailable.' }
                    if ($pattern.Current.IsReadOnly) { throw 'READ_ONLY: selected value cannot be changed.' }
                    Write-RouterEvent 'action_started' @{ index = $index }
                    $pattern.SetValue($step.value)
                }
                'invoke' {
                    $pattern = $null
                    if (-not $element.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$pattern)) { throw 'UNSUPPORTED_PATTERN: InvokePattern is unavailable.' }
                    Write-RouterEvent 'action_started' @{ index = $index }
                    $pattern.Invoke()
                }
                'wait' {
                    $record.status = 'asserted'
                    $record.observed = $found.observed
                    $record.observed_at = $found.observed_at
                }
            }
            $record.elapsed_ms = [Math]::Round($stepClock.Elapsed.TotalMilliseconds, 2)
            Write-RouterEvent 'step_completed' @{ index = $index; record = $record }
            $completedSteps.Add($record)
        }
    }
    if (-not $Probe) { $report.ok = $true; $report.status = 'completed' }
    Write-RouterEvent 'run_finished' @{ status = $report.status }
} catch {
    $report.error = $_.Exception.Message
} finally {
    if ($journalWriter) { $journalWriter.Dispose() }
}
$report.backend_ms = [Math]::Round($timer.Elapsed.TotalMilliseconds, 2)
$report | ConvertTo-Json -Depth 14 -Compress
if (-not $report.ok) { exit 1 }
