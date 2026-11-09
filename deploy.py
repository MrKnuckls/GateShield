#!/usr/bin/env python3
"""
Deploy GateShield from THIS GIT REPO to https://knuckls.com/gateshield/

Repo is the source of truth; refuses to run with uncommitted changes.
FTP credentials come from ~/.knuckls-ftp (mode 600) — not from this file.

Run:  python3 /home/shaun/gateshield/deploy.py
"""
import ftplib
import hashlib
import io
import pathlib
import subprocess
import time
import urllib.request

REPO = pathlib.Path(__file__).resolve().parent
REMOTE_DIR = "/public_html/gateshield"
FILES = ["index.html", "guide.html", "manifest.json", "icon-192.png", "icon-512.png"]
URL_BASE = "https://knuckls.com/gateshield/"
CREDS = pathlib.Path.home() / ".knuckls-ftp"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    dirty = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain", "--", *FILES],
        capture_output=True, text=True,
    ).stdout.strip()
    if dirty:
        print("Refusing to deploy — uncommitted changes:\n" + dirty)
        print("Commit them first, so the live site always matches a known revision.")
        return 1

    try:
        host, user, pw = [l.strip() for l in CREDS.read_text().splitlines()[:3]]
    except Exception as e:
        print(f"Cannot read {CREDS}: {e}")
        return 1

    local = {}
    for n in FILES:
        p = REPO / n
        if not p.exists():
            print(f"Missing {p}")
            return 1
        local[n] = p.read_bytes()

    rev = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    print(f"Deploying {rev} -> {REMOTE_DIR}")

    f = ftplib.FTP(host, timeout=90)
    f.login(user, pw)
    try:
        f.mkd(REMOTE_DIR)
    except Exception:
        pass  # already exists
    f.cwd(REMOTE_DIR)
    for n, data in local.items():
        f.storbinary("STOR " + n, io.BytesIO(data))
        print(f"  uploaded {n} ({len(data)} bytes)")
    f.quit()
    time.sleep(2)

    ok = True
    f = ftplib.FTP(host, timeout=90)
    f.login(user, pw)
    f.cwd(REMOTE_DIR)
    for n in FILES:
        buf = io.BytesIO()
        f.retrbinary("RETR " + n, buf.write)
        same = sha(buf.getvalue()) == sha(local[n])
        ok &= same
        print(f"  ftp  {n}: {'MATCH' if same else 'MISMATCH'}  {sha(local[n])[:16]}…")
    f.quit()

    for n in FILES:
        u = URL_BASE + n
        try:
            b = urllib.request.urlopen(
                urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40
            ).read()
            same = sha(b) == sha(local[n])
            ok &= same
            print(f"  https {n}: {'MATCH' if same else 'MISMATCH'}")
        except Exception as e:
            ok = False
            print(f"  https {n}: FETCH FAILED ({e})")

    print("DONE — all verified" if ok else "FAILED — mismatch, do not trust the live copy")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
