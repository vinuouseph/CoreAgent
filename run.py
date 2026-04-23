#!/usr/bin/env python3
"""
CoreAgent-2 — Convenience Launcher
Run with: python run.py
"""
import os
import subprocess
import sys

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_entry = os.path.join(project_root, "app", "main.py")

    if not os.path.exists(app_entry):
        print(f"Error: Could not find {app_entry}")
        sys.exit(1)

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"

    print("🧊 Starting CoreAgent-2 ...")
    try:
        subprocess.run(
            ["streamlit", "run", app_entry,
             "--server.headless", "true",
             "--theme.base", "dark"],
            env=env, check=True,
        )
    except KeyboardInterrupt:
        print("\n⏹  Shutting down CoreAgent-2.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
