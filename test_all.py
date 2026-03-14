import subprocess
import sys
import os

def run_step(name, cmd, cwd="."):
    print(f"\n>>> Running {name}...")
    try:
        res = subprocess.run(cmd, shell=True, cwd=cwd)
        if res.returncode != 0:
            print(f"!!! {name} FAILED")
            return False
        print(f"--- {name} PASSED")
        return True
    except Exception as e:
        print(f"!!! {name} ERRORED: {e}")
        return False

def main():
    steps = [
        ("Watcher Lint", ["cargo", "clippy", "--", "-D", "warnings"], "watcher"),
        ("Watcher Test", ["cargo", "test"], "watcher"),
        ("Engine Lint", ["uv", "run", "ruff", "check", "."], "engine"),
        ("Engine Types", ["uv", "run", "pyright", "src"], "engine"),
        ("Engine Test", ["uv", "run", "pytest", "../tests"], "engine"),
        ("UI Lint/Types", ["npx", "tsc"], "ui"),
        ("UI Test", ["npm", "run", "test"], "ui"),
        ("Android Analyze", ["flutter", "analyze"], "android_app"),
        ("Android Test", ["flutter", "test"], "android_app"),
    ]
    
    all_passed = True
    for name, cmd, cwd in steps:
        if not run_step(name, cmd, cwd):
            all_passed = False
            
    if all_passed:
        print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED. CHECK LOGS ABOVE.")
        sys.exit(1)

if __name__ == "__main__":
    main()
