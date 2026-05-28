#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Funnel chart drawing wrapper script - use R first, automatically switch to Python if failed
Usage: python run_funnel_plot.py <csv_path> <type> [outcome_name] [output_dir]"""

import sys
import os
import subprocess
import platform

def run_r_script(csv_path, data_type, outcome_name, output_dir):
    """Try using an R script"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        r_script = os.path.join(script_dir, 'funnel_plot.R')
        
        cmd = ['Rscript', r_script, csv_path, data_type]
        if outcome_name:
            cmd.append(outcome_name)
        if output_dir:
            cmd.append(output_dir)
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=120)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print("[R script execution failed and automatically switched to Python]", file=sys.stderr)
            if result.stderr:
                print(result.stderr[:200], file=sys.stderr)
            return False
    except FileNotFoundError:
        print("[Rscript not found, automatically switched to Python]", file=sys.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("[R script execution times out and automatically switches to Python]", file=sys.stderr)
        return False
    except Exception as e:
        print(f"【RScript execution exception，automatically switch toPython】", file=sys.stderr)
        return False

def run_python_script(csv_path, data_type, outcome_name, output_dir):
    """Using Python script"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        py_script = os.path.join(script_dir, 'funnel_plot.py')
        
        cmd = [sys.executable, py_script, csv_path, data_type]
        if outcome_name:
            cmd.append(outcome_name)
        if output_dir:
            cmd.append(output_dir)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        print(result.stdout)
        
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"PythonScript execution failed: {e}", file=sys.stderr)
        return False

def main():
    """main program"""
    if len(sys.argv) < 3:
        print("Usage: python run_funnel_plot.py <csv_path> <type> [outcome_name] [output_dir]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    data_type = sys.argv[2]
    outcome_name = sys.argv[3] if len(sys.argv) > 3 else ""
    output_dir = sys.argv[4] if len(sys.argv) > 4 else ""
    
    # Validate input
    if not os.path.exists(csv_path):
        print(f"mistake: File does not exist: {csv_path}")
        sys.exit(1)
    
    if data_type not in ["Binary", "Continuity", "Survival"]:
        print("Error: type must be Binary, Continuity or Survival")
        sys.exit(1)
    
    # Try R script first
    print("[Try using R script for plotting...]", file=sys.stderr)
    if run_r_script(csv_path, data_type, outcome_name, output_dir):
        sys.exit(0)
    
    # R script fails, switch to Python
    print("[Using Python script for drawing...]", file=sys.stderr)
    if run_python_script(csv_path, data_type, outcome_name, output_dir):
        sys.exit(0)
    else:
        print("Error: Both methods failed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
