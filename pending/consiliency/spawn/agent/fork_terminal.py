#!/usr/bin/env python3

import os
import platform
import shlex
import shutil
import subprocess
import time
import uuid
from typing import Optional


def fork_terminal(command: str, cwd: Optional[str] = None, capture: bool = False, log_to_file: bool = False, log_agent_output: bool = True) -> str:
    """
    Fork a new terminal window and run the specified command.
    - macOS: Terminal.app via osascript
    - Windows: Windows Terminal via wt.exe
    - WSL/Linux: tmux new-window or default terminal in WSL/Linux

    Args:
        command: The command to run in the new terminal
        cwd: Working directory (defaults to current directory)
        capture: If True, block and return output content directly
        log_to_file: If True, log full terminal output (debug) to file
        log_agent_output: If True (default), log clean agent output to JSON file

    Returns:
        If capture=True: The output content (blocks until complete)
        If log_agent_output=True: Path to agent JSON output file
        If log_to_file=True and not log_agent_output: Path to debug output file
        Otherwise: Empty string
    """

    system = platform.system().lower()

    cwd = cwd or os.getcwd()

    if system == "darwin":
        # macOS: use osascript to open a new Terminal window
        output_id = str(uuid.uuid4())[:8]
        agent_output_file = f"/tmp/fork-agent-{output_id}.json" if log_agent_output else None
        debug_output_file = f"/tmp/fork-debug-{output_id}.txt" if log_to_file else None
        done_file = f"/tmp/fork-output-{output_id}.done"

        if log_agent_output:
            shell_cmd = f"cd {cwd}; {command} | tee {agent_output_file}; touch {done_file}"
        elif log_to_file:
            shell_cmd = f"cd {cwd}; {command} 2>&1 | tee {debug_output_file}; touch {done_file}"
        else:
            shell_cmd = f"cd {cwd}; {command}"

        osa_script = f'''
        tell application "Terminal"
            activate
            do script "{shell_cmd}"
        end tell
        '''
        subprocess.run(
            ["osascript", "-e", osa_script],
            capture_output=True, text=True
        )

        if capture and (log_agent_output or log_to_file):
            output_file = agent_output_file or debug_output_file
            return read_fork_output(output_file)
        elif log_agent_output:
            return agent_output_file
        elif log_to_file:
            return debug_output_file
        else:
            return ""

    elif system == "windows":
        # Windows: use Windows Terminal (wt.exe)
        # -w new = new window
        # powershell by default, but we can run bash if WSL specific
        output_id = str(uuid.uuid4())[:8]
        agent_output_file = f"$env:TEMP\\fork-agent-{output_id}.json" if log_agent_output else None
        debug_output_file = f"$env:TEMP\\fork-debug-{output_id}.txt" if log_to_file else None
        done_file = f"$env:TEMP\\fork-output-{output_id}.done"

        if log_agent_output:
            ps_cmd = f"cd {shlex.quote(cwd)}; {command} | Tee-Object -FilePath {agent_output_file}; New-Item -Path {done_file} -ItemType File"
        elif log_to_file:
            ps_cmd = f"cd {shlex.quote(cwd)}; {command} 2>&1 | Tee-Object -FilePath {debug_output_file}; New-Item -Path {done_file} -ItemType File"
        else:
            ps_cmd = f"cd {shlex.quote(cwd)}; {command}"

        wt_cmd = [
            "wt.exe", "-w", "new", "powershell.exe",
            "-NoExit", "-Command", ps_cmd
        ]
        subprocess.Popen(wt_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Note: Windows output capture is limited - return path but blocking read not fully supported
        temp_dir = os.environ.get("TEMP", "C:\\Temp")
        if log_agent_output:
            return agent_output_file.replace("$env:TEMP", temp_dir)
        elif log_to_file:
            return debug_output_file.replace("$env:TEMP", temp_dir)
        else:
            return ""

    else:
        # Detect if running under WSL
        try:
            # WSL populates /proc/version with "Microsoft"
            with open("/proc/version", "r") as f:
                proc = f.read().lower()
            is_wsl = "microsoft" in proc
        except:
            is_wsl = False

        if is_wsl:
            # Try wt.exe in PATH first
            wt_path = shutil.which("wt.exe")

            # Try common Windows Terminal locations if not in PATH
            if not wt_path:
                import glob
                common_paths = [
                    "/mnt/c/Users/*/AppData/Local/Microsoft/WindowsApps/wt.exe",
                    "/mnt/c/Program Files/WindowsApps/Microsoft.WindowsTerminal_*/wt.exe",
                ]
                for pattern in common_paths:
                    matches = glob.glob(pattern)
                    if matches:
                        wt_path = matches[0]
                        break

            if wt_path:
                # Use '--' before wsl.exe to tell wt.exe the remaining args are the command
                output_id = str(uuid.uuid4())[:8]
                agent_output_file = f"/tmp/fork-agent-{output_id}.json" if log_agent_output else None
                debug_output_file = f"/tmp/fork-debug-{output_id}.txt" if log_to_file else None
                done_file = f"/tmp/fork-output-{output_id}.done"
                script_file = f"/tmp/fork-script-{output_id}.sh"

                if log_agent_output:
                    script_content = f'''#!/bin/bash -li
{command} | tee {agent_output_file}
touch {done_file}
exec bash
'''
                elif log_to_file:
                    script_content = f'''#!/bin/bash -li
{command} 2>&1 | tee {debug_output_file}
touch {done_file}
exec bash
'''
                else:
                    script_content = f'''#!/bin/bash -li
{command}
exec bash
'''

                with open(script_file, 'w') as f:
                    f.write(script_content)
                os.chmod(script_file, 0o755)
                wt_cmd = [wt_path, "-w", "new", "--", "wsl.exe", script_file]
                subprocess.Popen(wt_cmd)

                if capture and (log_agent_output or log_to_file):
                    output_file = agent_output_file or debug_output_file
                    return read_fork_output(output_file)
                elif log_agent_output:
                    return agent_output_file
                elif log_to_file:
                    return debug_output_file
                else:
                    return ""

            # Fallback: use cmd.exe to start a new window with WSL
            # Use 'wsl -- command' which passes args directly to default shell
            # Note: log_to_file not supported in this fallback path
            subprocess.run(f"cmd.exe /c 'start cmd /k wsl -- {command}'", shell=True)
            return ""

        # Otherwise use tmux to spawn a new pane/window
        tmux = shutil.which("tmux")
        if tmux:
            output_id = str(uuid.uuid4())[:8]
            agent_output_file = f"/tmp/fork-agent-{output_id}.json" if log_agent_output else None
            debug_output_file = f"/tmp/fork-debug-{output_id}.txt" if log_to_file else None
            done_file = f"/tmp/fork-output-{output_id}.done"

            if log_agent_output:
                wrapped_cmd = f"{command} | tee {agent_output_file}; touch {done_file}"
                tmux_cmd = ["tmux", "new-window", "-c", cwd, "bash", "-li", "-c", wrapped_cmd]
            elif log_to_file:
                wrapped_cmd = f"{command} 2>&1 | tee {debug_output_file}; touch {done_file}"
                tmux_cmd = ["tmux", "new-window", "-c", cwd, "bash", "-li", "-c", wrapped_cmd]
            else:
                tmux_cmd = ["tmux", "new-window", "-c", cwd, command]

            subprocess.Popen(tmux_cmd)

            if capture and (log_agent_output or log_to_file):
                output_file = agent_output_file or debug_output_file
                return read_fork_output(output_file)
            elif log_agent_output:
                return agent_output_file
            elif log_to_file:
                return debug_output_file
            else:
                return ""

        # Fallback: spawn background process in same terminal
        output_id = str(uuid.uuid4())[:8]
        agent_output_file = f"/tmp/fork-agent-{output_id}.json" if log_agent_output else None
        debug_output_file = f"/tmp/fork-debug-{output_id}.txt" if log_to_file else None
        done_file = f"/tmp/fork-output-{output_id}.done"

        if log_agent_output:
            wrapped_cmd = f"{command} | tee {agent_output_file}; touch {done_file}"
            subprocess.Popen(wrapped_cmd, shell=True, cwd=cwd)
            if capture:
                return read_fork_output(agent_output_file)
            return agent_output_file
        elif log_to_file:
            wrapped_cmd = f"{command} 2>&1 | tee {debug_output_file}; touch {done_file}"
            subprocess.Popen(wrapped_cmd, shell=True, cwd=cwd)
            if capture:
                return read_fork_output(debug_output_file)
            return debug_output_file
        else:
            subprocess.Popen(command, shell=True, cwd=cwd)
            return ""


def fork_for_auth(provider: str, cwd: Optional[str] = None) -> bool:
    """
    Fork a terminal for user authentication with an AI provider.

    This is used as a fallback when native Task agents encounter auth failures.
    The user authenticates in the spawned terminal, closes it, and the caller
    can then retry the native agent invocation.

    Args:
        provider: The AI provider requiring auth ("codex", "gemini", "cursor")
        cwd: Working directory (defaults to current directory)

    Returns:
        True when terminal closes (user completed auth flow)
    """
    login_commands = {
        "codex": "codex login",
        "gemini": "gemini auth login",
        "cursor": "cursor-agent login",
        "claude": "claude auth login",
    }

    if provider not in login_commands:
        raise ValueError(f"Unknown provider: {provider}. Valid: {list(login_commands.keys())}")

    command = login_commands[provider]

    # Fork terminal with the login command
    # Use log_to_file to track when terminal closes
    output_file = fork_terminal(command, cwd=cwd, log_to_file=True)

    if output_file:
        # Wait for the .done file to appear (terminal closed)
        done_file = output_file.replace('-debug-', '-output-').replace('.txt', '.done')

        # Poll for completion (max 5 minutes for auth)
        start = time.time()
        timeout = 300  # 5 minutes
        while not os.path.exists(done_file):
            if time.time() - start > timeout:
                return False  # Timeout waiting for auth
            time.sleep(1)

        return True

    return False


AUTH_FAILURE_PATTERNS = {
    "codex": ["please log in", "authentication required", "not authenticated"],
    "gemini": ["please authenticate", "run `gemini auth`", "not logged in"],
    "cursor": ["please log in", "login required", "authentication needed"],
}


def detect_auth_failure(output: str, provider: Optional[str] = None) -> Optional[str]:
    """
    Detect if output indicates an authentication failure.

    Args:
        output: The output from a CLI command
        provider: Optional provider to check. If None, checks all providers.

    Returns:
        The provider name if auth failure detected, None otherwise
    """
    output_lower = output.lower()

    providers_to_check = [provider] if provider else AUTH_FAILURE_PATTERNS.keys()

    for prov in providers_to_check:
        if prov in AUTH_FAILURE_PATTERNS:
            for pattern in AUTH_FAILURE_PATTERNS[prov]:
                if pattern in output_lower:
                    return prov

    return None


def read_fork_output(output_file: str, timeout: int = 30) -> str:
    """
    Wait for a forked terminal command to complete and return its output.

    Args:
        output_file: Path returned by fork_terminal (either .json or .txt)
        timeout: Maximum seconds to wait for command completion

    Returns:
        The captured output from the forked terminal command
    """
    # Extract base path and find done file
    if output_file.endswith('.json'):
        done_file = output_file.replace('-agent-', '-output-').replace('.json', '.done')
    else:
        done_file = output_file.replace('-debug-', '-output-').replace('.txt', '.done')

    start = time.time()
    while not os.path.exists(done_file):
        if time.time() - start > timeout:
            # Check if we have partial output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    partial = f.read()
                return f"[Timeout after {timeout}s - partial output:]\n{partial}"
            return f"[Timeout after {timeout}s waiting for command to complete]"
        time.sleep(0.5)

    with open(output_file, 'r') as f:
        return f.read()
