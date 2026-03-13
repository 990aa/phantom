import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FILES_TO_UPDATE = [
    ("ui/package.json", r'"version":\s*"([^"]+)"', r'"version": "{new_version}"'),
    ("ui/package-lock.json", r'"version":\s*"([^"]+)"', r'"version": "{new_version}"', 2),
    ("ui/src-tauri/tauri.conf.json", r'"version":\s*"([^"]+)"', r'"version": "{new_version}"'),
    ("ui/src-tauri/Cargo.toml", r'version\s*=\s*"([^"]+)"', r'version = "{new_version}"', 1),
    ("watcher/Cargo.toml", r'version\s*=\s*"([^"]+)"', r'version = "{new_version}"', 1),
    ("engine/pyproject.toml", r'version\s*=\s*"([^"]+)"', r'version = "{new_version}"', 1),
]

def get_current_version():
    with open("ui/package.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["version"]

def bump_version(current_version, bump_type):
    major, minor, patch = map(int, current_version.split("."))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Invalid bump type")

def update_file(path, pattern, replacement_template, new_version, max_replacements=0):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}")
        return
    
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()

    replacement = replacement_template.format(new_version=new_version)
    
    new_content, count = re.subn(pattern, replacement, content, count=max_replacements)
    
    with open(p, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Updated {path} ({count} replacements)")

def main():
    parser = argparse.ArgumentParser(description="Bump app version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--major", action="store_true", help="Bump major version")
    group.add_argument("--minor", action="store_true", help="Bump minor version")
    group.add_argument("--patch", action="store_true", help="Bump patch version")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes or commit")
    
    args = parser.parse_args()
    
    bump_type = "major" if args.major else "minor" if args.minor else "patch"
    
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)
    
    print(f"Bumping version from {current_version} to {new_version} (type: {bump_type})")
    
    if args.dry_run:
        print("Dry run enabled. The following files would be updated:")
        for file_info in FILES_TO_UPDATE:
            print(f" - {file_info[0]}")
        return

    for file_info in FILES_TO_UPDATE:
        path = file_info[0]
        pattern = file_info[1]
        template = file_info[2]
        max_replacements = file_info[3] if len(file_info) > 3 else 0
        update_file(path, pattern, template, new_version, max_replacements)
        
    # Auto commit
    print("Running repomix...")
    try:
        subprocess.run(["repomix"], check=True, shell=True)
    except Exception as e:
        print(f"Failed to run repomix: {e}")

    print("Committing version changes...")
    files_to_add = [f[0] for f in FILES_TO_UPDATE]
    subprocess.run(["git", "add"] + files_to_add, check=True)
    subprocess.run(["git", "commit", "-m", f"chore: bump version to {new_version}"], check=True)
    print("Done!")

if __name__ == "__main__":
    main()
