# -*- coding: utf-8 -*-
"""Lochraster-Aufbau 70 x 50 mm (27 x 19 Loecher, RM 2,54).

Bauteilseite = oben. Spalte c (0..26) von links, Zeile r (0..18) von oben.
Drahtbruecken auf der Loetseite werden automatisch verlegt (nur waagerecht/senkrecht,
jedes Loch gehoert hoechstens einem Netz) und gegen die Netzliste geprueft.
Erzeugt: layout-bauteilseite.png, layout-loetseite.png, verdrahtung.md
"""
import os, heapq, math, itertools
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
COLS, ROWS = 27, 19
P = 2.54
X0, Y0 = 70 - (COLS - 1) * P, 50 - (ROWS - 1) * P
X0 /= 2; Y0 /= 2


def xy(c, r):
    return X0 + c * P, Y0 + r * P


# ---------------------------------------------------------------- Bauteile
# leads: {pin: (c, r, net)}; body: ("rect", x0,y0,x1,y1) mm oder ("circle", cx, cy, d)
PARTS = {}


def part(ref, value, leads, body, label=None, order=""):
    PARTS[ref] = dict(value=value, leads=leads, body=body, label=label or ref, order=order)


def rect_around(holes, mx=1.3, my=1.3):
    xs = [xy(c, r)[0] for c, r in holes]; ys = [xy(c, r)[1] for c, r in holes]
    return ("rect", min(xs) - mx, min(ys) - my, max(xs) + mx, max(ys) + my)


def axial(ref, value, a, b, na, nb, w=1.3, label=None, order=""):
    (c0, r0), (c1, r1) = a, b
    if r0 == r1:
        body = ("rect", xy(min(c0, c1), r0)[0] + 1.6, xy(c0, r0)[1] - w, xy(max(c0, c1), r0)[0] - 1.6, xy(c0, r0)[1] + w)
    else:
        body = ("rect", xy(c0, r0)[0] - w, xy(c0, min(r0, r1))[1] + 1.6, xy(c0, r0)[0] + w, xy(c0, max(r0, r1))[1] - 1.6)
    part(ref, value, {"1": (c0, r0, na), "2": (c1, r1, nb)}, body, label, order)


def radial_elko(ref, value, plus, minus, np_, nm, d, order=""):
    (c0, r0), (c1, r1) = plus, minus
    cx = (xy(c0, r0)[0] + xy(c1, r1)[0]) / 2; cy = (xy(c0, r0)[1] + xy(c1, r1)[1]) / 2
    part(ref, value, {"+": (c0, r0, np_), "-": (c1, r1, nm)}, ("circle", cx, cy, d), order=order)


ESP_L = ["+5V", "GND", "+3V3", "EPD_CLK", "PWM", None, "EPD_BUSY", "ENC_SW"]          # 5V,GND,3V3,IO4,IO3,IO2,IO1,IO0
ESP_R = ["EPD_DC", "EPD_DIN", "EPD_CS", "SDA", "SCL", "EPD_RST", "ENC_B", "ENC_A"]     # IO5..IO10, IO20, IO21
ESP_LN = ["5V", "GND", "3V3", "IO4", "IO3", "IO2", "IO1", "IO0"]
ESP_RN = ["IO5", "IO6", "IO7", "IO8", "IO9", "IO10", "IO20", "IO21"]
ER0 = 2           # oberste ESP-Reihe (IO0 / IO21)
leads = {}
for i in range(8):
    leads["L" + ESP_LN[i]] = (2, ER0 + 7 - i, ESP_L[i])
    leads["R" + ESP_RN[i]] = (8, ER0 + 7 - i, ESP_R[i])
part("A1", "ESP32-C3 SuperMini (in 2x Buchsenleiste 1x8)", leads,
     ("rect", xy(2, 0)[0] - 1.4, xy(0, ER0)[1] - 2.6, xy(8, 0)[0] + 1.4, xy(0, ER0 + 7)[1] + 2.6), "ESP32-C3")

