# Platine Vaillant 7-8-9 Thermostat (KiCad 10)

70 × 50 mm, 2 Lagen, 1,6 mm, 4 × M2-Löcher im Raster 65 × 45 mm.
ERC und DRC (mit Schaltplan-Parität) laufen ohne Fehler und Warnungen durch.

## Bestellen bei JLCPCB

1. `fertigung/vaillant-789-gerber.zip` hochladen (2 Lagen, 1,6 mm, HASL, Farbe nach Wunsch).
2. „PCB Assembly“ → **Top Side** → `fertigung/BOM-JLCPCB.csv` und `fertigung/CPL-JLCPCB.csv`.
3. **In der Bestückungsvorschau jedes Teil auf Lage und Polarität prüfen.** Die
   Drehwinkel stammen direkt aus KiCad. Bei JLC kommt es öfter vor, dass sie
   bei einzelnen Gehäusen um 90° oder 180° versetzt erscheinen. Dann im Viewer
   drehen. Besonders prüfen:
   - U3 LM358 – Punkt = Pin 1 oben links
   - U1 EL817 – Pin 1 oben links
   - U2 78M09 – Kühlfahne rechts
   - C1, C7, C8 – Elkos, „+“-Markierung
   - D1, D2 – Kathodenstrich

## Abweichungen von der Schaltung in CLAUDE.md (gleiche Funktion)

| Teil | Vorgabe | Platine | Grund |
| --- | --- | --- | --- |
| U2 | 78L09 | **CJ78M09 (DPAK, C9071)** | Einen 78L09 im SMD-Gehäuse hat JLCPCB praktisch nicht auf Lager. Pinbelegung und Funktion sind gleich, die Ruhestromaufnahme ist etwas höher (ca. 4,6 mA statt ca. 3 mA). |
| C3 | 330 nF | **1 µF/50 V (0805)** | Basic-Teil mit ausreichender Spannungsfestigkeit, mehr Kapazität schadet nicht |
| R7 | 100 Ω 0,5 W | **100 Ω 2 W (2512)** | Mehr Reserve; es gibt bei JLC keinen 0,5-W-Typ, der auf Lager ist |
| C8 | 1000 µF/10 V | **1000 µF/16 V SMD (10 × 10 mm)** | auf Lager, 10,2 mm hoch |
| U1 | PC817 | **EL817S1(C)** | gleicher Typ mit gleicher Pinbelegung; ein PC817 als Basic-Teil ist nicht auf Lager |

## Selbst einlöten (THT)

Siehe `fertigung/Teile-selbst-loeten-v2.csv` und `../Einkaufsliste.md`:

- 2 × Buchsenleiste 1×8 (RM 2,54) für den ESP32-C3 SuperMini, USB nach unten, Antenne zur Platinenoberkante.
- TRACO TSR 0.5-2450
- Schraubklemme RM 5,08: oben Klemme 7, Mitte 8, unten 9; die Kabel kommen von rechts.
- Gewinkelte Stiftleisten RM 2,54 (von einer 1×40-Leiste abbrechen). Pin 1 ist jeweils rechts.
  - **J2 Display (9 Pins):** VCC, GND, DIN, CLK, CS, DC, RST, BUSY, PWR. Das beiliegende Waveshare-Kabel wird direkt aufgesteckt. PWR (nur bei neueren Modulen) liegt auf 3,3 V.
  - **J3 Sensor (4 Pins, unten links):** V = 3,3 V, G = GND, D = SDA, C = SCL.
  - **J4 Drehgeber (5 Pins, unten Mitte):** A, G, B, S (Taster), G.

  J3 und J4 zeigen über die Unterkante hinaus. Die Dupont-Stecker sitzen dann
  neben der Sensorkammer, links davon.

**Vor dem Bestellen nachmessen:** Der Footprint geht beim SuperMini von einem
Reihenabstand von 15,24 mm aus, mit dieser Belegung von unten (USB) nach oben:
links 5V-GND-3V3-4-3-2-1-0, rechts 5-6-7-8-9-10-20-21. Wenn dein Modul
anders aussieht, `ESP_LEFT`/`ESP_RIGHT` und den Abstand in `tools/gen_sch.py`
anpassen und neu erzeugen.

Verbindung zu Sensor und Drehgeber: Jumper-Kabel Buchse–Buchse verwenden. Am
Drehgeber die eine Buchse abschneiden und die Litze direkt anlöten.

## Neu erzeugen

Alles wird per Skript aus `tools/design.py` erzeugt: Netzliste, Bauteile,
Positionen und LCSC-Nummern. Der Router ist ein eigener A*-Router auf einem
0,1-mm-Raster; Freerouting ist nicht nötig.

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\gen_sch.py
```
```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\gen_pcb.py
```
```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --severity-all --schematic-parity vaillant-789.kicad_pcb
```
```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\export.py
```

Achtung: `gen_pcb.py` überschreibt die `.kicad_pcb`-Datei. Wer in KiCad von
Hand nachbessert, sollte das Skript danach nicht mehr laufen lassen.
