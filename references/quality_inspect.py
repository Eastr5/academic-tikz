#!/usr/bin/env python3
"""
Unified Quality Inspector — one script, 15 checks, all WARN, model decides.
Usage: python quality_inspect.py output.tex [output.pdf]

A sensor that cannot run reports FAIL instead of an empty result, so a broken
checker is never mistaken for a clean figure.

Exit: 0=no findings, 1=warnings, 2=sensor failure
"""

import sys, os, subprocess, re, json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def sensor_failure(script, detail):
    return [{"level": "FAIL", "check": script, "message": detail}]


def run_sensor(script, *args):
    """Run a sensor script, capture its JSON output."""
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"  # sensors emit UTF-8 even on a GBK console
        r = subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, script)] + list(args),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=60)
        out = r.stdout + r.stderr
        # Parse JSON from stdout only: stderr may carry warnings after the block.
        m = re.search(r'--- JSON ---\s*\n(.*)', r.stdout, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError as e:
                return sensor_failure(script, f"malformed JSON (exit {r.returncode}): {e}")
        # Fallback: parse warning counts
        warns = re.findall(r'(\d+) warnings?', out)
        if warns: return [{"level":"WARN","check":script,"message":f"{warns[-1]} findings"}]
        # Nothing parseable and a non-zero exit: the sensor crashed or refused to run.
        if r.returncode != 0:
            tail = " ".join(out.strip().splitlines()[-2:])[:300] or "no output"
            return sensor_failure(script, f"exit {r.returncode}: {tail}")
        return []
    except Exception as e:
        return sensor_failure(script, str(e))

def main():
    if len(sys.argv) < 2:
        print("Usage: python quality_inspect.py output.tex [output.pdf]")
        sys.exit(1)

    tex = sys.argv[1]
    pdf = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"{'='*60}")
    print(f"Quality Inspection: {tex}")
    print(f"{'='*60}")

    r1 = run_sensor("tikz-validator.py", tex)
    r2 = run_sensor("pdf-overlap-checker.py", pdf) if pdf else []
    r3 = run_sensor("quality-report.py", tex, pdf) if pdf else run_sensor("quality-report.py", tex)
    all_warns = r1 + r2 + r3
    fails = [w for w in all_warns if w.get("level") == "FAIL"]

    print(f"\n{'='*60}")
    print(f"Inspection: {len(all_warns)} warnings")
    if fails:
        print(f"FAILED SENSORS: {len(fails)}")
    print(f"{'='*60}")
    for i, w in enumerate(all_warns, 1):
        print(f"  {i}. [{w.get('check','?')}] {w.get('message','')}")

    if fails:
        print("\nSensor failure — findings are INCOMPLETE. Do not treat as PASS.")
    else:
        print("\nAll WARN. Model decides.")
    print(f"--- JSON ---")
    print(json.dumps(all_warns, indent=2))

    if fails:
        sys.exit(2)
    sys.exit(1 if all_warns else 0)

if __name__ == "__main__":
    main()
