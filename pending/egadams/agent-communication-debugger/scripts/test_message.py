#!/usr/bin/env python3
"""
Test message sending and receiving for agent communication system.

This script sends a test message to the orchestrator and waits for a response,
helping diagnose communication issues.
"""
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "rich",
# ]
# ///

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
PLANNER_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLANNER_ROOT))

try:
    from rich.console import Console
    from rich.panel import Panel
except ImportError:
    print("Error: rich package not available. Install with: pip install rich")
    sys.exit(1)

try:
    from a2a_communicating_agents.agent_messaging import post_message, inbox
except ImportError as e:
    print(f"Error importing agent messaging: {e}")
    print("Make sure you're running from the project root.")
    sys.exit(1)

console = Console()


def test_message_delivery():
    """Test sending a message and checking for responses."""

    console.print(Panel.fit(
        "[bold cyan]Agent Communication Test[/bold cyan]\n"
        "Testing message delivery to orchestrator...",
        border_style="cyan"
    ))

    # Test message
    test_msg = "System health check - this is a test message from agent-debug skill"
    test_agent = "debug-test-agent"

    # Step 1: Send test message
    console.print("\n[bold]Step 1:[/bold] Sending test message to orchestrator topic...")
    try:
        post_message(
            message=test_msg,
            topic="orchestrator",
            from_agent=test_agent,
            to_agent="board"
        )
        console.print("[green]✓[/green] Message sent successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to send message: {e}")
        return False

    # Step 2: Wait a moment for processing
    console.print("\n[bold]Step 2:[/bold] Waiting for orchestrator to process (5 seconds)...")
    time.sleep(5)

    # Step 3: Check for responses
    console.print("\n[bold]Step 3:[/bold] Checking for responses on orchestrator topic...")
    try:
        messages = inbox("orchestrator", limit=10, render=False)

        if not messages:
            console.print("[yellow]⚠[/yellow] No messages found in orchestrator topic")
            console.print("This could mean:")
            console.print("  - Orchestrator is not running")
            console.print("  - Transport layer has issues")
            console.print("  - Messages are being stored elsewhere")
            return False

        console.print(f"[green]✓[/green] Found {len(messages)} messages in orchestrator topic")

        # Look for our test message and responses
        found_test = False
        found_response = False

        for msg in messages:
            sender = getattr(msg, "sender", "unknown")
            content = getattr(msg, "content", "")

            if test_agent in sender and test_msg in content:
                found_test = True
                console.print(f"  [green]✓[/green] Found our test message")

            if "orchestrator" in sender.lower() and "test" in content.lower():
                found_response = True
                console.print(f"  [green]✓[/green] Found orchestrator response:")
                console.print(f"    {content[:100]}...")

        if not found_test:
            console.print("  [yellow]⚠[/yellow] Our test message not visible yet (may be processed)")

        if not found_response:
            console.print("  [yellow]⚠[/yellow] No response from orchestrator yet")
            console.print("  This could mean:")
            console.print("    - Orchestrator is not running")
            console.print("    - Orchestrator couldn't route the message")
            console.print("    - Response delay (wait longer)")

        return found_response

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to check messages: {e}")
        import traceback
        console.print(traceback.format_exc())
        return False


def check_agent_status():
    """Check which agents are currently running."""
    import subprocess

    console.print("\n[bold]Step 4:[/bold] Checking agent process status...")

    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = result.stdout.split("\n")
        agent_processes = [
            line for line in lines
            if any(x in line for x in ["orchestrator_agent", "coder_agent", "tester_agent", "websocket_server"])
            and "grep" not in line
        ]

        if agent_processes:
            console.print(f"[green]✓[/green] Found {len(agent_processes)} agent process(es) running:")
            for proc in agent_processes:
                # Extract key info
                parts = proc.split()
                if len(parts) >= 11:
                    cmd = " ".join(parts[10:])
                    console.print(f"  - {cmd[:80]}")
        else:
            console.print("[red]✗[/red] No agent processes found running")
            console.print("Expected processes:")
            console.print("  - orchestrator_agent/main.py")
            console.print("  - coder_agent/main.py")
            console.print("  - tester_agent/main.py (optional)")
            console.print("  - websocket_server.py (if using WebSocket)")
            return False

        return True

    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Could not check processes: {e}")
        return None


def main():
    """Run the complete test suite."""
    console.print("\n" + "="*60)
    console.print("[bold cyan]A2A Agent Communication Test Suite[/bold cyan]")
    console.print("="*60 + "\n")

    # Run tests
    delivery_ok = test_message_delivery()
    status_ok = check_agent_status()

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)

    if delivery_ok and status_ok:
        console.print(Panel(
            "[bold green]✓ All tests passed![/bold green]\n\n"
            "The agent communication system appears to be working correctly.\n"
            "Messages are being delivered and orchestrator is responding.",
            border_style="green",
            title="Success"
        ))
        return 0
    elif not status_ok:
        console.print(Panel(
            "[bold red]✗ Agents not running[/bold red]\n\n"
            "No agent processes detected. Start the agents first:\n"
            "  cd a2a_communicating_agents\n"
            "  ./start_orchestrator.sh\n"
            "  ./start_coder_agent.sh",
            border_style="red",
            title="Failed"
        ))
        return 1
    elif not delivery_ok:
        console.print(Panel(
            "[bold yellow]⚠ Communication issues detected[/bold yellow]\n\n"
            "Agents are running but messages may not be flowing correctly.\n"
            "Check:\n"
            "  - Agent logs in logs/ directory\n"
            "  - Transport connectivity (WebSocket or RAG board)\n"
            "  - API keys are set (OPENAI_API_KEY)",
            border_style="yellow",
            title="Warning"
        ))
        return 1
    else:
        console.print(Panel(
            "[bold yellow]⚠ Partial success[/bold yellow]\n\n"
            "Some tests passed but not all. Review the output above.",
            border_style="yellow",
            title="Partial"
        ))
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
