import subprocess
import json
import sys
import argparse
from pathlib import Path

def get_current_version():
    with open("ui/package.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["version"]

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error executing {' '.join(cmd)}:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Release and push current version")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying git history or pushing")
    args = parser.parse_args()

    # 1. Check for uncommitted changes and auto-commit
    status = run_cmd(["git", "status", "--porcelain"])
    if status:
        print("Uncommitted changes detected. Auto-committing before release...")
        if args.dry_run:
            print("[Dry Run] Would run: git add .")
            print("[Dry Run] Would run: git commit -m 'chore: auto-commit before release'")
        else:
            run_cmd(["git", "add", "."])
            run_cmd(["git", "commit", "-m", "chore: auto-commit before release"])
    
    # 2. Get current version
    version = get_current_version()
    tag_name = f"v{version}"
    print(f"Preparing to release {tag_name}...")
    
    # 3. Check if tag exists
    tags = run_cmd(["git", "tag"])
    if tag_name in tags.split('\n'):
        print(f"Tag {tag_name} already exists. Skipping tag creation.")
    else:
        print(f"Creating tag {tag_name}...")
        if args.dry_run:
            print(f"[Dry Run] Would run: git tag -a {tag_name} -m 'Release {tag_name}'")
        else:
            run_cmd(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"])
        
    # 4. Push commits and tags
    print(f"Pushing to origin main with tags to trigger workflows...")
    if args.dry_run:
        print("[Dry Run] Would run: git push origin main --tags")
    else:
        try:
            # We don't use run_cmd check=True here because there may be no origin or no network
            res = subprocess.run(["git", "push", "origin", "main", "--tags"], capture_output=True, text=True)
            if res.returncode != 0:
                print("Failed to push. Do you have an origin remote configured?")
                print(res.stderr)
            else:
                print(res.stdout)
                print(f"Successfully pushed {tag_name} and triggered release workflows.")
        except Exception as e:
            print(f"Failed to push: {e}")

if __name__ == "__main__":
    main()
