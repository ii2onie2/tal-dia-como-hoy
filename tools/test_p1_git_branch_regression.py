#!/usr/bin/env python3
"""Offline Git regression test. No remote GitHub writes or TikTok calls."""
import os
from pathlib import Path
import subprocess
import tempfile

def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=check)

workflow = Path(".github/workflows/render.yml").read_text(encoding="utf-8")
assert "github.ref == 'refs/heads/main'" in workflow
assert 'git pull --rebase origin "$GITHUB_REF_NAME"' in workflow
assert 'git push origin "HEAD:$GITHUB_REF_NAME"' in workflow
assert "git pull --rebase origin main" not in workflow

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    remote = root / "remote.git"
    git(root, "init", "--bare", str(remote))
    main = root / "main"
    main.mkdir()
    git(main, "init", "-b", "main")
    git(main, "config", "user.name", "Test")
    git(main, "config", "user.email", "test@example.invalid")
    (main / "render.py").write_text("main version\n")
    git(main, "add", ".")
    git(main, "commit", "-m", "main render")
    git(main, "remote", "add", "origin", str(remote))
    git(main, "push", "-u", "origin", "main")
    git(remote, "symbolic-ref", "HEAD", "refs/heads/main")
    feature = root / "feature"
    git(root, "clone", str(remote), str(feature))
    git(feature, "config", "user.name", "Test")
    git(feature, "config", "user.email", "test@example.invalid")
    git(feature, "checkout", "-b", "integration")
    (feature / "render.py").write_text("integration version\n")
    git(feature, "add", ".")
    git(feature, "commit", "-m", "feature render")
    git(feature, "push", "-u", "origin", "integration")
    (main / "render.py").write_text("main diverged version\n")
    git(main, "add", ".")
    git(main, "commit", "-m", "main diverges")
    git(main, "push", "origin", "main")
    git(feature, "fetch", "origin", "main")
    git(feature, "checkout", "-b", "test-archive")
    (feature / "video.mp4").write_bytes(b"synthetic MP4 placeholder - not for publication")
    git(feature, "add", ".")
    git(feature, "commit", "-m", "archive test artifact")
    # Rebase on main is an incorrect target and yields a content conflict.
    bad = git(feature, "rebase", "origin/main", check=False)
    assert bad.returncode != 0, "Expected rebase against unrelated main content to fail"
    git(feature, "rebase", "--abort")
    good = git(feature, "pull", "--rebase", "origin", "integration")
    assert good.returncode == 0
    git(feature, "push", "origin", "HEAD:test-archive")
    assert git(feature, "rev-parse", "HEAD").stdout.strip() == git(root, "--git-dir", str(remote), "rev-parse", "refs/heads/test-archive").stdout.strip()
print("P1_GIT_REGRESSION=PASS")
print("SYNTHETIC_LOCAL_ONLY=YES")
print("PRODUCTION_WRITE=NO")
print("TIKTOK_REQUEST=NO")
