# Read-only native enumeration also finds owned dialogs and independent windows.
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class RouterWindows {
    public struct Window { public IntPtr Handle; public int Pid; }
    private delegate bool EnumCallback(IntPtr handle, IntPtr param);
    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumCallback callback, IntPtr param);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr handle, out int pid);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr handle);
    public static Window[] Find(int[] processIds) {
        var wanted = new HashSet<int>(processIds);
        var found = new List<Window>();
        EnumWindows(delegate(IntPtr handle, IntPtr param) {
            int pid; GetWindowThreadProcessId(handle, out pid);
            if (wanted.Contains(pid) && IsWindowVisible(handle)) found.Add(new Window { Handle=handle, Pid=pid });
            return true;
        }, IntPtr.Zero);
        return found.ToArray();
    }
}
'@

function Get-RouterWindows([int[]]$ProcessIds, [string]$ExactName) {
    if (-not $script:routerProxiesInitialized) {
        # A scoped desktop FindAll initializes .NET UIA client-side proxies. A first
        # FromHandle call alone exposes legacy WinForms controls as empty HWND panes.
        $initialCondition = [System.Windows.Automation.PropertyCondition]::new(
            [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $ProcessIds[0])
        $null = [System.Windows.Automation.AutomationElement]::RootElement.FindAll(
            [System.Windows.Automation.TreeScope]::Children, $initialCondition)
        $script:routerProxiesInitialized = $true
    }
    $items = [Collections.Generic.List[object]]::new()
    foreach ($entry in [RouterWindows]::Find($ProcessIds)) {
        try {
            $element = [System.Windows.Automation.AutomationElement]::FromHandle($entry.Handle)
            $info = $element.Current
            if ($info.ProcessId -ne $entry.Pid -or $info.IsOffscreen) { continue }
            if ($ExactName -and $info.Name -cne $ExactName) { continue }
            $items.Add(@{ element = $element; pid = $entry.Pid; handle = $entry.Handle.ToInt64(); name = $info.Name })
        } catch [System.Windows.Automation.ElementNotAvailableException] { }
    }
    return ,$items
}

function Find-RouterWindowOwner([int]$RootPid, [string]$ExactName, [double]$TimeoutSeconds) {
    $clock = [Diagnostics.Stopwatch]::StartNew()
    $processes = @()
    do {
        Assert-Target
        $snapshot = @(Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId, CreationDate)
        $rootInfo = $snapshot | Where-Object { $_.ProcessId -eq $RootPid } | Select-Object -First 1
        if (-not $rootInfo) { throw 'TARGET_EXITED: launcher exited during probe.' }
        $queue = [Collections.Generic.Queue[object]]::new()
        $queue.Enqueue($rootInfo)
        $members = [Collections.Generic.Dictionary[int,object]]::new()
        while ($queue.Count -gt 0) {
            $entry = $queue.Dequeue()
            if ($members.ContainsKey([int]$entry.ProcessId)) { continue }
            if ($members.Count -ge 64) { throw 'PROBE_LIMIT: more than 64 related processes; narrow the launcher.' }
            try { $running = Get-Process -Id $entry.ProcessId -ErrorAction Stop } catch { continue }
            # Exclude stale parent IDs and processes which disappeared during the snapshot.
            if ([Math]::Abs(($running.StartTime.ToUniversalTime() - $entry.CreationDate.ToUniversalTime()).TotalMilliseconds) -gt 2) { continue }
            $members[[int]$entry.ProcessId] = [ordered]@{
                pid = [int]$entry.ProcessId; parent_pid = [int]$entry.ParentProcessId; executable = $running.Path
                started_at = $running.StartTime.ToUniversalTime().ToString('o'); start_ticks = $running.StartTime.ToUniversalTime().Ticks
            }
            foreach ($child in $snapshot) {
                if ($child.ParentProcessId -eq $entry.ProcessId -and $child.CreationDate -ge $entry.CreationDate) { $queue.Enqueue($child) }
            }
        }
        $processes = @($members.Values)
        $windows = Get-RouterWindows ([int[]]@($members.Keys)) $ExactName
        $observed = [Collections.Generic.List[object]]::new()
        foreach ($window in $windows) {
            $identity = $members[[int]$window.pid]
            try { $running = Get-Process -Id $window.pid -ErrorAction Stop } catch { continue }
            if ($running.StartTime.ToUniversalTime().Ticks -ne $identity.start_ticks -or
                -not [string]::Equals($running.Path, $identity.executable, [StringComparison]::OrdinalIgnoreCase)) { continue }
            $observed.Add(@{ pid = $window.pid; name = $window.name; handle = $window.handle })
        }
        Assert-Target
        $owners = @($observed | ForEach-Object { $_.pid } | Sort-Object -Unique)
        if ($owners.Count -eq 1 -and $members[[int]$owners[0]].executable) {
            return @{ ok = $true; status = 'completed'; mode = 'probe'; target = $members[[int]$owners[0]]; windows = @($observed); processes = $processes }
        }
        if ($owners.Count -gt 1) {
            return @{ ok = $false; status = 'ambiguous'; mode = 'probe'; target = $null; windows = @($observed); processes = $processes;
                error = 'AMBIGUOUS_OWNER: multiple related processes own matching windows; refine --window or choose an explicit PID.' }
        }
        Start-Sleep -Milliseconds 100
    } while ($clock.Elapsed.TotalSeconds -lt $TimeoutSeconds)
    return @{ ok = $false; status = 'no_window'; mode = 'probe'; target = $null; windows = @(); processes = $processes;
        error = 'NO_WINDOW: no visible verified owner found within the probe deadline.' }
}