# Kabel (Display, Sensor, Drehgeber) direkt neben die ESP-Pins loeten
CAB = {}
def cab(name, c, r, net):
    CAB[name] = (c, r, net)
for i, n in enumerate(ESP_RN):
    net = ESP_R[i]
    lab = {"EPD_DC": "Disp DC", "EPD_DIN": "Disp DIN", "EPD_CS": "Disp CS", "SDA": "Sens SDA", "SCL": "Sens SCL",
           "EPD_RST": "Disp RST", "ENC_B": "Enc B", "ENC_A": "Enc A"}[net]
    cab(lab, 9, ER0 + 7 - i, net)
cab("Enc SW", 1, ER0 + 0, "ENC_SW")
cab("Disp BUSY", 1, ER0 + 1, "EPD_BUSY")
cab("Disp CLK", 1, ER0 + 3, "EPD_CLK")
cab("Disp VCC", 1, ER0 + 5, "+3V3")
cab("Disp PWR", 0, ER0 + 5, "+3V3")
cab("Sens VIN", 0, ER0 + 4, "+3V3")
cab("Disp GND", 1, ER0 + 6, "GND")
cab("Sens GND", 0, ER0 + 6, "GND")
cab("Enc C", 0, ER0 + 7, "GND")
cab("Enc SW-GND", 0, ER0 + 8, "GND")
part("K", "Kabelanschluesse", CAB, None, "Kabel")

# Versorgung (rechts)
part("U4", "TRACO TSR 0.5-2450", {"Vin": (22, 1, "VDC"), "GND": (22, 2, "GND"), "Vout": (22, 3, "+5V")},
     ("rect", xy(22, 0)[0] - 2.9, xy(22, 1)[1] - 4.0, xy(22, 0)[0] + 6.2, xy(22, 1)[1] + 9.1), "U4 TSR")
radial_elko("C8", "1000uF/10V (10x16)", (22, 7), (24, 7), "+5V", "GND", 10.0)
radial_elko("C7", "220uF/35V (8x15, RM3,5 auf 2,54 biegen)", (17, 2), (18, 2), "VDC", "GND", 8.0)
axial("R7", "100R 0,6W", (20, 2), (20, 6), "VDC", "+V")
radial_elko("C1", "100uF/35V", (19, 9), (20, 9), "+V", "GND", 6.3)
part("J1", "Schraubklemme 3-pol. RM 5,08", {"7": (24, 11, "K7"), "8": (24, 13, "K8"), "9": (24, 15, "GND")},
     ("rect", xy(24, 0)[0] - 5.2, xy(0, 11)[1] - 2.6, xy(24, 0)[0] + 4.6, xy(0, 15)[1] + 2.6), "J1 Therme")
axial("D1", "1N5819", (21, 17), (21, 13), "K8", "+V", label="D1", order="Ring (Kathode) oben")
part("U2", "78L09 (TO-92)", {"OUT": (13, 17, "+9V"), "GND": (14, 17, "GND"), "IN": (15, 17, "+V")},
     ("rect", xy(13, 0)[0] - 1.4, xy(0, 17)[1] - 1.0, xy(15, 0)[0] + 1.4, xy(0, 17)[1] + 2.4), "U2 78L09",
     order="flache Seite zur Platinenkante, Beine OUT-GND-IN von links")
part("C3", "4,7uF/50V X7R 1210 (SMD auf 2 Loetpunkte)", {"1": (17, 17, "+V"), "2": (17, 16, "GND")},
     ("rect", xy(17, 0)[0] - 1.3, xy(0, 16)[1], xy(17, 0)[0] + 1.3, xy(0, 17)[1]), "C3")
