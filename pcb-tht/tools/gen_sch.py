# -*- coding: utf-8 -*-
"""Erzeugt Schaltplan, eigene Bibliotheken und Projektdatei."""
import os, uuid, json
from sexpr import parse, dump, q, unq, find, findall, SymLib, pins_of
import design as D

HERE = os.path.dirname(os.path.abspath(__file__))
PRJ = os.path.dirname(HERE)
KSYM = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"


def U():
    return str(uuid.uuid4())


ROOT_UUID = "6f1a3c52-7d0e-4b8a-9c1e-0a5b8e7f7890"

# ---------------------------------------------------------------- eigene Lib
ESP_LEFT = ["5V", "GND", "3V3", "IO4", "IO3", "IO2", "IO1", "IO0"]
ESP_RIGHT = ["IO5", "IO6", "IO7", "IO8", "IO9", "IO10", "IO20", "IO21"]


def esp_symbol(name="ESP32-C3_SuperMini"):
    f = '(effects (font (size 1.27 1.27)))'
    fh = '(effects (font (size 1.27 1.27)) (hide yes))'
    pins = []
    for i, n in enumerate(ESP_LEFT):
        t = {"5V": "power_in", "GND": "power_in", "3V3": "power_out"}.get(n, "bidirectional")
        pins.append('(pin %s line (at -12.7 %.2f 0) (length 2.54) (name "%s" %s) (number "%d" %s))'
                    % (t, 8.89 - i * 2.54, n, f, i + 1, f))
    for i, n in enumerate(ESP_RIGHT):
        pins.append('(pin bidirectional line (at 12.7 %.2f 180) (length 2.54) (name "%s" %s) (number "%d" %s))'
                    % (8.89 - i * 2.54, n, f, i + 9, f))
    return parse('''(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
  (property "Reference" "A" (at 0 13.97 0) %s)
  (property "Value" "ESP32-C3_SuperMini" (at 0 -13.97 0) %s)
  (property "Footprint" "vaillant:ESP32-C3_SuperMini_Socket" (at 0 0 0) %s)
  (property "Datasheet" "" (at 0 0 0) %s)
  (property "Description" "ESP32-C3 SuperMini, 2x8 Pins, gesteckt" (at 0 0 0) %s)
  (symbol "%s_0_1" (rectangle (start -10.16 11.43) (end 10.16 -11.43) (stroke (width 0.254) (type default)) (fill (type background))))
  (symbol "%s_1_1" %s))''' % (name, f, f, fh, fh, fh, name, name, " ".join(pins)))[0]


def write_symlib():
    s = esp_symbol()
    txt = '(kicad_symbol_lib (version 20241209) (generator "vaillant_gen") (generator_version "1.0")\n\t%s\n)\n' % dump(s, 1)
    open(os.path.join(PRJ, "vaillant.kicad_sym"), "w", encoding="utf-8").write(txt)


def write_esp_footprint():
    os.makedirs(os.path.join(PRJ, "vaillant.pretty"), exist_ok=True)
    L = []
    eff = lambda h: '(effects (font (size %s %s) (thickness %.2f)))' % (h, h, 0.15 if float(h) >= 0.8 else 0.12)
    L.append('(footprint "ESP32-C3_SuperMini_Socket" (version 20240108) (generator "vaillant_gen") (layer "F.Cu")')
    L.append(' (descr "ESP32-C3 SuperMini (22,5 x 18 mm) gesteckt in 2x Buchsenleiste 1x8 RM 2,54, Reihenabstand 15,24 mm. USB unten, Antenne oben.")')
    L.append(' (property "Reference" "A1" (at -10.4 0 90) (layer "F.SilkS") (uuid "%s") %s)' % (U(), eff("1")))
    L.append(' (property "Value" "ESP32-C3_SuperMini" (at 0 12.3 0) (layer "F.Fab") (uuid "%s") %s)' % (U(), eff("1")))
    L.append(' (property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") %s)' % (U(), eff("1")))
    L.append(' (attr through_hole)')
    for lay, (x0, y0, x1, y1), w in [("F.SilkS", (-9.1, -11.35, 9.1, 11.35), 0.12), ("F.CrtYd", (-9.4, -11.6, 9.4, 11.6), 0.05),
                                     ("F.Fab", (-9.0, -11.25, 9.0, 11.25), 0.1)]:
        L.append(' (fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width %.2f) (type solid)) (fill none) (layer "%s") (uuid "%s"))'
                 % (x0, y0, x1, y1, w, lay, U()))
    # Antennenbereich markieren
    L.append(' (fp_text user "ANTENNE" (at 0 -10.2 0) (layer "F.SilkS") (uuid "%s") %s)' % (U(), eff("0.8")))
    L.append(' (fp_text user "USB" (at 0 10.3 0) (layer "F.SilkS") (uuid "%s") %s)' % (U(), eff("0.8")))
    for i, n in enumerate(ESP_LEFT):
        y = 8.89 - i * 2.54
        L.append(' (fp_text user "%s" (at -6.0 %.2f 0) (layer "F.SilkS") (uuid "%s") (effects (font (size 0.7 0.7) (thickness 0.12)) (justify left)))'
                 % (n.replace("IO", ""), y, U()))
        L.append(' (pad "%d" thru_hole %s (at -7.62 %.2f) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "%s"))'
                 % (i + 1, "rect" if i == 0 else "circle", y, U()))
    for i, n in enumerate(ESP_RIGHT):
        y = 8.89 - i * 2.54
        L.append(' (fp_text user "%s" (at 6.0 %.2f 0) (layer "F.SilkS") (uuid "%s") (effects (font (size 0.7 0.7) (thickness 0.12)) (justify right)))'
                 % (n.replace("IO", ""), y, U()))
        L.append(' (pad "%d" thru_hole circle (at 7.62 %.2f) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask") (uuid "%s"))'
                 % (i + 9, y, U()))
    L.append(')')
    open(os.path.join(PRJ, "vaillant.pretty", "ESP32-C3_SuperMini_Socket.kicad_mod"), "w", encoding="utf-8").write("\n".join(L) + "\n")


