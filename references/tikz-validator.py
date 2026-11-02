#!/usr/bin/env python3
"""
TikZ pre-compile validator — 5 automated layout checks before pdflatex.
Usage: python tikz-validator.py <file.tex>

Checks: container overflow, label collision, edge clipping, boundary
clearance, oversize nodes. Shared parser: tikz_parser.py.

Exit: 0=PASS, 1=WARN, 2=ERROR
"""

import json
import re
import sys
from dataclasses import dataclass
from tikz_parser import (
    Node, Zone, parse_nodes, parse_zones
)


@dataclass
class Issue:
    level: str  # ERROR, WARN
    category: str
    line_no: int
    message: str


# ─── Check 1: Container overflow ───

def check_container_overflow(nodes: list[Node], zones: list[Zone], diag: float = 30.0) -> list[Issue]:
    issues = []
    PAD = diag * 0.01  # 1% of diagonal
    for node in nodes:
        if not node.name:
            continue
        containing = None
        for zone in zones:
            if zone.x_min <= node.x <= zone.x_max and zone.y_min <= node.y <= zone.y_max:
                if containing is None or (zone.x_max - zone.x_min) < (containing.x_max - containing.x_min):
                    containing = zone
        if containing is None:
            continue
        hw, hh = node.width / 2, node.height / 2
        if node.x - hw < containing.x_min + PAD:
            issues.append(Issue(level="WARN", category="overflow", line_no=0,
                message=f"Overflow: '{node.name}' left {node.x-hw:.1f} beyond zone left {containing.x_min:.1f}"))
        if node.x + hw > containing.x_max - PAD:
            issues.append(Issue(level="WARN", category="overflow", line_no=0,
                message=f"Overflow: '{node.name}' right {node.x+hw:.1f} beyond zone right {containing.x_max:.1f}"))
        if node.y - hh < containing.y_min + PAD:
            issues.append(Issue(level="WARN", category="overflow", line_no=0,
                message=f"Overflow: '{node.name}' bottom {node.y-hh:.1f} beyond zone bottom {containing.y_min:.1f}"))
        if node.y + hh > containing.y_max - PAD:
            issues.append(Issue(level="WARN", category="overflow", line_no=0,
                message=f"Overflow: '{node.name}' top {node.y+hh:.1f} beyond zone top {containing.y_max:.1f}"))
    return issues


# ─── Check 2: Label collision ───

def check_label_collision(nodes: list[Node], diag: float = 30.0) -> list[Issue]:
    issues = []
    MIN_GAP = diag * 0.005  # 0.5% of diagonal
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1, n2 = nodes[i], nodes[j]
            if not n1.name or not n2.name:
                continue
            if abs(n1.x - n2.x) < 0.01 and abs(n1.y - n2.y) < 0.01:
                continue
            hw1, hh1 = n1.width / 2, n1.height / 2
            hw2, hh2 = n2.width / 2, n2.height / 2
            x_overlap = (n1.x - hw1 - MIN_GAP < n2.x + hw2 and n1.x + hw1 + MIN_GAP > n2.x - hw2)
            y_overlap = (n1.y - hh1 - MIN_GAP < n2.y + hh2 and n1.y + hh1 + MIN_GAP > n2.y - hh2)
            if x_overlap and y_overlap:
                dist_x = abs(n1.x - n2.x) - hw1 - hw2
                dist_y = abs(n1.y - n2.y) - hh1 - hh2
                issues.append(Issue(level="WARN", category="collision", line_no=0,
                    message=f"Collision: '{n1.name}' & '{n2.name}' gap x={dist_x:.2f} y={dist_y:.2f}cm"))
    return issues


# ─── Check 3: Edge clipping ───

def check_edge_clipping(nodes: list[Node], zones: list[Zone], diag: float = 30.0) -> list[Issue]:
    issues = []
    M = diag * 0.02  # 2% of diagonal
    if zones:
        all_x = [z.x_min for z in zones] + [z.x_max for z in zones]
        all_y = [z.y_min for z in zones] + [z.y_max for z in zones]
        cx0, cx1 = min(all_x) - 1.0, max(all_x) + 1.0
        cy0, cy1 = min(all_y) - 1.0, max(all_y) + 1.0
    elif nodes:
        all_x = [n.x - n.width/2 for n in nodes] + [n.x + n.width/2 for n in nodes]
        all_y = [n.y - n.height/2 for n in nodes] + [n.y + n.height/2 for n in nodes]
        cx0, cx1 = min(all_x) - 1.0, max(all_x) + 1.0
        cy0, cy1 = min(all_y) - 1.0, max(all_y) + 1.0
    else:
        return issues

    for node in nodes:
        if not node.name:
            continue
        hw, hh = node.width / 2, node.height / 2
        l, r, b, t = node.x - hw, node.x + hw, node.y - hh, node.y + hh
        sides = [
            ("left", l - cx0, M), ("right", cx1 - r, M),
            ("bottom", b - cy0, M), ("top", cy1 - t, M),
        ]
        for side, gap, need in sides:
            if gap < need:
                issues.append(Issue(level="WARN", category="edge-clip", line_no=0,
                    message=f"Edge clip: '{node.name}' {side} gap {gap:.1f}cm < {need}cm"))
    return issues