axial("C4", "100nF", (11, 17), (11, 15), "+9V", "GND", w=1.2)
# Steuerung (unten links / Mitte)
part("U1", "PC817 (DIP-4)", {"1": (3, 13, "OPTO_A"), "2": (3, 14, "GND"), "3": (6, 14, "GND"), "4": (6, 13, "OPTO_C")},
     ("rect", xy(3, 0)[0] + 0.6, xy(0, 13)[1] - 1.0, xy(6, 0)[0] - 0.6, xy(0, 14)[1] + 1.0), "U1 PC817",
     order="Punkt/Pin 1 oben links")
axial("R1", "330R", (3, 12), (7, 12), "OPTO_A", "PWM", w=1.2)
axial("R2", "10k", (6, 16), (10, 16), "OPTO_C", "+9V")
axial("R3", "100k", (7, 14), (11, 14), "OPTO_C", "FILT")
part("C5", "4,7uF/50V X7R 1210 (SMD auf 2 Loetpunkte)", {"1": (12, 15, "FILT"), "2": (12, 16, "GND")},
     ("rect", xy(12, 0)[0] - 1.3, xy(0, 15)[1], xy(12, 0)[0] + 1.3, xy(0, 16)[1]), "C5")
part("U3", "LM358 (DIP-8, Fassung)",
     {"1": (13, 11, "OPOUT"), "2": (13, 12, "FB"), "3": (13, 13, "FILT"), "4": (13, 14, "GND"),
      "5": (16, 14, "GND"), "6": (16, 13, "UB"), "7": (16, 12, "UB"), "8": (16, 11, "+V")},
     ("rect", xy(13, 0)[0] + 0.6, xy(0, 11)[1] - 1.1, xy(16, 0)[0] - 0.6, xy(0, 14)[1] + 1.1), "U3 LM358",
     order="Kerbe/Pin 1 oben links")
axial("C6", "100nF", (17, 11), (17, 13), "+V", "GND", w=1.2)
axial("R5", "120k 1%", (10, 9), (14, 9), "FB", "OPOUT")
axial("R4", "100k 1% (stehend)", (11, 10), (11, 12), "FB", "GND", w=1.3)
axial("D2", "1N4148", (14, 10), (18, 10), "OPOUT", "K7R", w=1.0, label="D2", order="Ring (Kathode) links")
axial("R6", "220R", (19, 11), (19, 15), "K7R", "K7")

# gesperrte Loecher: Montageloecher (aufbohren 2,2 mm) + direkte Nachbarn, Antennenbereich
MOUNT = [(0, 0), (26, 0), (0, 18), (26, 18)]
BLOCK = set()
for (c, r) in MOUNT:
    for dc, dr in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        BLOCK.add((c + dc, r + dr))
for c in range(3, 8):
    for r in range(0, ER0 + 1):
        BLOCK.add((c, r))        # unter der ESP-Antenne keine Draehte


