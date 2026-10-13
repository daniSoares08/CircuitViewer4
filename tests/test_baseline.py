#!/usr/bin/env python3
# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.
"""Freezes the complete generated catalog byte-for-byte.

Why: a format or catalog change can silently shift an offset and corrupt
content that was already correct - and the symptom may only appear on the
calculator, pages deep into an exercise. `pack_v2.py`'s simulator catches a
parser that walks the wrong number of bytes; this catches the complementary
risk of an unintended writer or content change.

Hash `src/exercises.c` and every `CV4DAT*.bin` payload and compare them with
the recorded manifest. Re-bless only after an intentional catalog change.

    python tests/test_baseline.py            # verify
    python tests/test_baseline.py --bless    # re-record (intentional change)
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "baseline_manifest.json"


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def snapshot():
    """Regenerate, then hash every generated artifact."""
    subprocess.run([sys.executable, str(ROOT / "tools" / "generate_cv4.py")],
                   cwd=str(ROOT), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = {"exercises_c": _sha(ROOT / "src" / "exercises.c")}
    for binf in sorted((ROOT / "bin").glob("CV4DAT*.bin")):
        out[binf.name] = _sha(binf)
        out[binf.name + ".size"] = binf.stat().st_size
    return out


def main():
    bless = "--bless" in sys.argv
    current = snapshot()

    if bless or not MANIFEST.exists():
        MANIFEST.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n",
                            encoding="ascii")
        print("baseline registrado (%d artefatos) -> %s"
              % (len(current), MANIFEST.name))
        for k, v in sorted(current.items()):
            print("   %-22s %s" % (k, v))
        return 0

    expected = json.loads(MANIFEST.read_text(encoding="ascii"))
    diffs = []
    for key in sorted(set(expected) | set(current)):
        a, b = expected.get(key), current.get(key)
        if a != b:
            diffs.append((key, a, b))

    if not diffs:
        print("BASELINE OK: %d artefatos inalterados" % len(current))
        return 0

    print("BASELINE MUDOU em %d artefato(s):" % len(diffs))
    for key, a, b in diffs:
        print("   %-22s esperado=%s  atual=%s" % (key, a, b))
    print("\nSe a mudanca for intencional, re-registre com:")
    print("   python tests/test_baseline.py --bless")
    return 1


if __name__ == "__main__":
    sys.exit(main())
