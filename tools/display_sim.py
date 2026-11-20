"""Simulation der E-Paper-Anzeige (Waveshare 2,9", 296 x 128, rotation 270).

Bildet den display-lambda aus vaillant-789.yaml 1:1 nach (gleiche Koordinaten,
Roboto-Schriften in gleichen Pixelgroessen, 1-Bit wie das E-Paper) und
rendert einige typische Zustaende nach druck/../display-sim.png.

    python tools/display_sim.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 296, 128
FONTS = r"C:\Windows\Fonts"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

f_big = ImageFont.truetype(os.path.join(FONTS, "Roboto-Bold.ttf"), 46)
f_mid = ImageFont.truetype(os.path.join(FONTS, "Roboto-Regular.ttf"), 20)
f_small = ImageFont.truetype(os.path.join(FONTS, "Roboto-Regular.ttf"), 14)

NAN = float("nan")


def isnan(v):
    return v != v


def render(ist, soll, mode_off, vl, demand, betriebsart, notbetrieb, online, pegel=NAN):
    img = Image.new("1", (W, H), 1)          # COLOR_OFF = weiss
    d = ImageDraw.Draw(img)
    boxes = []

    def text(x, y, font, s, align="la"):
        # ESPHome TOP_LEFT: y = Oberkante (Ascender) wie PIL-Anker "la"/"ra"
        d.text((x, y), s, font=font, fill=0, anchor=align)
        boxes.append((s, d.textbbox((x, y), s, font=font, anchor=align)))

    def line(x0, y0, x1, y1):
        d.line((x0, y0, x1, y1), fill=0)

    # --- links: Raumtemperatur gross, darunter Soll ---
    text(6, 4, f_big, "--.-°" if isnan(ist) else f"{ist:.1f}°")
    text(8, 66, f_mid, "Heizung aus" if mode_off else f"Soll {soll:.1f}°")

    # --- rechts: Vorlauf und Bedarf ---
    line(188, 6, 188, 98)
    text(198, 6, f_small, "Vorlauf")
    text(198, 24, f_mid, "--" if isnan(vl) else f"{vl:.0f}°C")
    if betriebsart >= 2:
        text(198, 56, f_small, "Pegel")
        text(198, 74, f_mid, "--" if isnan(pegel) else f"{pegel:.0f}%")
    else:
        text(198, 56, f_small, "Bedarf")
        text(198, 74, f_mid, f"{demand * 100:.0f}%")

    # --- unten: Statuszeile ---
    line(0, 104, 296, 104)
    m = betriebsart
    if notbetrieb:
        status = "NOTBETRIEB"
    elif m == 0:
        status = "Betrieb: Aus"
    elif m == 2:
        status = "Vorlauf manuell"
    elif m == 3:
        status = "Kalibrierung"
    elif not isnan(vl):
        status = "Heizt"
    else:
        status = "Bereit"
    text(6, 108, f_small, status)
    text(290, 108, f_small, "WLAN" if online else "offline", align="ra")

    # Pruefung: Text ausserhalb des Displays oder ueber den Trennlinien?
    warn = []
    for s, (x0, y0, x1, y1) in boxes:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            warn.append(f"'{s}' ragt aus dem Display ({x0},{y0},{x1},{y1})")
        if x0 < 188 < x1 and y0 < 98 and y1 > 6:
            warn.append(f"'{s}' beruehrt die senkrechte Linie (x={x1})")
        if y0 < 104 < y1:
            warn.append(f"'{s}' beruehrt die waagerechte Linie")
    return img, warn


SZENARIEN = [
    ("Raumregelung, heizt", dict(ist=20.4, soll=21.5, mode_off=False, vl=58,
                                 demand=0.62, betriebsart=1, notbetrieb=False, online=True)),
    ("Ziel erreicht (Bedarf <= 2 %)", dict(ist=21.5, soll=21.5, mode_off=False, vl=NAN,
                           demand=0.01, betriebsart=1, notbetrieb=False, online=True)),
    ("Heizung aus", dict(ist=22.8, soll=21.0, mode_off=True, vl=NAN,
                         demand=0.0, betriebsart=0, notbetrieb=False, online=True)),
    ("Sensor ausgefallen", dict(ist=NAN, soll=21.0, mode_off=False, vl=45,
                                demand=0.40, betriebsart=1, notbetrieb=True, online=False)),
    ("Vorlauf manuell", dict(ist=19.7, soll=21.0, mode_off=False, vl=82,
                             demand=1.0, betriebsart=2, notbetrieb=False, online=True, pegel=87)),
    ("Kalibrierung", dict(ist=-5.3, soll=30.0, mode_off=False, vl=NAN,
                          demand=0.55, betriebsart=3, notbetrieb=False, online=True, pegel=50)),
]


def panel(img, title, scale=3):
    """E-Paper-Optik: graues 'Papier', schwarze Pixel, Rahmen wie Modul."""
    big = img.convert("L").resize((W * scale, H * scale), Image.NEAREST)
    paper = Image.new("RGB", big.size, (226, 224, 216))
    ink = Image.new("RGB", big.size, (34, 34, 38))
    shown = Image.composite(paper, ink, big)
    m, top = 18, 44
    out = Image.new("RGB", (big.width + 2 * m, big.height + m + top), (245, 245, 242))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((m - 8, top - 8, m + big.width + 7, top + big.height + 7),
                        radius=6, fill=(40, 40, 44))
    out.paste(shown, (m, top))
    d.text((m, 8), title, font=ImageFont.truetype(os.path.join(FONTS, "Roboto-Bold.ttf"), 18),
           fill=(30, 30, 30))
    return out


def main():
    tiles, alle_warn = [], []
    for title, st in SZENARIEN:
        img, warn = render(**st)
        tiles.append(panel(img, title))
        alle_warn += [f"{title}: {w}" for w in warn]
    cols = 2
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (245, 245, 242))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
    out = os.path.join(ROOT, "display-sim.png")
    sheet.save(out)
    print("gespeichert:", out)
    for w in alle_warn:
        print("WARNUNG:", w)
    if not alle_warn:
        print("keine Ueberlappungen / Ueberstaende")


if __name__ == "__main__":
    main()