# ---------------------------------------------------------------- Schaltplan
def libsym(lib_id):
    lib, name = lib_id.split(":")
    if lib == "vaillant":
        s = esp_symbol(name)
    else:
        s = SymLib(os.path.join(KSYM, lib + ".kicad_sym")).flat(name)
    s[1] = q(lib_id)
    return s


def prop(name, val, x, y, hide=False, size=1.27, just=None):
    e = '(effects (font (size %s %s))%s%s)' % (size, size, " (justify %s)" % just if just else "", " (hide yes)" if hide else "")
    return '(property %s %s (at %.2f %.2f 0) %s)' % (q(name), q(val), x, y, e)


def build_sch():
    items = []
    lib_ids = {}
    labels = []
    ncs = []
    texts = []

    def place(lib_id, ref, value, fp, x, y, unit, pins_map, extra_props=(), in_bom=True, on_board=True, sym_uuid=None):
        s = lib_ids.setdefault(lib_id, libsym(lib_id))
        allpins = pins_of(s)
        upins = [p for p in allpins if p["unit"] in (0, unit)]
        su = sym_uuid or U()
        L = ['(symbol (lib_id %s) (at %.2f %.2f 0) (unit %d) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (uuid "%s")'
             % (q(lib_id), x, y, unit, "yes" if in_bom else "no", "yes" if on_board else "no", su)]
        top = max([p["y"] for p in upins] + [2.54])
        bot = min([p["y"] for p in upins] + [-2.54])
        L.append(prop("Reference", ref, x + 2.54, y - top - 2.54, hide=ref.startswith("#")))
        L.append(prop("Value", value, x + 2.54, y - bot + 2.54, hide=ref.startswith("#")))
        L.append(prop("Footprint", fp or "", x, y, hide=True))
        L.append(prop("Datasheet", "", x, y, hide=True))
        for k, v in extra_props:
            L.append(prop(k, v, x, y, hide=True))
        for p in upins:
            L.append('(pin %s (uuid "%s"))' % (q(p["number"]), U()))
        L.append('(instances (project %s (path "/%s" (reference %s) (unit %d))))' % (q(D.PROJECT), ROOT_UUID, q(ref), unit))
        L.append(')')
        items.append(" ".join(L))
        for p in upins:
            px, py = x + p["x"], y - p["y"]
            if p["number"] not in pins_map:
                continue
            net = pins_map[p["number"]]
            if net is None:
                ncs.append('(no_connect (at %.2f %.2f) (uuid "%s"))' % (px, py, U()))
                continue
            a = (p["angle"] + 180) % 360
            just = "left bottom" if a in (0, 90) else "right bottom"
            labels.append('(label %s (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))'
                          % (q(net), px, py, a, just, U()))
        return su

    uuids = {}
    for p in D.PARTS:
        props = []
        if p.get("lcsc"):
            props.append(("LCSC", p["lcsc"]))
        if p.get("mpn"):
            props.append(("MPN", p["mpn"]))
        su = U()
        uuids[p["ref"]] = su
        if p.get("units"):
            for unit, (x, y) in p["units"].items():
                place(p["sym"], p["ref"], p["value"], p["fp"], x, y, unit, p["pins"], props,
                      sym_uuid=su if unit == 1 else None)
        else:
            x, y = p["sch"]
            place(p["sym"], p["ref"], p["value"], p["fp"], x, y, 1, p["pins"], props,
                  in_bom=not p.get("nobom"), sym_uuid=su)
    for i, n in enumerate(D.PWR_FLAGS):
        place("power:PWR_FLAG", "#FLG0%d" % (i + 1), "PWR_FLAG", "", 30.48 + i * 25.4, 213.36, 1, {"1": n},
              in_bom=False, on_board=False)

    def text(s, x, y, size=2.0):
        texts.append('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %s %s) (bold yes)) (justify left bottom)) (uuid "%s"))'
                     % (q(s), x, y, size, size, U()))
    text("VERSORGUNG aus Klemme 8 (ca. 23,6 V), Masse = Klemme 9", 20.32, 22.86)
    text("STEUERUNG KLEMME 7  (fail-safe: ESP aus -> Opto aus -> +9V am Tiefpass -> Klemme 7 frei)", 20.32, 83.82)
    text("Verstaerkung 1 + R5/R4 = 2,2  ->  U(OPOUT) = 19,8 V x Pegel, Klemme 7 = OPOUT + 0,6 V", 20.32, 88.9, 1.5)
    text("PERIPHERIE (3,3 V vom ESP32-C3 SuperMini)", 20.32, 144.78)
    text("PWR_FLAGs", 20.32, 200.66, 1.5)
    texts.append('(text %s (exclude_from_sim no) (at 20.32 238.76 0) (effects (font (size 1.5 1.5)) (justify left bottom)) (uuid "%s"))'
                 % (q("Netze werden ueber gleichnamige Labels verbunden. LCSC-Nummern stehen im Feld LCSC (fuer JLCPCB)."), U()))

    libs = "\n\t\t".join(dump(s, 2) for s in lib_ids.values())
    body = "\n\t".join(items + labels + ncs + texts)
    sch = '''(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "%s")
	(paper "A3")
	(title_block
		(title "Vaillant 7-8-9 Wandthermostat")
		(date "2026-11-19")
		(rev "1.0")
		(comment 1 "Therme atmoTEC VCW 194/3-C-HL, ersetzt calorMATIC 332")
		(comment 2 "ESP32-C3 SuperMini + ESPHome")
	)
	(lib_symbols
		%s
	)
	%s
	(sheet_instances (path "/" (page "1")))
	(embedded_fonts no)
)
''' % (ROOT_UUID, libs, body)
    open(os.path.join(PRJ, D.PROJECT + ".kicad_sch"), "w", encoding="utf-8").write(sch)
    json.dump(uuids, open(os.path.join(HERE, "sym_uuids.json"), "w"), indent=1)


