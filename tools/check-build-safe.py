#!/usr/bin/env python3
"""
Check that _build.py is safe to run: in a temporary copy of the repo, run
_build.py in its default mode and fail if any existing file changes.

Usage:  python3 tools/check-build-safe.py

Never touches the real working tree. Compares a SHA-256 of every file
(except .git and __pycache__) before and after the build run, and also
checks that git status of tracked files in the copy is the same
before and after. New files are reported but allowed, since
default mode only writes pages that do not exist yet.
"""
import hashlib, pathlib, shutil, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
SKIP = {".git", "__pycache__", "node_modules"}


def snapshot(root):
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and not (SKIP & set(p.relative_to(root).parts)):
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main():
    with tempfile.TemporaryDirectory(prefix="ameridex-buildcheck-") as tmp:
        copy = pathlib.Path(tmp) / "repo"
        shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
        def git_status():
            return subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                                  cwd=copy, capture_output=True, text=True).stdout
        before = snapshot(copy)
        status_before = git_status()
        run = subprocess.run([sys.executable, "-B", "_build.py"], cwd=copy,
                             capture_output=True, text=True)
        print(run.stdout, end="")
        if run.returncode != 0:
            print(run.stderr, end="")
            print(f"FAIL: _build.py exited with {run.returncode}")
            return 1
        after = snapshot(copy)
        changed = sorted(f for f in before if f in after and before[f] != after[f])
        removed = sorted(f for f in before if f not in after)
        added = sorted(f for f in after if f not in before)
        status = "" if git_status() == status_before else git_status().strip()
        for f in added:
            print(f"note: new file written: {f}")
        if changed or removed or status:
            for f in changed:
                print(f"FAIL: changed {f}")
            for f in removed:
                print(f"FAIL: removed {f}")
            if status:
                print("FAIL: git status of tracked files changed in the temp copy:\n" + status)
            return 1
        print(f"OK: default _build.py run left all {len(before)} existing files unchanged")
        return 0


if __name__ == "__main__":
    sys.exit(main())