# ---------------------------------------------------------------- Pruefung Platzierung
def check_placement():
    errs = []
    used = {}
    for ref, p in PARTS.items():
        for pin, (c, r, n) in p["leads"].items():
            if not (0 <= c < COLS and 0 <= r < ROWS):
                errs.append("%s.%s ausserhalb" % (ref, pin))
            if (c, r) in used:
                errs.append("Loch %s doppelt: %s.%s / %s" % ((c, r), ref, pin, used[(c, r)]))
            used[(c, r)] = "%s.%s" % (ref, pin)
            if (c, r) in BLOCK:
                errs.append("%s.%s in Sperrbereich" % (ref, pin))

    def inside(body, x, y, m=0.6):
        if body is None:
            return False
        if body[0] == "rect":
            return body[1] - m < x < body[3] + m and body[2] - m < y < body[4] + m
        return math.hypot(x - body[1], y - body[2]) < body[3] / 2 + m

    for ref, p in PARTS.items():
        for ref2, p2 in PARTS.items():
            if ref2 == ref:
                continue
            for pin, (c, r, n) in p2["leads"].items():
                if inside(p["body"], *xy(c, r)):
                    errs.append("Bein %s.%s unter Gehaeuse von %s" % (ref2, pin, ref))
    # Gehaeuse-Ueberlappung (grob)
    def bb(b):
        if b[0] == "rect":
            return b[1:]
        return (b[1] - b[3] / 2, b[2] - b[3] / 2, b[1] + b[3] / 2, b[2] + b[3] / 2)
    refs = [r for r in PARTS if PARTS[r]["body"]]
    for a, b2 in itertools.combinations(refs, 2):
        A, B = bb(PARTS[a]["body"]), bb(PARTS[b2]["body"])
        if A[0] < B[2] - 0.2 and B[0] < A[2] - 0.2 and A[1] < B[3] - 0.2 and B[1] < A[3] - 0.2:
            if {a, b2} != {"A1", "J2"}:
                errs.append("Gehaeuse %s und %s ueberlappen" % (a, b2))
    for (x, y) in [(0, 0), (70, 50)]:
        pass
    for ref, p in PARTS.items():
        b = p["body"]
        if b:
            x0, y0, x1, y1 = bb(b)
            if x0 < -0.3 or y0 < -2.0 or x1 > 70.3 or y1 > 50.3:
                errs.append("%s ragt ueber den Rand" % ref)
    return errs


# ---------------------------------------------------------------- Router (Loetseite)
def route(order=None):
    owner = {}
    for (c, r) in BLOCK:
        owner[(c, r)] = "#"
    pins_by_net = {}
    for ref, p in PARTS.items():
        for pin, (c, r, n) in p["leads"].items():
            owner[(c, r)] = n or "#NC"
            if n:
                pins_by_net.setdefault(n, []).append((c, r, "%s.%s" % (ref, pin)))
    wires = {}      # net -> list of segments ((c,r),(c,r)) blanker Draht
    jumpers = []    # (net, a, b) isolierte Drahtbruecke
    # Reihenfolge: kurze Netze zuerst, GND zuletzt
    def span(n):
        pts = pins_by_net[n]
        return (max(p[0] for p in pts) - min(p[0] for p in pts)) + (max(p[1] for p in pts) - min(p[1] for p in pts))
    if order is None:
        order = sorted([n for n in pins_by_net if n != "GND"], key=span) + ["GND"]
    for net in order:
        pts = pins_by_net[net]
        tree = {(pts[0][0], pts[0][1])}
        rest = [(p[0], p[1]) for p in pts[1:]]
        while rest:
            rest.sort(key=lambda q: min(abs(q[0] - t[0]) + abs(q[1] - t[1]) for t in tree))
            s = rest.pop(0)
            path = astar(s, tree, net, owner)
            if path is None:
                t = min(tree, key=lambda t: math.hypot(s[0] - t[0], s[1] - t[1]))
                jumpers.append((net, s, t))
                tree.add(s)
                continue
            for a, b in zip(path, path[1:]):
                wires.setdefault(net, []).append((a, b))
            for h in path:
                owner[h] = net
                tree.add(h)
    return wires, jumpers, pins_by_net, owner


def astar(start, targets, net, owner):
    def h(p):
        return min(abs(p[0] - t[0]) + abs(p[1] - t[1]) for t in targets)
    openq = [(h(start), 0, start, None)]
    came = {start: None}
    g = {start: 0}
    while openq:
        f, gc, cur, d = heapq.heappop(openq)
        if cur in targets and cur != start:
            path = [cur]
            while came[path[-1]] is not None:
                path.append(came[path[-1]][0])
            return path[::-1]
        for k, (dc, dr) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
            nb = (cur[0] + dc, cur[1] + dr)
            if not (0 <= nb[0] < COLS and 0 <= nb[1] < ROWS):
                continue
            o = owner.get(nb)
            if o is not None and o != net:
                continue
            ng = gc + 1 + (0.4 if d is not None and d != k else 0)
            if ng < g.get(nb, 1e9):
                g[nb] = ng; came[nb] = (cur, k)
                heapq.heappush(openq, (ng + h(nb), ng, nb, k))
    return None


