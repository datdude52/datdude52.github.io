"""Export the ARC-001 scan data for the interactive scan on the site.

    python scripts/export_scan.py [path/to/Sonar Scanner/CODE/analysis/matlab]

Reads the MATLAB-export CSVs (pooled per-angle medians, scene objects and vertices) and
writes content/projects/arc-001-ultrasonic-vs-tof/scan.json. The JSON is committed, so the
site build and CI never need the raw data. Rerun this only when the analysis changes.
"""
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT.parent / "Sonar Scanner" / "CODE" / "analysis" / "matlab"
OUT = ROOT / "content" / "projects" / "arc-001-ultrasonic-vs-tof" / "scan.json"


def rows(data: Path, name: str) -> list:
    with open(data / f"{name}.csv", newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except ValueError:
        return None


def main(data: Path) -> None:
    # One sweep direction (dir 0) is enough to show both sensors at every angle.
    by_angle = {}
    for r in rows(data, "main_pooled"):
        if r["dir"] != "0":
            continue
        a = by_angle.setdefault(round(float(r["world_deg"]), 2), {"deg": round(float(r["world_deg"]), 1)})
        med = num(r["median_mm"])
        a["tof" if r["sensor"] == "1" else "us"] = round(med) if med is not None and num(r["detect_frac"]) else None
    # Two ground truths from the ray-cast model: the object on the beam's centre line ("ray"), and the
    # nearest surface anywhere inside the ultrasonic sensor's +/-18 degree beam ("cone").
    for r in rows(data, "r_true"):
        if r["dir"] != "0":
            continue
        a = by_angle.get(round(float(r["world_deg"]), 2))
        if a is not None:
            ray, cone = num(r["r_true_mm"]), num(r["beam_min_18deg_mm"])
            a["ray"] = round(ray) if ray is not None else None
            a["cone"] = round(cone) if cone is not None else None
    angles = [by_angle[k] for k in sorted(by_angle)]

    polys = {}
    for r in rows(data, "scene_vertices"):
        polys.setdefault(r["object_num"], []).append([round(float(r["x_mm"])), round(float(r["y_mm"]))])
    circles = []
    for o in rows(data, "scene_objects"):
        rad = num(o["radius_mm"])
        if o["kind"] == "circ" and rad is not None:
            rc = float(o["r_min_mm"]) + rad
            th = math.radians((float(o["theta_min_deg"]) + float(o["theta_max_deg"])) / 2)
            circles.append([round(rc * math.cos(th)), round(rc * math.sin(th)), round(rad)])

    OUT.write_text(json.dumps({"angles": angles, "polys": list(polys.values()), "circles": circles},
                              separators=(",", ":")), encoding="utf-8")
    print(f"[export_scan] {len(angles)} angles, {len(polys)} polygons, {len(circles)} circles -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT)