# ─── Check 4: Boundary clearance ───

def check_boundary_clearance(nodes: list[Node], diag: float = 30.0) -> list[Issue]:
    issues = []
    C = diag * 0.01  # 1% of diagonal
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1, n2 = nodes[i], nodes[j]
            if not n1.name or not n2.name:
                continue
            gx = abs(n1.x - n2.x) - n1.width/2 - n2.width/2
            gy = abs(n1.y - n2.y) - n1.height/2 - n2.height/2
            if gx < C and gy < C and gx > -1 and gy > -1:
                if 0 < gx < C or 0 < gy < C:
                    issues.append(Issue(level="WARN", category="tight-clearance", line_no=0,
                        message=f"Tight: '{n1.name}' & '{n2.name}' gap x={gx:.2f} y={gy:.2f}cm"))
    return issues


# ─── Check 5: Oversize nodes (box >> text content) ───

def check_oversize_nodes(nodes: list[Node]) -> list[Issue]:
    """Flag nodes where explicitly-set widths/heights are >1.8x estimated text size."""
    issues = []
    for node in nodes:
        if not node.name or len(node.name) < 2:
            continue
        # Skip anonymous text labels (long descriptive text)
        if len(node.name) > 30:
            continue
        # Skip default-dimension nodes (parser used 2.8/0.9 as fallback)
        if abs(node.width - 2.8) < 0.01 and abs(node.height - 0.9) < 0.01:
            continue

        text_chars = len(node.name)
        est_width = text_chars * 0.12 + 0.8   # chars * font + inner_sep
        est_height = 0.65                      # single line + padding

        if node.width > 1.5 and node.width > est_width * 3.0:  # 3x text width
            issues.append(Issue(level="WARN", category="oversize", line_no=0,
                message=f"Box too wide: '{node.name}' {node.width:.1f}cm for '{node.name}'"
                f" (est text ~{est_width:.1f}cm, ratio {node.width/est_width:.1f}x)"
                f" — drop minimum width or reduce to ~{est_width:.1f}cm"))
        if node.height > 1.0 and node.height > est_height * 3.0:  # 3x text height
            issues.append(Issue(level="WARN", category="oversize", line_no=0,
                message=f"Box too tall: '{node.name}' {node.height:.1f}cm"
                f" (est text ~{est_height:.1f}cm, ratio {node.height/est_height:.1f}x)"
                f" — drop minimum height"))
    return issues


# ─── Main ───

def compute_diag(nodes):
    """Calculate figure diagonal from node positions."""
    if not nodes: return 30.0  # default ~30cm diagonal
    xs = [n.x for n in nodes]
    ys = [n.y for n in nodes]
    w = max(xs) - min(xs) + 3 if xs else 20
    h = max(ys) - min(ys) + 3 if ys else 15
    return (w**2 + h**2) ** 0.5  # cm

def validate(filepath: str) -> list[Issue]:
    """Interference checks only — thresholds relative to figure diagonal."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.split("\n")

    all_issues = []
    nodes = parse_nodes(lines)
    zones = parse_zones(lines)
    diag = compute_diag(nodes)  # cm
    # 1. Boxes touching/overlapping (relaxed: diag*0.5%)
    if len(nodes) >= 2:
        all_issues.extend(check_label_collision(nodes, diag))
    # 2. Node outside its zone background (padding: diag*1%)
    if zones:
        all_issues.extend(check_container_overflow(nodes, zones, diag))
    # 3. Node too close to canvas edge (margin: diag*2%)
    all_issues.extend(check_edge_clipping(nodes, zones, diag))
    # 4. Nodes too close (gap: diag*1%)
    all_issues.extend(check_boundary_clearance(nodes, diag))
    # 5. Box size >> text size (3x, already relative)
    all_issues.extend(check_oversize_nodes(nodes))
    return all_issues


def print_json(issues: list[Issue]) -> None:
    """Machine-readable block consumed by references/quality_inspect.py."""
    print("--- JSON ---")
    print(json.dumps([
        {"level": i.level, "check": "tikz-validator", "category": i.category,
         "line": i.line_no, "message": i.message}
        for i in issues
    ], indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print("Usage: python tikz-validator.py <file.tex>")
        sys.exit(1)

    filepath = sys.argv[1]
    issues = validate(filepath)

    if not issues:
        print("PASS — no issues found")
        print_json(issues)
        sys.exit(0)

    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]

    print(f"{'='*60}")
    print(f"TikZ Validator Report: {filepath}")
    print(f"{'='*60}")

    all_warns = errors + warns
    if all_warns:
        print(f"\nWARN ({len(all_warns)}) — model decides:")
        for i, issue in enumerate(all_warns, 1):
            loc = f"L{issue.line_no}" if issue.line_no else ""
            print(f"  {i}. [{issue.category}] {loc} {issue.message}")

    print(f"\nTotal: {len(all_warns)} warnings")
    print_json(all_warns)

    sys.exit(1 if all_warns else 0)


if __name__ == "__main__":
    main()