def verify(wires, jumpers, pins_by_net):
    parent = {}
    def f(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def u(a, b):
        parent[f(a)] = f(b)
    holenet = {}
    for net, segs in wires.items():
        for a, b in segs:
            u(a, b)
            for hh in (a, b):
                if holenet.setdefault(hh, net) != net:
                    return ["Kurzschluss an Loch %s: %s / %s" % (hh, holenet[hh], net)]
    for net, a, b in jumpers:
        u(a, b)
    errs = []
    for net, pts in pins_by_net.items():
        roots = {f((c, r)) for c, r, _ in pts}
        if len(roots) > 1:
            errs.append("Netz %s nicht verbunden" % net)
    # verschiedene Netze im selben Baum?
    rootnet = {}
    for net, pts in pins_by_net.items():
        for c, r, _ in pts:
            rt = f((c, r))
            if rootnet.setdefault(rt, net) != net:
                errs.append("Netze %s und %s kurzgeschlossen" % (rootnet[rt], net))
    return errs


# ---------------------------------------------------------------- Zeichnen
NETCOL = {"GND": (40, 40, 40), "+V": (220, 30, 30), "K8": (230, 120, 0), "VDC": (200, 60, 160),
          "+5V": (200, 0, 0), "+9V": (240, 80, 80), "+3V3": (255, 140, 0)}


def netcolor(n):
    if n in NETCOL:
        return NETCOL[n]
    hsh = sum(ord(ch) * (i + 7) for i, ch in enumerate(n))
    pal = [(30, 110, 220), (0, 150, 140), (120, 80, 200), (20, 150, 40), (160, 110, 0), (0, 120, 180),
           (170, 40, 120), (90, 130, 30), (60, 60, 200), (0, 140, 90)]
    return pal[hsh % len(pal)]


def render(wires, jumpers, mirror, fname, title):
    S = 22
    M = 200
    W, H = int(70 * S + 2 * M), int(50 * S + 2 * M + 40)
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 15); fsm = ImageFont.truetype("arial.ttf", 12)
        fbig = ImageFont.truetype("arialbd.ttf", 20)
    except Exception:
        font = fsm = fbig = ImageFont.load_default()

    def T(x, y):
        if mirror:
            x = 70 - x
        return M + x * S, M + 40 + y * S
    d.text((M, 10), title, fill=(0, 0, 0), font=fbig)
    d.rectangle([T(0, 0), T(70, 50)] if not mirror else [T(70, 0), T(0, 50)], fill=(222, 196, 140), outline=(120, 90, 40), width=2)
    # Spalten/Zeilen-Beschriftung
    for c in range(COLS):
        x, y = T(*xy(c, 0)); d.text((x - 6, M + 40 - 22), str(c), fill=(90, 90, 90), font=fsm)
    for r in range(ROWS):
        x, y = T(*xy(0 if not mirror else 26, r)); d.text((M - 28, y - 7), str(r), fill=(90, 90, 90), font=fsm)
    for c in range(COLS):
        for r in range(ROWS):
            x, y = T(*xy(c, r))
            col = (180, 150, 90)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(200, 170, 110), outline=col)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(90, 70, 40))
    for (c, r) in MOUNT:
        x, y = T(*xy(c, r)); d.ellipse([x - 24, y - 24, x + 24, y + 24], outline=(0, 0, 0), width=2)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(255, 255, 255), outline=(0, 0, 0))
    # Antennenbereich
    a0 = T(xy(2, 0)[0] - 2, 0); a1 = T(xy(8, 0)[0] + 2, xy(0, 2)[1] + 0.6)
    d.rectangle([min(a0[0], a1[0]), a0[1], max(a0[0], a1[0]), a1[1]], outline=(0, 150, 0), width=2)
    # Bauteile
    for ref, p in PARTS.items():
        b = p["body"]
        if b is None:
            continue
        if b[0] == "rect":
            p0 = T(b[1], b[2]); p1 = T(b[3], b[4])
            box = [min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])]
            d.rectangle(box, outline=(0, 0, 0) if not mirror else (150, 150, 150), width=2 if not mirror else 1,
                        fill=None if mirror else ((235, 235, 245) if ref != "A1" else None))
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        else:
            cx, cy = T(b[1], b[2]); rr = b[3] / 2 * S
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(0, 0, 0) if not mirror else (150, 150, 150),
                      width=2 if not mirror else 1, fill=None if mirror else (225, 235, 250))
        if not mirror:
            d.text((cx, cy), p["label"], fill=(0, 0, 0), font=font, anchor="mm")
    # Draehte
    for net, segs in wires.items():
        col = netcolor(net)
        for a, b2 in segs:
            d.line([T(*xy(*a)), T(*xy(*b2))], fill=col if mirror else tuple(min(255, v + 150) for v in col),
                   width=7 if mirror else 3)
    for net, a, b2 in jumpers:
        col = netcolor(net)
        pa, pb = T(*xy(*a)), T(*xy(*b2))
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2 - 25
        pts = [(pa[0] + (mx - pa[0]) * t * 2 if t < .5 else mx + (pb[0] - mx) * (t - .5) * 2,
                pa[1] + (my - pa[1]) * t * 2 if t < .5 else my + (pb[1] - my) * (t - .5) * 2) for t in [i / 20 for i in range(21)]]
        d.line(pts, fill=col, width=4)
    # Beinchen / Pads
    leftlab = {}
    for ref, p in PARTS.items():
        for pin, (c, r, n) in p["leads"].items():
            x, y = T(*xy(c, r))
            col = netcolor(n) if n else (150, 150, 150)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=col, outline=(0, 0, 0))
            if ref == "K":
                if not mirror:
                    if c <= 1:
                        leftlab.setdefault(r, []).append((c, pin))
                    else:
                        d.text((x + 12, y), pin, fill=(150, 0, 0), font=fsm, anchor="lm")
                continue
            if ref in ("J2", "J3", "J4") or (ref == "A1") or (ref in ("U1", "U3") and pin == "1") or ref == "U4" or ref == "J1":
                txt = pin[1:] if ref == "A1" else pin
                if not mirror:
                    off = -16 if r <= 1 else 16
                    if ref == "A1":
                        off = 0
                        d.text((x + (20 if pin[0] == "L" else -20), y), txt, fill=(0, 0, 120), font=fsm,
                               anchor="lm" if pin[0] == "L" else "rm")
                    else:
                        d.text((x, y + off), txt, fill=(0, 0, 120), font=fsm, anchor="mm")
    for r, items in leftlab.items():
        x, y = T(*xy(0, r))
        txt = "  ".join("%s [c%d]" % (n, c) for c, n in sorted(items))
        d.text((M - 36, y), txt, fill=(150, 0, 0), font=fsm, anchor="rm")
    # Legende
    yl = H - 28
    d.text((M, yl), ("Ansicht von der LOETSEITE (gespiegelt). Farbige Linien = blanker Draht / Loetbruecke."
                      if mirror else "Ansicht BAUTEILSEITE. Blasse Linien = Draehte auf der Loetseite. Kreise in den Ecken = auf 2,2 mm aufbohren."),
           fill=(0, 0, 0), font=font)
    img.save(os.path.join(HERE, fname))


