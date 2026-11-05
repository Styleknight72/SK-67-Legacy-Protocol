#!/usr/bin/env python3
"""Digital DNA: a provable-origin manifest for a folder of work. Standard library only.

  python3 digital_dna.py stamp  --author "Steve Claude Patient"   # fingerprint every file, chain to the last manifest
  python3 digital_dna.py verify                                   # check every file against the manifest
  python3 digital_dna.py verify --previous OLD/DIGITAL_DNA.json   # also check the chain back to an older manifest

What it proves: these exact files existed with these exact contents when the manifest was made, and each
manifest is linked to the one before it, so history cannot be quietly rewritten. For an independent date,
timestamp the manifest with OpenTimestamps:  ots stamp DIGITAL_DNA.json
What it does not prove: who wrote the files, or that anything in them is true.
"""
import argparse, datetime, hashlib, json, os, sys

MANIFEST = "DIGITAL_DNA.json"
SKIP_DIRS = {".git", "__pycache__"}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def list_files(root):
    out = {}
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if rel in (MANIFEST, MANIFEST + ".ots"):
                continue
            out[rel] = sha256_file(os.path.join(root, rel))
    return out

def body_hash(m):
    body = {k: v for k, v in m.items() if k != "manifest_sha256"}
    data = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def stamp(root, author):
    path = os.path.join(root, MANIFEST)
    prev = load(path) if os.path.exists(path) else None
    m = {
        "format": "digital-dna/1",
        "author": author,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sequence": (prev["sequence"] + 1) if prev else 1,
        "parent_manifest_sha256": prev["manifest_sha256"] if prev else None,
        "files": list_files(root),
    }
    m["manifest_sha256"] = body_hash(m)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print(f"Stamped manifest #{m['sequence']}: {len(m['files'])} files")
    print(f"Manifest fingerprint: {m['manifest_sha256']}")
    print("Next: for an independent date, run  ots stamp " + MANIFEST)
    return 0

def verify(root, previous):
    problems = []
    m = load(os.path.join(root, MANIFEST))
    if body_hash(m) != m.get("manifest_sha256"):
        problems.append("The manifest itself was changed (its own fingerprint does not match).")
    now = list_files(root)
    for rel, h in sorted(m["files"].items()):
        if rel not in now:
            problems.append(f"MISSING  {rel}")
        elif now[rel] != h:
            problems.append(f"CHANGED  {rel}")
    added = sorted(set(now) - set(m["files"]))
    if previous:
        old = load(previous)
        if body_hash(old) != old.get("manifest_sha256"):
            problems.append("The previous manifest was changed (its own fingerprint does not match).")
        elif m.get("parent_manifest_sha256") != old["manifest_sha256"]:
            problems.append("CHAIN BROKEN: this manifest does not link to the previous one.")
    for a in added:
        print(f"note: new file since the stamp: {a}")
    if problems:
        print("FAILED")
        for p in problems:
            print("  " + p)
        return 1
    print(f"OK: {len(m['files'])} files match manifest #{m['sequence']} (made {m['created_utc']}, author {m['author']}).")
    if previous:
        print("OK: chain to the previous manifest is intact.")
    return 0

def main():
    ap = argparse.ArgumentParser(description="Digital DNA: provable-origin manifest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stamp"); s.add_argument("--author", required=True); s.add_argument("--root", default=".")
    v = sub.add_parser("verify"); v.add_argument("--previous"); v.add_argument("--root", default=".")
    a = ap.parse_args()
    sys.exit(stamp(a.root, a.author) if a.cmd == "stamp" else verify(a.root, a.previous))

if __name__ == "__main__":
    main()