def write_tables():
    open(os.path.join(PRJ, "sym-lib-table"), "w").write(
        '(sym_lib_table\n\t(version 7)\n\t(lib (name "vaillant") (type "KiCad") (uri "${KIPRJMOD}/vaillant.kicad_sym") (options "") (descr "Projektbibliothek"))\n)\n')
    open(os.path.join(PRJ, "fp-lib-table"), "w").write(
        '(fp_lib_table\n\t(version 7)\n\t(lib (name "vaillant") (type "KiCad") (uri "${KIPRJMOD}/vaillant.pretty") (options "") (descr "Projektbibliothek"))\n)\n')


def write_pro():
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "silk_line_width": 0.12,
                             "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {"min_clearance": 0.15, "min_track_width": 0.15, "min_via_annular_width": 0.13,
                          "min_via_diameter": 0.5, "min_through_hole_diameter": 0.3, "min_hole_clearance": 0.25,
                          "min_hole_to_hole": 0.25, "min_copper_edge_clearance": 0.3, "min_silk_clearance": 0.0,
                          "min_text_height": 0.6, "min_text_thickness": 0.1, "solder_mask_to_copper_clearance": 0.0},
                "rule_severities": {"silk_overlap": "warning", "silk_over_copper": "warning",
                                    "silk_edge_clearance": "warning", "text_height": "warning",
                                    "text_thickness": "warning", "lib_footprint_issues": "warning",
                                    "lib_footprint_mismatch": "warning"},
                "track_widths": [0.0, 0.25, 0.4, 0.5],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}],
            }
        },
        "erc": {"rule_severities": {}},
        "meta": {"filename": D.PROJECT + ".kicad_pro", "version": 3},
        "net_settings": {
            "classes": [{"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6,
                         "via_drill": 0.3, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                         "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
                         "wire_width": 6, "bus_width": 12, "line_style": 0,
                         "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
                         "priority": 2147483647}],
            "meta": {"version": 4},
        },
        "sheets": [[ROOT_UUID, "Root"]],
    }
    json.dump(pro, open(os.path.join(PRJ, D.PROJECT + ".kicad_pro"), "w"), indent=2)


if __name__ == "__main__":
    write_symlib()
    write_esp_footprint()
    write_tables()
    build_sch()
    write_pro()
    print("ok")
