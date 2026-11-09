#!/usr/bin/env python3
"""
Deploy GateShield from THIS GIT REPO to https://knuckls.com/gateshield/

knuckls.com is served from the VM100 box (10.15.34.140, CF tunnel origin
http://10.15.34.140:80) with docroot /var/www/knuckls.com — the Hostinger
FTP space is a mirror, NOT the origin.

Repo is the source of truth; refuses to run with uncommitted changes.
Cloudflare injects its RUM beacon into served HTML; verification strips it
before hashing so we compare OUR bytes, not CF's.

Run:  python3 /home/shaun/gateshield/deploy.py
"""
import hashlib
import pathlib
import re
import subprocess
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent
REMOTE_HOST = "shaun@10.15.34.140"
REMOTE_DIR = "/var/www/knuckls.com/gateshield"
FILES = ["index.html", "guide.html", "manifest.json", "icon-192.png", "icon-512.png"]
URL_BASE = "https://knuckls.com/gateshield/"


def cf_strip(b: bytes) -> bytes:
    """Strip Cloudflare's injected RUM analytics beacon from HTML before hashing."""
    if b[:5] != b"<!DOC" and b"<html" not in b[:2000].lower():
        return b
    return re.sub(rb"<script[^>]+cloudflareinsights[^>]*></script>\s*", b"", b)


def sha(b: bytes) -> str:
    return hashlib.sha256(cf_strip(b)).hexdigest()


def ssh(cmd: str, timeout=120) -> str:
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", REMOTE_HOST, cmd],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"ssh failed: {r.stderr.strip()}")
    return r.stdout.strip()


def main() -> int:
    dirty = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain", "--", *FILES],
        capture_output=True, text=True,
    ).stdout.strip()
    if dirty:
        print("Refusing to deploy — uncommitted changes:\n" + dirty)
        print("Commit them first, so the live site always matches a known revision.")
        return 1

    rev = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    print(f"Deploying {rev} -> {REMOTE_HOST}:{REMOTE_DIR}")

    for n in FILES:
        if not (REPO / n).exists():
            print(f"Missing {n}")
            return 1

    ssh("sudo mkdir -p " + REMOTE_DIR
        + " && sudo chown shaun:shaun " + REMOTE_DIR)
    subprocess.run(["scp", "-o", "BatchMode=yes", "-q",
                    *[str(REPO / n) for n in FILES],
                    f"{REMOTE_HOST}:{REMOTE_DIR}/"], check=True, timeout=120)
    ssh("sudo chown www-data:www-data " + REMOTE_DIR + "/*"
        + " && sudo chmod 644 " + REMOTE_DIR + "/*")
    for n in FILES:
        print(f"  uploaded {n}")
    time.sleep(2)

    ok = True
    for n in FILES:
        u = URL_BASE + n
        local = sha((REPO / n).read_bytes())
        try:
            b = urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=40).read()
            same = sha(b) == local
            ok &= same
            print(f"  https {n}: {'MATCH' if same else 'MISMATCH'}  {local[:16]}…")
        except Exception as e:
            ok = False
            print(f"  https {n}: FETCH FAILED ({e})")

    print("DONE — all verified" if ok else "FAILED — mismatch, do not trust the live copy")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