def runs(segs):
    """Segmente zu geraden Strecken zusammenfassen."""
    adj = {}
    for a, b in segs:
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    used = set(); out = []
    for a, b in segs:
        if (a, b) in used or (b, a) in used:
            continue
        dirv = (b[0] - a[0], b[1] - a[1])
        s, e = a, b
        while True:
            n = (s[0] - dirv[0], s[1] - dirv[1])
            if n in adj.get(s, ()) and (n, s) not in used and (s, n) not in used:
                used.add((n, s)); s = n
            else:
                break
        while True:
            n = (e[0] + dirv[0], e[1] + dirv[1])
            if n in adj.get(e, ()) and (e, n) not in used and (n, e) not in used:
                used.add((e, n)); e = n
            else:
                break
        used.add((a, b))
        out.append((s, e))
    return out


def write_md(wires, jumpers):
    L = ["# Lochraster-Aufbau - Bauteile und Verdrahtung", "",
         "Raster: Spalte **c** von links (0..26), Zeile **r** von oben (0..18), jeweils auf der **Bauteilseite** gesehen.",
         "Auf der Loetseite ist links und rechts vertauscht (siehe `layout-loetseite.png`).", "",
         "## Bauteile", "", "| Teil | Wert | Beinchen (c,r) | Hinweis |", "| --- | --- | --- | --- |"]
    for ref, p in PARTS.items():
        if ref == "K":
            continue
        legs = ", ".join("%s=(%d,%d)" % (pin.lstrip("LR") if ref == "A1" else pin, c, r) for pin, (c, r, n) in p["leads"].items())
        L.append("| %s | %s | %s | %s |" % (ref, p["value"], legs, p.get("order", "")))
    L += ["", "## Kabel direkt einloeten", "", "| Kabel | Loch (c,r) | Signal |", "| --- | --- | --- |"]
    for name, (c, r, n) in PARTS["K"]["leads"].items():
        L.append("| %s | (%d,%d) | %s |" % (name, c, r, n))
    L += ["", "## Verbindungen auf der Loetseite (blanker Draht / Loetbruecke)", "",
          "Jede Zeile ist eine gerade Strecke von Loch zu Loch.", ""]
    for net in sorted(wires):
        rr = runs(wires[net])
        L.append("- **%s**: " % net + ", ".join("(%d,%d)-(%d,%d)" % (a[0], a[1], b[0], b[1]) for a, b in rr))
    if jumpers:
        L += ["", "## Isolierte Drahtbruecken", ""]
        for net, a, b in jumpers:
            L.append("- **%s**: (%d,%d) nach (%d,%d)" % (net, a[0], a[1], b[0], b[1]))
    open(os.path.join(HERE, "verdrahtung.md"), "w", encoding="utf-8").write(chr(10).join(L) + chr(10))


