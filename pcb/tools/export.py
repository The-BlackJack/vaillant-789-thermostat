# -*- coding: utf-8 -*-
"""Fertigungsdaten fuer JLCPCB: Gerber+Bohrdaten (ZIP), BOM, CPL, Renders, Schaltplan-PDF."""
import os, csv, subprocess, zipfile, glob, shutil, tempfile
import design as D

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)
OUT = os.path.join(PRJ, "fertigung")
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
PCB = os.path.join(PRJ, D.PROJECT + ".kicad_pcb")
SCH = os.path.join(PRJ, D.PROJECT + ".kicad_sch")


def run(*a):
    r = subprocess.run([CLI] + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stdout, r.stderr)
        raise SystemExit("kicad-cli fehlgeschlagen: " + " ".join(a))
    return r.stdout


def main():
    os.makedirs(OUT, exist_ok=True)
    gdir = tempfile.mkdtemp(prefix="vaillant_gerber_")

    run("pcb", "export", "gerbers", "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
        "--subtract-soldermask", "-o", gdir + os.sep, PCB)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-units", "mm", "--generate-map",
        "--map-format", "gerberx2", "-o", gdir + os.sep, PCB)
    zp = os.path.join(OUT, D.PROJECT + "-gerber.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(gdir, "*"))):
            z.write(f, os.path.basename(f))
    print("Gerber:", len(glob.glob(os.path.join(gdir, "*"))), "Dateien ->", zp)

    # BOM (nur JLCPCB-bestueckte Teile), gleiche LCSC-Nummer zusammenfassen
    groups = {}
    for p in D.PARTS:
        if not p.get("smd"):
            continue
        key = (p["value"], p["fp"].split(":")[1], p["lcsc"])
        groups.setdefault(key, []).append(p["ref"])
    with open(os.path.join(OUT, "BOM-JLCPCB.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "JLCPCB Part #"])
        for (val, fp, lcsc), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            w.writerow([val, ",".join(sorted(refs)), fp, lcsc])

    # CPL aus KiCad-Positionsdatei (gleicher Ursprung wie Gerber)
    pos = os.path.join(gdir, "pos.csv")
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "front", "-o", pos, PCB)
    smd = {p["ref"] for p in D.PARTS if p.get("smd")}
    rows = list(csv.DictReader(open(pos, encoding="utf-8")))
    with open(os.path.join(OUT, "CPL-JLCPCB.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for r in rows:
            if r["Ref"] in smd:
                w.writerow([r["Ref"], r["PosX"] + "mm", r["PosY"] + "mm", "Top", "%g" % (float(r["Rot"]) % 360)])
    missing = smd - {r["Ref"] for r in rows}
    if missing:
        raise SystemExit("CPL: fehlende Teile " + str(missing))

    # Selbst einzuloetende Teile
    with open(os.path.join(OUT, "Teile-selbst-loeten-v2.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Bauteil", "Wert", "Teil"])
        for p in D.PARTS:
            if not p.get("smd") and not p.get("nobom"):
                w.writerow([p["ref"], p["value"], p.get("mpn", "")])

    run("sch", "export", "pdf", "-o", os.path.join(OUT, "schaltplan.pdf"), SCH)
    run("pcb", "render", "--side", "top", "--width", "1600", "--height", "1150", "--quality", "high",
        "-o", os.path.join(OUT, "render-oben.png"), PCB)
    run("pcb", "render", "--side", "top", "--width", "1600", "--height", "1150", "--quality", "high",
        "--rotate", "-35,0,20", "--zoom", "0.9", "-o", os.path.join(OUT, "render-schraeg.png"), PCB)
    run("pcb", "render", "--side", "bottom", "--width", "1600", "--height", "1150", "--quality", "high",
        "-o", os.path.join(OUT, "render-unten.png"), PCB)
    shutil.rmtree(gdir, ignore_errors=True)
    print("fertig ->", OUT)


if __name__ == "__main__":
    main()
