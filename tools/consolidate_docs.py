"""
Consolidate markdown files into README.md and QUICKSTART.md.
Moves originals to staging/docs_backup/ preserving path so this can be undone.

Usage:
    python tools\consolidate_docs.py --root "C:\path\to\repo"

If no --root provided, uses current working directory.

Heuristics:
 - Filenames containing quick, quickstart, getting, start, guide, usage, quick-reference -> QUICKSTART.md
 - All others -> README.md

This script is conservative: it moves originals into staging/docs_backup rather than permanently deleting.
"""
from __future__ import annotations
import argparse
import os
import shutil
from pathlib import Path

QUICK_KEYWORDS = ("quick", "quickstart", "getting", "start", "guide", "usage", "quick-reference", "getting_started")


def is_quick(fname: str) -> bool:
    n = fname.lower()
    return any(k in n for k in QUICK_KEYWORDS)


def consolidate(root: Path):
    root = root.resolve()
    readme = root / "README.md"
    quick = root / "QUICKSTART.md"
    license_file = root / "LICENSE"
    staging_backup = root / "staging" / "docs_backup"
    staging_backup.mkdir(parents=True, exist_ok=True)

    # Ensure target files exist
    if not readme.exists():
        readme.write_text("# Project README\n\n")
    if not quick.exists():
        quick.write_text("# Quickstart\n\n")

    # Walk and find markdown files
    moved = []
    for dirpath, dirnames, filenames in os.walk(root):
        pdir = Path(dirpath)
        # skip staging folder
        if staging_backup in pdir.parents or pdir == staging_backup:
            continue
        for fn in filenames:
            if not fn.lower().endswith(".md"):
                continue
            fp = pdir / fn
            # skip the two canonical files in repo root and license
            if fp.resolve() == readme.resolve() or fp.resolve() == quick.resolve():
                continue
            if fp.resolve() == license_file.resolve():
                continue
            # also skip files under .git, venv, build dirs
            if any(part in (".git", "venv", "env", "build", "dist") for part in fp.parts):
                continue

            # Decide target
            rel = fp.relative_to(root)
            target = quick if is_quick(str(rel)) else readme
            header = f"\n\n---\n\n**Source:** `{rel}`\n\n"
            try:
                content = fp.read_text(encoding="utf-8")
            except Exception:
                try:
                    content = fp.read_text(encoding="latin-1")
                except Exception:
                    content = ""  # skip unreadable

            # Append to target
            with target.open("a", encoding="utf-8") as f:
                f.write(header)
                f.write(content)

            # Move original to backup
            dest = staging_backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(fp), str(dest))
            moved.append((str(rel), str(dest)))
            print(f"Consolidated {rel} -> {target.name}")

    print("\nConsolidation complete.")
    print(f"Moved {len(moved)} files to {staging_backup}")
    if moved:
        print("If everything looks good, you can delete the originals under staging/docs_backup or keep them as archive.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root (default=current dir)")
    args = parser.parse_args()
    consolidate(Path(args.root))
