# Platine zum Selbstlöten (THT) – nur die Leiterplatte von JLCPCB

70 × 50 mm, 2 Lagen, 1,6 mm, Massefläche auf beiden Seiten. Alle Bauteile sind
bedrahtet. Ausnahme sind C3 und C5: Das sind große SMD-Keramikkondensatoren
(Bauform 1210) mit Handlöt-Pads. Die Teile sind dieselben wie bei der
Lochraster-Variante (Reichelt).

**Geprüft:**
- **ERC:** 0 Fehler.
- **DRC:** 0 Verstöße, 0 offene Verbindungen, 0 Abweichungen zum Schaltplan (`kicad-cli`).

Auf der Oberseite ist das Hunde-Logo (`logo-hund.png`, ca. 12,5 mm) als Bestückungsdruck aufgedruckt.
Position und Größe stehen in `tools/gen_pcb.py` unter `LOGO`.

Die Montagelöcher (Ø 2,2 mm) liegen an denselben Stellen wie bei der
Lochrasterplatine. Die `.scad`-Datei passt also ohne Änderung.

## Bei JLCPCB bestellen

1. `fertigung/vaillant-789-gerber.zip` hochladen.
2. Einstellungen: 2 Layer, 1,6 mm, HASL (lead free), Farbe nach Wunsch,
   **PCB Assembly: aus**. Optional „Remove Order Number“ (meist gegen Aufpreis).
3. Mindestmenge sind 5 Stück, die Platine ist kleiner als 100 × 100 mm. Damit
   fällt sie in den günstigsten Tarif; der Großteil der Kosten ist der Versand.

## Teile

Die Einkaufsliste steht in [../lochraster/README.md](../lochraster/README.md#einkaufsliste).
Die Lochrasterplatine und den Silberdraht brauchst du dabei nicht. Die
Zuordnung der Bauteile zu den Positionen steht in `fertigung/Stueckliste.csv`.

## Bestücken

Erst die flachen Teile, dann die hohen:

1. C3 und C5 (SMD 1210, je zwei große Pads)
2. Widerstände, Dioden
3. IC-Fassung für U3, U1 (PC817)
4. Kerkos C4/C6, 78L09 (U2, flache Seite wie im Bestückungsdruck)
5. Buchsenleisten für den ESP
6. Elkos (auf „+“ achten)
7. TSR, Schraubklemme

**Achtung:**
- **R4:** Er steht aufrecht. Der Körper sitzt auf dem runden Pad.
- **D1:** Der Ring zeigt zum „K“.
- **D2:** Der Ring zeigt zum „K“ (links).
- **U1, U3:** Pin 1 hat das eckige Pad.

**Kabel:** Die Lötpunkte J2 (Display, oben), J3 (Sensor, unten links) und J4
(Drehgeber, unten Mitte) sind im Bestückungsdruck beschriftet. Du kannst die
Litzen direkt einlöten oder eine Stiftleiste setzen.

**Klemme 7-8-9:** Die Zahlen 7, 8 und 9 stehen links neben der Schraubklemme.
Die Kabel kommen von rechts.

## Neu erzeugen

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\gen_sch.py
```
```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\gen_pcb.py
```
```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" tools\export.py
```

Positionen und Bauteile stehen in `tools/design.py`. Achtung: `gen_pcb.py`
überschreibt die `.kicad_pcb`-Datei.