def main():
    errs = check_placement()
    for e in errs:
        print("PLATZ:", e)
    import random
    rnd = random.Random(7)
    wires, jumpers, pins_by_net, owner = route()
    nets = sorted(pins_by_net)
    best = (len(jumpers), sum(len(v) for v in wires.values()), None)
    for t in range(1500):
        o = nets[:]
        rnd.shuffle(o)
        w, j, _, _ = route(o)
        key = (len(j), sum(len(v) for v in w.values()))
        if key < best[:2]:
            best = key + (o,)
    if best[2]:
        wires, jumpers, pins_by_net, owner = route(best[2])
    verr = verify(wires, jumpers, pins_by_net)
    for e in verr:
        print("NETZ:", e)
    print("Netze:", len(pins_by_net), "Drahtsegmente:", sum(len(s) for s in wires.values()),
          "isolierte Bruecken:", len(jumpers), [(n, a, b) for n, a, b in jumpers])
    write_md(wires, jumpers)
    render(wires, jumpers, False, "layout-bauteilseite.png", "Vaillant 7-8-9 - Lochraster 70 x 50 mm (27 x 19 Loecher) - Bauteilseite")
    render(wires, jumpers, True, "layout-loetseite.png", "Vaillant 7-8-9 - Lochraster - Loetseite (gespiegelt)")
    return errs, verr, wires, jumpers, pins_by_net


if __name__ == "__main__":
    main()
